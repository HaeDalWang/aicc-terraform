import unittest
import json
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime, timezone

# Lambda 함수 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from call_logging import (
    lambda_handler,
    handle_call_start,
    handle_call_end,
    handle_call_update,
    generate_call_id,
    mask_phone_number,
    hash_phone_number,
    save_call_log,
    get_call_log,
    update_call_log,
    send_cloudwatch_metrics
)


class TestCallLogging(unittest.TestCase):
    """통화 로깅 Lambda 함수 테스트"""
    
    @mock_aws
    def setUp(self):
        """테스트 설정"""
        # DynamoDB 테이블 생성
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
        
        self.call_logs_table = self.dynamodb.create_table(
            TableName='dev-saltware-call-logs',
            KeySchema=[
                {'AttributeName': 'call_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'call_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # CloudWatch 클라이언트 생성
        self.cloudwatch = boto3.client('cloudwatch', region_name='ap-northeast-2')
        
        # 테이블 준비 대기
        self.call_logs_table.wait_until_exists()
    
    def test_call_start_logging(self):
        """통화 시작 로깅 테스트"""
        event = {
            'action': 'start',
            'phone_number': '010-1234-5678',
            'customer_info': {
                'customer_id': 'cust_001',
                'company_name': 'ABC Corporation',
                'support_level': 'MSP'
            },
            'flow_path': ['Main Entry']
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertIsNotNone(body['call_id'])
        self.assertEqual(body['message'], '통화 시작이 기록되었습니다.')
        
        # DynamoDB에 저장되었는지 확인
        call_log = get_call_log(body['call_id'])
        self.assertIsNotNone(call_log)
        self.assertEqual(call_log['call_status'], 'in_progress')
        self.assertEqual(call_log['customer_id'], 'cust_001')
    
    def test_call_end_logging(self):
        """통화 종료 로깅 테스트"""
        # 먼저 통화 시작 로깅
        start_event = {
            'action': 'start',
            'phone_number': '010-1234-5678',
            'customer_info': {
                'customer_id': 'cust_001',
                'company_name': 'ABC Corporation',
                'support_level': 'MSP'
            }
        }
        
        start_response = lambda_handler(start_event, None)
        start_body = json.loads(start_response['body'])
        call_id = start_body['call_id']
        
        # 통화 종료 로깅
        end_event = {
            'action': 'end',
            'call_id': call_id,
            'phone_number': '010-1234-5678',
            'resolution': '문제 해결 완료',
            'assigned_to': 'eng_001',
            'call_duration': 300,
            'notes': '고객 만족'
        }
        
        response = lambda_handler(end_event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['call_id'], call_id)
        self.assertEqual(body['message'], '통화 종료가 기록되었습니다.')
        
        # DynamoDB에서 업데이트 확인
        call_log = get_call_log(call_id)
        self.assertEqual(call_log['call_status'], 'completed')
        self.assertEqual(call_log['resolution'], '문제 해결 완료')
        self.assertEqual(call_log['assigned_to'], 'eng_001')
        self.assertEqual(call_log['call_duration'], 300)
    
    def test_call_update_logging(self):
        """통화 정보 업데이트 테스트"""
        # 먼저 통화 시작 로깅
        start_event = {
            'action': 'start',
            'phone_number': '010-1234-5678'
        }
        
        start_response = lambda_handler(start_event, None)
        start_body = json.loads(start_response['body'])
        call_id = start_body['call_id']
        
        # 통화 정보 업데이트
        update_event = {
            'action': 'update',
            'call_id': call_id,
            'phone_number': '010-1234-5678',
            'customer_info': {
                'customer_id': 'cust_002',
                'company_name': 'XYZ Company',
                'support_level': 'General'
            },
            'flow_path': ['Customer Auth', 'General Flow'],
            'assigned_to': 'eng_002'
        }
        
        response = lambda_handler(update_event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['message'], '통화 정보가 업데이트되었습니다.')
        
        # DynamoDB에서 업데이트 확인
        call_log = get_call_log(call_id)
        self.assertEqual(call_log['customer_id'], 'cust_002')
        self.assertEqual(call_log['company_name'], 'XYZ Company')
        self.assertEqual(call_log['assigned_to'], 'eng_002')
        self.assertIn('Customer Auth', call_log['flow_path'])
        self.assertIn('General Flow', call_log['flow_path'])
    
    def test_invalid_action(self):
        """잘못된 액션 테스트"""
        event = {
            'action': 'invalid_action',
            'phone_number': '010-1234-5678'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertTrue(body['error'])
    
    def test_missing_phone_number(self):
        """전화번호 누락 테스트"""
        event = {
            'action': 'start'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertTrue(body['error'])
    
    def test_call_end_without_call_id(self):
        """통화 ID 없이 종료 시도 테스트"""
        event = {
            'action': 'end',
            'phone_number': '010-1234-5678'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertEqual(body['message'], '통화 ID가 필요합니다.')
    
    def test_call_end_with_nonexistent_call_id(self):
        """존재하지 않는 통화 ID로 종료 시도 테스트"""
        event = {
            'action': 'end',
            'call_id': 'nonexistent_call_id',
            'phone_number': '010-1234-5678'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertEqual(body['message'], '해당 통화 로그를 찾을 수 없습니다.')
    
    def test_generate_call_id(self):
        """통화 ID 생성 테스트"""
        call_id1 = generate_call_id()
        call_id2 = generate_call_id()
        
        # 고유성 확인
        self.assertNotEqual(call_id1, call_id2)
        
        # 형식 확인
        self.assertTrue(call_id1.startswith('call_'))
        self.assertTrue(call_id2.startswith('call_'))
    
    def test_mask_phone_number(self):
        """전화번호 마스킹 테스트"""
        # 일반적인 휴대폰 번호
        phone1 = '010-1234-5678'
        masked1 = mask_phone_number(phone1)
        self.assertEqual(masked1, '010****5678')
        
        # 짧은 번호
        phone2 = '1234'
        masked2 = mask_phone_number(phone2)
        self.assertEqual(masked2, '****')
        
        # 긴 번호
        phone3 = '02-1234-5678'
        masked3 = mask_phone_number(phone3)
        self.assertEqual(masked3, '02-***5678')
    
    def test_hash_phone_number(self):
        """전화번호 해시 테스트"""
        phone = '010-1234-5678'
        hash1 = hash_phone_number(phone)
        hash2 = hash_phone_number(phone)
        
        # 동일한 입력에 대해 동일한 해시
        self.assertEqual(hash1, hash2)
        
        # 해시 길이 확인 (SHA256)
        self.assertEqual(len(hash1), 64)
        
        # 다른 번호는 다른 해시
        different_phone = '010-9876-5432'
        different_hash = hash_phone_number(different_phone)
        self.assertNotEqual(hash1, different_hash)
    
    def test_save_and_get_call_log(self):
        """통화 로그 저장 및 조회 테스트"""
        call_log_data = {
            'call_id': 'test_call_001',
            'phone_number_hash': 'test_hash',
            'masked_phone_number': '010****5678',
            'call_start_time': datetime.now(timezone.utc).isoformat(),
            'call_status': 'in_progress'
        }
        
        # 저장
        save_call_log(call_log_data)
        
        # 조회
        retrieved_log = get_call_log('test_call_001')
        
        self.assertIsNotNone(retrieved_log)
        self.assertEqual(retrieved_log['call_id'], 'test_call_001')
        self.assertEqual(retrieved_log['call_status'], 'in_progress')
    
    def test_update_call_log_function(self):
        """통화 로그 업데이트 함수 테스트"""
        # 먼저 로그 저장
        call_log_data = {
            'call_id': 'test_call_002',
            'phone_number_hash': 'test_hash',
            'call_status': 'in_progress'
        }
        save_call_log(call_log_data)
        
        # 업데이트
        update_data = {
            'call_status': 'completed',
            'resolution': '문제 해결',
            'call_duration': 180
        }
        update_call_log('test_call_002', update_data)
        
        # 확인
        updated_log = get_call_log('test_call_002')
        self.assertEqual(updated_log['call_status'], 'completed')
        self.assertEqual(updated_log['resolution'], '문제 해결')
        self.assertEqual(updated_log['call_duration'], 180)
    
    @patch('call_logging.cloudwatch')
    def test_send_cloudwatch_metrics(self, mock_cloudwatch):
        """CloudWatch 메트릭 전송 테스트"""
        event = {
            'customer_info': {
                'support_level': 'MSP'
            },
            'call_duration': 300
        }
        
        send_cloudwatch_metrics('end', event)
        
        # CloudWatch put_metric_data 호출 확인
        mock_cloudwatch.put_metric_data.assert_called_once()
        
        # 호출 인자 확인
        call_args = mock_cloudwatch.put_metric_data.call_args
        self.assertEqual(call_args[1]['Namespace'], 'Saltware/IVR')
        
        metrics = call_args[1]['MetricData']
        self.assertGreater(len(metrics), 0)
        
        # 기본 CallCount 메트릭 확인
        call_count_metric = next((m for m in metrics if m['MetricName'] == 'CallCount'), None)
        self.assertIsNotNone(call_count_metric)
        self.assertEqual(call_count_metric['Value'], 1)


if __name__ == '__main__':
    unittest.main()