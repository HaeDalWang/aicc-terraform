import json
import boto3
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    고객 조회 Lambda 함수
    
    Args:
        event: {
            "company_name": "고객사명",
            "aws_account_id": "AWS Account ID 마지막 4자리",
            "contact_name": "담당자명 (선택사항)"
        }
    
    Returns:
        {
            "statusCode": 200,
            "body": {
                "customer_found": true/false,
                "customer_type": "MSP" | "General" | "Unknown",
                "customer_info": {
                    "customer_id": "string",
                    "company_name": "string",
                    "support_level": "string",
                    "assigned_engineer": "string"
                },
                "message": "처리 결과 메시지"
            }
        }
    """
    
    try:
        # 입력 파라미터 검증
        company_name = event.get('company_name', '').strip()
        aws_account_id = event.get('aws_account_id', '').strip()
        contact_name = event.get('contact_name', '').strip()
        
        logger.info(f"고객 조회 요청 - 회사명: {company_name}, AWS Account ID: {aws_account_id}")
        
        if not company_name or not aws_account_id:
            return create_error_response(400, "회사명과 AWS Account ID는 필수 입력 항목입니다.")
        
        # AWS Account ID 형식 검증 (4자리 숫자)
        if not aws_account_id.isdigit() or len(aws_account_id) != 4:
            return create_error_response(400, "AWS Account ID는 4자리 숫자여야 합니다.")
        
        # 고객 정보 조회
        customer_info = lookup_customer(company_name, aws_account_id)
        
        if customer_info:
            # 고객 분류 및 담당 엔지니어 정보 조회
            customer_type = classify_customer(customer_info)
            assigned_engineer = get_assigned_engineer(customer_info)
            
            response_body = {
                "customer_found": True,
                "customer_type": customer_type,
                "customer_info": {
                    "customer_id": customer_info.get('customer_id'),
                    "company_name": customer_info.get('company_name'),
                    "support_level": customer_info.get('support_level'),
                    "assigned_engineer": assigned_engineer
                },
                "message": f"{customer_type} 고객으로 확인되었습니다."
            }
            
            logger.info(f"고객 조회 성공 - {customer_type} 고객: {company_name}")
            
        else:
            # 미등록 고객 처리
            response_body = {
                "customer_found": False,
                "customer_type": "Unknown",
                "customer_info": None,
                "message": "등록되지 않은 고객입니다. 신규 고객 처리 절차를 진행합니다."
            }
            
            logger.warning(f"미등록 고객 - 회사명: {company_name}, AWS Account ID: {aws_account_id}")
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_body, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"고객 조회 중 오류 발생: {str(e)}")
        return create_error_response(500, "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")


def lookup_customer(company_name: str, aws_account_id: str) -> Optional[Dict[str, Any]]:
    """
    DynamoDB에서 고객 정보 조회
    
    Args:
        company_name: 고객사명
        aws_account_id: AWS Account ID 마지막 4자리
    
    Returns:
        고객 정보 딕셔너리 또는 None
    """
    try:
        # 환경 변수에서 테이블명 가져오기 (기본값 설정)
        import os
        table_name = os.environ.get('CUSTOMERS_TABLE', 'dev-saltware-customers')
        table = dynamodb.Table(table_name)
        
        # GSI가 없는 경우를 대비해 scan 사용 (테스트 환경)
        try:
            # 회사명으로 먼저 조회 (GSI 사용)
            response = table.query(
                IndexName='company_name-index',
                KeyConditionExpression=Key('company_name').eq(company_name)
            )
            customers = response.get('Items', [])
        except ClientError as e:
            if 'ValidationException' in str(e) and 'index' in str(e):
                # GSI가 없는 경우 scan 사용 (테스트 환경)
                logger.warning("GSI를 찾을 수 없어 scan을 사용합니다.")
                response = table.scan(
                    FilterExpression=Attr('company_name').eq(company_name)
                )
                customers = response.get('Items', [])
                logger.info(f"Scan 결과: {len(customers)}개 고객 발견")
            else:
                raise
        
        # AWS Account ID로 필터링
        logger.info(f"필터링할 고객 수: {len(customers)}")
        for customer in customers:
            stored_account_id = customer.get('aws_account_id', '')
            logger.info(f"고객 확인: {customer.get('company_name')}, 저장된 ID: {stored_account_id}, 입력된 ID: {aws_account_id}")
            # 마지막 4자리 비교
            if stored_account_id.endswith(aws_account_id):
                logger.info(f"고객 매치 성공: {customer.get('company_name')}")
                return customer
        
        return None
        
    except ClientError as e:
        logger.error(f"DynamoDB 조회 오류: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"고객 조회 중 예상치 못한 오류: {str(e)}")
        raise


def classify_customer(customer_info: Dict[str, Any]) -> str:
    """
    고객 분류 (MSP vs 일반 고객)
    
    Args:
        customer_info: 고객 정보
    
    Returns:
        "MSP" 또는 "General"
    """
    support_level = customer_info.get('support_level', '').upper()
    
    if support_level == 'MSP':
        return 'MSP'
    elif support_level == 'GENERAL':
        return 'General'
    else:
        # 기본값은 일반 고객으로 분류
        logger.warning(f"알 수 없는 지원 레벨: {support_level}, 일반 고객으로 분류")
        return 'General'


def get_assigned_engineer(customer_info: Dict[str, Any]) -> Optional[str]:
    """
    담당 엔지니어 정보 조회
    
    Args:
        customer_info: 고객 정보
    
    Returns:
        담당 엔지니어 정보 또는 None
    """
    try:
        assigned_engineer_id = customer_info.get('assigned_engineer')
        
        if not assigned_engineer_id:
            return None
        
        # 엔지니어 정보 조회
        import os
        engineers_table_name = os.environ.get('ENGINEERS_TABLE', 'dev-saltware-engineers')
        engineers_table = dynamodb.Table(engineers_table_name)
        
        response = engineers_table.get_item(
            Key={'engineer_id': assigned_engineer_id}
        )
        
        engineer = response.get('Item')
        if engineer:
            return {
                "engineer_id": engineer.get('engineer_id'),
                "name": engineer.get('name'),
                "part": engineer.get('part'),
                "phone": engineer.get('phone'),
                "is_available": engineer.get('is_available', True)
            }
        
        return None
        
    except Exception as e:
        logger.error(f"담당 엔지니어 조회 중 오류: {str(e)}")
        return None


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
            "customer_found": False,
            "customer_type": "Unknown",
            "customer_info": None,
            "message": message,
            "error": True
        }, ensure_ascii=False)
    }