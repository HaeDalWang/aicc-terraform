import json
import boto3
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
import hashlib

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 서비스 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    통화 로깅 Lambda 함수
    
    Args:
        event: {
            "action": "start" | "end" | "update",
            "call_id": "통화 ID (선택사항, 자동 생성)",
            "phone_number": "발신자 번호",
            "customer_info": {
                "customer_id": "고객 ID",
                "company_name": "고객사명",
                "support_level": "MSP" | "General"
            },
            "flow_path": ["Main Entry", "Customer Auth", "MSP Flow"],
            "resolution": "처리 결과",
            "assigned_to": "담당자 ID",
            "call_duration": 120,  # 통화 시간 (초)
            "notes": "추가 메모"
        }
    
    Returns:
        {
            "statusCode": 200,
            "body": {
                "success": true,
                "call_id": "생성된 통화 ID",
                "message": "처리 결과 메시지"
            }
        }
    """
    
    try:
        # 입력 파라미터 검증
        action = event.get('action', '').lower()
        if action not in ['start', 'end', 'update']:
            return create_error_response(400, "action은 'start', 'end', 'update' 중 하나여야 합니다.")
        
        phone_number = event.get('phone_number', '').strip()
        if not phone_number:
            return create_error_response(400, "발신자 번호는 필수 입력 항목입니다.")
        
        # 개인정보 보호 처리된 전화번호
        masked_phone = mask_phone_number(phone_number)
        
        logger.info(f"통화 로깅 요청 - 액션: {action}, 전화번호: {masked_phone}")
        
        # 액션별 처리
        if action == 'start':
            result = handle_call_start(event, masked_phone)
        elif action == 'end':
            result = handle_call_end(event, masked_phone)
        elif action == 'update':
            result = handle_call_update(event, masked_phone)
        
        # CloudWatch 메트릭 전송
        send_cloudwatch_metrics(action, event)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"통화 로깅 중 오류 발생: {str(e)}")
        return create_error_response(500, "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")


def handle_call_start(event: Dict[str, Any], masked_phone: str) -> Dict[str, Any]:
    """
    통화 시작 로깅 처리
    
    Args:
        event: 이벤트 데이터
        masked_phone: 마스킹된 전화번호
    
    Returns:
        처리 결과
    """
    try:
        # 통화 ID 생성 또는 사용
        call_id = event.get('call_id') or generate_call_id()
        
        # 통화 로그 데이터 생성
        call_log = {
            'call_id': call_id,
            'phone_number_hash': hash_phone_number(event.get('phone_number')),
            'masked_phone_number': masked_phone,
            'call_start_time': datetime.now(timezone.utc).isoformat(),
            'call_status': 'in_progress',
            'flow_path': event.get('flow_path', []),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # 고객 정보 추가 (있는 경우)
        customer_info = event.get('customer_info')
        if customer_info:
            call_log.update({
                'customer_id': customer_info.get('customer_id'),
                'company_name': customer_info.get('company_name'),
                'support_level': customer_info.get('support_level')
            })
        
        # DynamoDB에 저장
        save_call_log(call_log)
        
        logger.info(f"통화 시작 로깅 완료 - Call ID: {call_id}")
        
        return {
            "success": True,
            "call_id": call_id,
            "message": "통화 시작이 기록되었습니다."
        }
        
    except Exception as e:
        logger.error(f"통화 시작 로깅 중 오류: {str(e)}")
        raise


def handle_call_end(event: Dict[str, Any], masked_phone: str) -> Dict[str, Any]:
    """
    통화 종료 로깅 처리
    
    Args:
        event: 이벤트 데이터
        masked_phone: 마스킹된 전화번호
    
    Returns:
        처리 결과
    """
    try:
        call_id = event.get('call_id')
        if not call_id:
            return {"success": False, "message": "통화 ID가 필요합니다."}
        
        # 기존 통화 로그 조회
        existing_log = get_call_log(call_id)
        if not existing_log:
            return {"success": False, "message": "해당 통화 로그를 찾을 수 없습니다."}
        
        # 통화 종료 정보 업데이트
        update_data = {
            'call_end_time': datetime.now(timezone.utc).isoformat(),
            'call_status': 'completed',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # 추가 정보 업데이트
        if event.get('resolution'):
            update_data['resolution'] = event.get('resolution')
        
        if event.get('assigned_to'):
            update_data['assigned_to'] = event.get('assigned_to')
        
        if event.get('call_duration'):
            update_data['call_duration'] = event.get('call_duration')
        
        if event.get('notes'):
            update_data['notes'] = event.get('notes')
        
        if event.get('flow_path'):
            # 기존 flow_path와 병합
            existing_flow = existing_log.get('flow_path', [])
            new_flow = event.get('flow_path', [])
            update_data['flow_path'] = list(set(existing_flow + new_flow))
        
        # DynamoDB 업데이트
        update_call_log(call_id, update_data)
        
        logger.info(f"통화 종료 로깅 완료 - Call ID: {call_id}")
        
        return {
            "success": True,
            "call_id": call_id,
            "message": "통화 종료가 기록되었습니다."
        }
        
    except Exception as e:
        logger.error(f"통화 종료 로깅 중 오류: {str(e)}")
        raise


def handle_call_update(event: Dict[str, Any], masked_phone: str) -> Dict[str, Any]:
    """
    통화 정보 업데이트 처리
    
    Args:
        event: 이벤트 데이터
        masked_phone: 마스킹된 전화번호
    
    Returns:
        처리 결과
    """
    try:
        call_id = event.get('call_id')
        if not call_id:
            return {"success": False, "message": "통화 ID가 필요합니다."}
        
        # 기존 통화 로그 확인
        existing_log = get_call_log(call_id)
        if not existing_log:
            return {"success": False, "message": "해당 통화 로그를 찾을 수 없습니다."}
        
        # 업데이트할 데이터 준비
        update_data = {
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # 선택적 필드 업데이트
        optional_fields = ['resolution', 'assigned_to', 'notes']
        for field in optional_fields:
            if event.get(field):
                update_data[field] = event.get(field)
        
        # flow_path 업데이트 (기존 경로에 추가)
        if event.get('flow_path'):
            existing_flow = existing_log.get('flow_path', [])
            new_flow = event.get('flow_path', [])
            update_data['flow_path'] = existing_flow + [path for path in new_flow if path not in existing_flow]
        
        # 고객 정보 업데이트
        customer_info = event.get('customer_info')
        if customer_info:
            if customer_info.get('customer_id'):
                update_data['customer_id'] = customer_info.get('customer_id')
            if customer_info.get('company_name'):
                update_data['company_name'] = customer_info.get('company_name')
            if customer_info.get('support_level'):
                update_data['support_level'] = customer_info.get('support_level')
        
        # DynamoDB 업데이트
        update_call_log(call_id, update_data)
        
        logger.info(f"통화 정보 업데이트 완료 - Call ID: {call_id}")
        
        return {
            "success": True,
            "call_id": call_id,
            "message": "통화 정보가 업데이트되었습니다."
        }
        
    except Exception as e:
        logger.error(f"통화 정보 업데이트 중 오류: {str(e)}")
        raise


def generate_call_id() -> str:
    """
    고유한 통화 ID 생성
    
    Returns:
        통화 ID
    """
    # UUID4 + 타임스탬프 조합으로 고유성 보장
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"call_{timestamp}_{unique_id}"


def mask_phone_number(phone_number: str) -> str:
    """
    전화번호 마스킹 처리 (개인정보 보호)
    
    Args:
        phone_number: 원본 전화번호
    
    Returns:
        마스킹된 전화번호
    """
    if len(phone_number) <= 4:
        return "*" * len(phone_number)
    
    # 앞 3자리와 뒤 4자리만 표시, 나머지는 마스킹
    if len(phone_number) > 7:
        return phone_number[:3] + "*" * (len(phone_number) - 7) + phone_number[-4:]
    else:
        return phone_number[:2] + "*" * (len(phone_number) - 4) + phone_number[-2:]


def hash_phone_number(phone_number: str) -> str:
    """
    전화번호 해시 처리 (검색용)
    
    Args:
        phone_number: 원본 전화번호
    
    Returns:
        해시된 전화번호
    """
    return hashlib.sha256(phone_number.encode()).hexdigest()


def save_call_log(call_log: Dict[str, Any]) -> None:
    """
    통화 로그를 DynamoDB에 저장
    
    Args:
        call_log: 통화 로그 데이터
    """
    try:
        import os
        table_name = os.environ.get('CALL_LOGS_TABLE', 'dev-saltware-call-logs')
        table = dynamodb.Table(table_name)
        
        # TTL 설정 (90일 후 자동 삭제)
        from datetime import timedelta
        ttl_date = datetime.now(timezone.utc) + timedelta(days=90)
        call_log['ttl'] = int(ttl_date.timestamp())
        
        table.put_item(Item=call_log)
        
    except ClientError as e:
        logger.error(f"DynamoDB 저장 오류: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"통화 로그 저장 중 예상치 못한 오류: {str(e)}")
        raise


def get_call_log(call_id: str) -> Optional[Dict[str, Any]]:
    """
    통화 로그 조회
    
    Args:
        call_id: 통화 ID
    
    Returns:
        통화 로그 데이터 또는 None
    """
    try:
        import os
        table_name = os.environ.get('CALL_LOGS_TABLE', 'dev-saltware-call-logs')
        table = dynamodb.Table(table_name)
        
        response = table.get_item(Key={'call_id': call_id})
        return response.get('Item')
        
    except ClientError as e:
        logger.error(f"DynamoDB 조회 오류: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        logger.error(f"통화 로그 조회 중 예상치 못한 오류: {str(e)}")
        return None


def update_call_log(call_id: str, update_data: Dict[str, Any]) -> None:
    """
    통화 로그 업데이트
    
    Args:
        call_id: 통화 ID
        update_data: 업데이트할 데이터
    """
    try:
        import os
        table_name = os.environ.get('CALL_LOGS_TABLE', 'dev-saltware-call-logs')
        table = dynamodb.Table(table_name)
        
        # UpdateExpression 생성
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        for key, value in update_data.items():
            # 예약어 처리
            attr_name = f"#{key}"
            attr_value = f":{key}"
            
            update_expression += f"{attr_name} = {attr_value}, "
            expression_attribute_names[attr_name] = key
            expression_attribute_values[attr_value] = value
        
        # 마지막 쉼표 제거
        update_expression = update_expression.rstrip(', ')
        
        table.update_item(
            Key={'call_id': call_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        
    except ClientError as e:
        logger.error(f"DynamoDB 업데이트 오류: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"통화 로그 업데이트 중 예상치 못한 오류: {str(e)}")
        raise


def send_cloudwatch_metrics(action: str, event: Dict[str, Any]) -> None:
    """
    CloudWatch 메트릭 전송
    
    Args:
        action: 액션 타입
        event: 이벤트 데이터
    """
    try:
        # 기본 메트릭
        metrics = [
            {
                'MetricName': 'CallCount',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Action', 'Value': action}
                ]
            }
        ]
        
        # 고객 타입별 메트릭
        customer_info = event.get('customer_info')
        if customer_info and customer_info.get('support_level'):
            metrics.append({
                'MetricName': 'CallCountByCustomerType',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'CustomerType', 'Value': customer_info.get('support_level')},
                    {'Name': 'Action', 'Value': action}
                ]
            })
        
        # 통화 시간 메트릭 (종료 시에만)
        if action == 'end' and event.get('call_duration'):
            metrics.append({
                'MetricName': 'CallDuration',
                'Value': event.get('call_duration'),
                'Unit': 'Seconds',
                'Dimensions': [
                    {'Name': 'CustomerType', 'Value': customer_info.get('support_level', 'Unknown')}
                ]
            })
        
        # CloudWatch에 메트릭 전송
        cloudwatch.put_metric_data(
            Namespace='Saltware/IVR',
            MetricData=metrics
        )
        
        logger.info(f"CloudWatch 메트릭 전송 완료 - Action: {action}")
        
    except Exception as e:
        # 메트릭 전송 실패는 전체 처리를 중단시키지 않음
        logger.warning(f"CloudWatch 메트릭 전송 실패: {str(e)}")


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    오류 응답 생성
    
    Args:
        status_code: HTTP 상태 코드
        message: 오류 메시지
    
    Returns:
        오류 응답 딕셔너리
    """
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "success": False,
            "call_id": None,
            "message": message,
            "error": True
        }, ensure_ascii=False)
    }