import json
import boto3
import logging
from datetime import datetime, time
from typing import Dict, Any, List
import pytz
from botocore.exceptions import ClientError

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 업무시간 설정 (평일 09:00-18:00)
BUSINESS_START_TIME = time(9, 0)  # 09:00
BUSINESS_END_TIME = time(18, 0)   # 18:00

# 한국 공휴일 (2025년 기준)
KOREAN_HOLIDAYS_2025 = [
    "2025-01-01",  # 신정
    "2025-01-28",  # 설날 연휴
    "2025-01-29",  # 설날
    "2025-01-30",  # 설날 연휴
    "2025-03-01",  # 삼일절
    "2025-05-05",  # 어린이날
    "2025-05-13",  # 부처님오신날
    "2025-06-06",  # 현충일
    "2025-08-15",  # 광복절
    "2025-09-06",  # 추석 연휴
    "2025-09-07",  # 추석 연휴
    "2025-09-08",  # 추석
    "2025-09-09",  # 추석 연휴
    "2025-10-03",  # 개천절
    "2025-10-09",  # 한글날
    "2025-12-25",  # 크리스마스
]

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    업무시간 확인 Lambda 함수
    
    Args:
        event: {
            "timezone": "Asia/Seoul" (선택사항, 기본값),
            "check_time": "2025-01-15T14:30:00" (선택사항, 현재 시간 사용)
        }
    
    Returns:
        {
            "statusCode": 200,
            "body": {
                "is_business_hours": true/false,
                "current_time": "2025-01-15T14:30:00+09:00",
                "business_hours": "평일 09:00-18:00",
                "next_business_day": "2025-01-16T09:00:00+09:00",
                "message": "현재 업무시간입니다" | "현재 업무시간이 아닙니다"
            }
        }
    """
    
    try:
        # 입력 파라미터 처리
        timezone_str = event.get('timezone', 'Asia/Seoul')
        check_time_str = event.get('check_time')
        
        # 시간대 설정
        try:
            target_timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"알 수 없는 시간대: {timezone_str}, 한국 시간 사용")
            target_timezone = KST
        
        # 확인할 시간 설정
        if check_time_str:
            try:
                # ISO 형식 시간 파싱
                check_time = datetime.fromisoformat(check_time_str.replace('Z', '+00:00'))
                # 지정된 시간대로 변환
                if check_time.tzinfo is None:
                    check_time = target_timezone.localize(check_time)
                else:
                    check_time = check_time.astimezone(target_timezone)
            except ValueError as e:
                logger.error(f"잘못된 시간 형식: {check_time_str}")
                return create_error_response(400, "잘못된 시간 형식입니다.")
        else:
            # 현재 시간 사용
            check_time = datetime.now(target_timezone)
        
        logger.info(f"업무시간 확인 요청 - 시간: {check_time}")
        
        # 업무시간 확인
        is_business_hours = check_business_hours(check_time)
        
        # 다음 업무일 계산
        next_business_day = get_next_business_day(check_time)
        
        # 응답 메시지 생성
        if is_business_hours:
            message = "현재 업무시간입니다"
            logger.info(f"업무시간 확인 결과: 업무시간 중 - {check_time}")
        else:
            message = "현재 업무시간이 아닙니다"
            logger.info(f"업무시간 확인 결과: 업무시간 외 - {check_time}")
        
        response_body = {
            "is_business_hours": is_business_hours,
            "current_time": check_time.isoformat(),
            "business_hours": "평일 09:00-18:00 (한국시간)",
            "next_business_day": next_business_day.isoformat() if next_business_day else None,
            "message": message
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_body, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"업무시간 확인 중 오류 발생: {str(e)}")
        return create_error_response(500, "시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")


def check_business_hours(check_time: datetime) -> bool:
    """
    업무시간 확인
    
    Args:
        check_time: 확인할 시간 (timezone-aware datetime)
    
    Returns:
        업무시간 여부 (True/False)
    """
    try:
        # 한국 시간으로 변환
        kst_time = check_time.astimezone(KST)
        
        # 요일 확인 (0=월요일, 6=일요일)
        weekday = kst_time.weekday()
        
        # 주말 확인 (토요일=5, 일요일=6)
        if weekday >= 5:
            return False
        
        # 공휴일 확인
        date_str = kst_time.strftime('%Y-%m-%d')
        if is_holiday(date_str):
            return False
        
        # 업무시간 확인 (09:00-18:00)
        current_time = kst_time.time()
        if BUSINESS_START_TIME <= current_time < BUSINESS_END_TIME:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"업무시간 확인 중 오류: {str(e)}")
        return False


def is_holiday(date_str: str) -> bool:
    """
    공휴일 확인
    
    Args:
        date_str: 날짜 문자열 (YYYY-MM-DD 형식)
    
    Returns:
        공휴일 여부 (True/False)
    """
    # 하드코딩된 공휴일 목록에서 확인
    if date_str in KOREAN_HOLIDAYS_2025:
        return True
    
    # 추가적인 공휴일 로직 (예: 대체공휴일 등)을 여기에 구현할 수 있음
    
    return False


def get_next_business_day(current_time: datetime) -> datetime:
    """
    다음 업무일 계산
    
    Args:
        current_time: 현재 시간
    
    Returns:
        다음 업무일의 업무 시작 시간
    """
    try:
        # 한국 시간으로 변환
        kst_time = current_time.astimezone(KST)
        
        # 현재 날짜부터 시작
        next_day = kst_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # 현재 시간이 업무시간 중이라면 현재 날짜 반환
        if check_business_hours(current_time):
            return next_day
        
        # 현재 시간이 업무시간 전이라면 오늘 반환
        if (kst_time.weekday() < 5 and 
            not is_holiday(kst_time.strftime('%Y-%m-%d')) and 
            kst_time.time() < BUSINESS_START_TIME):
            return next_day
        
        # 다음 업무일 찾기
        from datetime import timedelta
        
        next_day += timedelta(days=1)
        
        # 최대 10일까지 검색 (무한 루프 방지)
        for _ in range(10):
            # 주말이 아니고 공휴일이 아닌 날 찾기
            if (next_day.weekday() < 5 and 
                not is_holiday(next_day.strftime('%Y-%m-%d'))):
                return next_day.replace(hour=9, minute=0, second=0, microsecond=0)
            
            next_day += timedelta(days=1)
        
        # 찾지 못한 경우 현재 시간 + 1일 반환
        return kst_time + timedelta(days=1)
        
    except Exception as e:
        logger.error(f"다음 업무일 계산 중 오류: {str(e)}")
        # 오류 발생 시 현재 시간 + 1일 반환
        return current_time + timedelta(days=1)


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
            "is_business_hours": False,
            "current_time": None,
            "business_hours": "평일 09:00-18:00 (한국시간)",
            "next_business_day": None,
            "message": message,
            "error": True
        }, ensure_ascii=False)
    }


# 캐싱을 위한 간단한 메모리 캐시 (Lambda 컨테이너 재사용 시 활용)
_cache = {}
_cache_ttl = {}

def get_cached_business_hours(check_time: datetime, ttl_seconds: int = 300) -> bool:
    """
    캐싱된 업무시간 확인 결과 반환
    
    Args:
        check_time: 확인할 시간
        ttl_seconds: 캐시 TTL (초)
    
    Returns:
        업무시간 여부
    """
    try:
        # 캐시 키 생성 (분 단위로 캐싱)
        cache_key = check_time.strftime('%Y-%m-%d-%H-%M')
        
        # 캐시 확인
        if cache_key in _cache:
            cache_time = _cache_ttl.get(cache_key, 0)
            if datetime.now().timestamp() - cache_time < ttl_seconds:
                logger.info(f"캐시된 업무시간 확인 결과 사용: {cache_key}")
                return _cache[cache_key]
        
        # 캐시 미스 - 새로 계산
        result = check_business_hours(check_time)
        
        # 캐시 저장
        _cache[cache_key] = result
        _cache_ttl[cache_key] = datetime.now().timestamp()
        
        # 캐시 크기 제한 (최대 100개)
        if len(_cache) > 100:
            # 가장 오래된 항목 삭제
            oldest_key = min(_cache_ttl.keys(), key=lambda k: _cache_ttl[k])
            del _cache[oldest_key]
            del _cache_ttl[oldest_key]
        
        return result
        
    except Exception as e:
        logger.error(f"캐시된 업무시간 확인 중 오류: {str(e)}")
        return check_business_hours(check_time)