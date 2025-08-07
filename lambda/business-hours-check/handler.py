"""
업무시간 체크 Lambda 함수
OO금융지주 AICC 시스템 - 업무시간 확인 및 라우팅 결정
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

# 업무시간 설정
BUSINESS_HOURS = {
    'start_hour': 9,    # 오전 9시
    'end_hour': 18,     # 오후 6시
    'weekdays': [0, 1, 2, 3, 4]  # 월-금 (0=월요일, 6=일요일)
}

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    업무시간 체크 Lambda 핸들러
    
    Args:
        event: Amazon Connect에서 전달되는 이벤트 데이터
        context: Lambda 실행 컨텍스트
        
    Returns:
        dict: 업무시간 여부 및 라우팅 정보
    """
    try:
        logger.info("업무시간 체크 시작")
        
        # 현재 한국 시간 가져오기
        now_kst = datetime.now(KST)
        current_hour = now_kst.hour
        current_weekday = now_kst.weekday()
        
        logger.info(f"현재 시간: {now_kst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"현재 시간(시): {current_hour}, 요일: {current_weekday}")
        
        # 업무시간 체크
        is_business_hours = (
            current_weekday in BUSINESS_HOURS['weekdays'] and
            BUSINESS_HOURS['start_hour'] <= current_hour < BUSINESS_HOURS['end_hour']
        )
        
        # 응답 데이터 구성
        response = {
            'isBusinessHours': is_business_hours,
            'currentTime': now_kst.strftime('%Y-%m-%d %H:%M:%S'),
            'currentHour': current_hour,
            'currentWeekday': current_weekday,
            'businessHoursStart': BUSINESS_HOURS['start_hour'],
            'businessHoursEnd': BUSINESS_HOURS['end_hour'],
            'message': '업무시간입니다.' if is_business_hours else '업무시간 외입니다.'
        }
        
        logger.info(f"업무시간 체크 결과: {response}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response, ensure_ascii=False),
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }
        
    except Exception as e:
        logger.error(f"업무시간 체크 중 오류 발생: {str(e)}")
        
        # 오류 발생 시 기본적으로 업무시간으로 처리 (안전장치)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'isBusinessHours': True,
                'error': '업무시간 체크 중 오류가 발생했습니다.',
                'message': '기본 업무시간으로 처리합니다.'
            }, ensure_ascii=False),
            'headers': {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }