import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Amazon Connect에서 호출되는 Lambda 함수
    고객의 문의에 대한 AI 기반 응답을 제공
    """
    try:
        # Connect에서 전달받은 고객 정보
        contact_data = event.get('Details', {}).get('ContactData', {})
        customer_endpoint = contact_data.get('CustomerEndpoint', {})
        customer_number = customer_endpoint.get('Address', 'Unknown')
        
        # 기본 응답 메시지들
        responses = {
            "general": """
            안녕하세요! Saltware는 클라우드 기술 전문 업체입니다. 
            저희는 AWS, Azure, GCP 등 다양한 클라우드 플랫폼에서 
            인프라 구축, 마이그레이션, 운영 관리 서비스를 제공합니다.
            
            주요 서비스:
            1. 클라우드 인프라 설계 및 구축
            2. 레거시 시스템 클라우드 마이그레이션  
            3. DevOps 및 CI/CD 파이프라인 구축
            4. 클라우드 보안 및 모니터링
            5. 24/7 운영 관리 서비스
            
            더 자세한 상담을 원하시면 전담 엔지니어와 연결해드리겠습니다.
            """,
            
            "pricing": """
            Saltware의 서비스 요금은 프로젝트 규모와 요구사항에 따라 달라집니다.
            
            기본 컨설팅: 월 300만원부터
            인프라 구축: 프로젝트당 1,000만원부터  
            운영 관리: 월 500만원부터
            
            정확한 견적은 무료 상담을 통해 제공해드립니다.
            """,
            
            "contact": """
            Saltware 연락처 정보:
            - 대표번호: 02-1234-5678
            - 이메일: info@saltware.co.kr
            - 주소: 서울시 강남구 테헤란로 123
            - 웹사이트: www.saltware.co.kr
            
            영업시간: 평일 09:00 ~ 18:00
            """
        }
        
        # 간단한 키워드 기반 응답 (실제로는 더 정교한 AI 모델 사용 가능)
        response_text = responses["general"]
        
        # 고객 정보 로깅 (실제 운영시에는 개인정보 보호 고려)
        logger.info(f"Customer call from: {customer_number}")
        
        # Connect로 반환할 응답
        return {
            'response': response_text,
            'customer_number': customer_number,
            'timestamp': context.aws_request_id
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'response': '죄송합니다. 일시적인 오류가 발생했습니다. 전담 엔지니어에게 연결해드리겠습니다.',
            'error': str(e)
        }

def get_enhanced_ai_response(customer_input, customer_history=None):
    """
    향후 확장을 위한 고도화된 AI 응답 함수
    OpenAI GPT, AWS Bedrock 등과 연동 가능
    """
    # 여기에 실제 AI 모델 호출 로직 구현
    # 예: OpenAI API, AWS Bedrock, 자체 ML 모델 등
    pass

def log_customer_interaction(customer_number, interaction_type, response):
    """
    고객 상호작용 로깅 (분석 및 개선을 위해)
    """
    # CloudWatch Logs, DynamoDB 등에 저장
    logger.info({
        'customer_number': customer_number,
        'interaction_type': interaction_type,
        'response_length': len(response),
        'timestamp': context.aws_request_id
    })