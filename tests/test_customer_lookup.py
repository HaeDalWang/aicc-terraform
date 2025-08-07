import unittest
import json
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
import sys
import os

# Lambda 함수 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from customer_lookup import lambda_handler, lookup_customer, classify_customer, get_assigned_engineer


class TestCustomerLookup(unittest.TestCase):
    """고객 조회 Lambda 함수 테스트"""
    
    @mock_aws
    def setUp(self):
        """테스트 설정"""
        # DynamoDB 테이블 생성
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
        
        # 고객 테이블 생성
        self.customers_table = self.dynamodb.create_table(
            TableName='dev-saltware-customers',
            KeySchema=[
                {'AttributeName': 'customer_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'customer_id', 'AttributeType': 'S'},
                {'AttributeName': 'company_name', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'company_name-index',
                    'KeySchema': [
                        {'AttributeName': 'company_name', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # 엔지니어 테이블 생성
        self.engineers_table = self.dynamodb.create_table(
            TableName='dev-saltware-engineers',
            KeySchema=[
                {'AttributeName': 'engineer_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'engineer_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # 테이블 준비 대기
        self.customers_table.wait_until_exists()
        self.engineers_table.wait_until_exists()
        
        # 테스트 데이터 삽입
        self._insert_test_data()
    
    def _insert_test_data(self):
        """테스트 데이터 삽입"""
        # MSP 고객 데이터
        response = self.customers_table.put_item(Item={
            'customer_id': 'cust_001',
            'company_name': 'ABC Corporation',
            'aws_account_id': '123456781234',
            'support_level': 'MSP',
            'assigned_engineer': 'eng_001'
        })
        print(f"MSP 고객 데이터 삽입 응답: {response}")
        
        # 일반 고객 데이터
        response = self.customers_table.put_item(Item={
            'customer_id': 'cust_002',
            'company_name': 'XYZ Company',
            'aws_account_id': '987654329876',
            'support_level': 'General',
            'assigned_engineer': 'eng_002'
        })
        print(f"일반 고객 데이터 삽입 응답: {response}")
        
        # 데이터 삽입 확인
        scan_response = self.customers_table.scan()
        print(f"삽입 후 테이블 데이터: {scan_response.get('Items', [])}")
        
        # 엔지니어 데이터
        self.engineers_table.put_item(Item={
            'engineer_id': 'eng_001',
            'name': '김철수',
            'part': 'Leaf',
            'phone': '010-1234-5678',
            'is_available': True
        })
        
        self.engineers_table.put_item(Item={
            'engineer_id': 'eng_002',
            'name': '이영희',
            'part': 'Tiger',
            'phone': '010-9876-5432',
            'is_available': True
        })
    
    def test_valid_msp_customer_lookup(self):
        """유효한 MSP 고객 조회 테스트"""
        # 직접 lookup_customer 함수 테스트
        import customer_lookup
        
        # 원래 dynamodb를 백업하고 테스트용으로 교체
        original_dynamodb = customer_lookup.dynamodb
        customer_lookup.dynamodb = self.dynamodb
        
        try:
            # 환경 변수 설정
            import os
            os.environ['CUSTOMERS_TABLE'] = 'dev-saltware-customers'
            
            # 고객 조회 테스트
            result = lookup_customer('ABC Corporation', '1234')
            
            self.assertIsNotNone(result)
            self.assertEqual(result['company_name'], 'ABC Corporation')
            self.assertEqual(result['support_level'], 'MSP')
            self.assertEqual(result['customer_id'], 'cust_001')
            
        finally:
            # 원래 dynamodb 복원
            customer_lookup.dynamodb = original_dynamodb
    
    def test_valid_general_customer_lookup(self):
        """유효한 일반 고객 조회 테스트"""
        event = {
            'company_name': 'XYZ Company',
            'aws_account_id': '9876'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['customer_found'])
        self.assertEqual(body['customer_type'], 'General')
        self.assertEqual(body['customer_info']['company_name'], 'XYZ Company')
    
    def test_customer_not_found(self):
        """고객을 찾을 수 없는 경우 테스트"""
        event = {
            'company_name': 'Unknown Company',
            'aws_account_id': '0000'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['customer_found'])
        self.assertEqual(body['customer_type'], 'Unknown')
        self.assertIsNone(body['customer_info'])
    
    def test_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        # 회사명 누락
        event = {'aws_account_id': '1234'}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        
        # AWS Account ID 누락
        event = {'company_name': 'ABC Corporation'}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
    
    def test_invalid_aws_account_id_format(self):
        """잘못된 AWS Account ID 형식 테스트"""
        # 4자리가 아닌 경우
        event = {
            'company_name': 'ABC Corporation',
            'aws_account_id': '12345'
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        
        # 숫자가 아닌 경우
        event = {
            'company_name': 'ABC Corporation',
            'aws_account_id': 'abcd'
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
    
    def test_classify_customer(self):
        """고객 분류 함수 테스트"""
        # MSP 고객
        msp_customer = {'support_level': 'MSP'}
        self.assertEqual(classify_customer(msp_customer), 'MSP')
        
        # 일반 고객
        general_customer = {'support_level': 'General'}
        self.assertEqual(classify_customer(general_customer), 'General')
        
        # 알 수 없는 레벨 (기본값: General)
        unknown_customer = {'support_level': 'Unknown'}
        self.assertEqual(classify_customer(unknown_customer), 'General')
    
    def test_get_assigned_engineer(self):
        """담당 엔지니어 조회 테스트"""
        customer_info = {'assigned_engineer': 'eng_001'}
        
        engineer_info = get_assigned_engineer(customer_info)
        
        self.assertIsNotNone(engineer_info)
        self.assertEqual(engineer_info['engineer_id'], 'eng_001')
        self.assertEqual(engineer_info['name'], '김철수')
        self.assertEqual(engineer_info['part'], 'Leaf')
    
    def test_get_assigned_engineer_not_found(self):
        """담당 엔지니어를 찾을 수 없는 경우 테스트"""
        customer_info = {'assigned_engineer': 'eng_999'}
        
        engineer_info = get_assigned_engineer(customer_info)
        
        self.assertIsNone(engineer_info)
    
    def test_get_assigned_engineer_no_assignment(self):
        """담당 엔지니어가 배정되지 않은 경우 테스트"""
        customer_info = {}
        
        engineer_info = get_assigned_engineer(customer_info)
        
        self.assertIsNone(engineer_info)


if __name__ == '__main__':
    unittest.main()