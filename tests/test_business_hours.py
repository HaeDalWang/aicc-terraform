import unittest
import json
from datetime import datetime, time
from unittest.mock import patch, MagicMock
import sys
import os
import pytz

# Lambda 함수 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from business_hours import (
    lambda_handler, 
    check_business_hours, 
    is_holiday, 
    get_next_business_day,
    get_cached_business_hours
)


class TestBusinessHours(unittest.TestCase):
    """업무시간 확인 Lambda 함수 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.kst = pytz.timezone('Asia/Seoul')
    
    def test_business_hours_weekday_morning(self):
        """평일 오전 업무시간 테스트"""
        # 2025년 1월 15일 (수요일) 오전 10시
        test_time = self.kst.localize(datetime(2025, 1, 15, 10, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['is_business_hours'])
        self.assertEqual(body['message'], '현재 업무시간입니다')
    
    def test_business_hours_weekday_afternoon(self):
        """평일 오후 업무시간 테스트"""
        # 2025년 1월 15일 (수요일) 오후 3시
        test_time = self.kst.localize(datetime(2025, 1, 15, 15, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['is_business_hours'])
    
    def test_non_business_hours_early_morning(self):
        """평일 이른 아침 업무시간 외 테스트"""
        # 2025년 1월 15일 (수요일) 오전 8시
        test_time = self.kst.localize(datetime(2025, 1, 15, 8, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['is_business_hours'])
        self.assertEqual(body['message'], '현재 업무시간이 아닙니다')
    
    def test_non_business_hours_late_evening(self):
        """평일 늦은 저녁 업무시간 외 테스트"""
        # 2025년 1월 15일 (수요일) 오후 7시
        test_time = self.kst.localize(datetime(2025, 1, 15, 19, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['is_business_hours'])
    
    def test_weekend_saturday(self):
        """토요일 업무시간 외 테스트"""
        # 2025년 1월 18일 (토요일) 오전 10시
        test_time = self.kst.localize(datetime(2025, 1, 18, 10, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['is_business_hours'])
    
    def test_weekend_sunday(self):
        """일요일 업무시간 외 테스트"""
        # 2025년 1월 19일 (일요일) 오전 10시
        test_time = self.kst.localize(datetime(2025, 1, 19, 10, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['is_business_hours'])
    
    def test_holiday_new_year(self):
        """신정 공휴일 테스트"""
        # 2025년 1월 1일 (신정) 오전 10시
        test_time = self.kst.localize(datetime(2025, 1, 1, 10, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['is_business_hours'])
    
    def test_holiday_lunar_new_year(self):
        """설날 공휴일 테스트"""
        # 2025년 1월 29일 (설날) 오전 10시
        test_time = self.kst.localize(datetime(2025, 1, 29, 10, 0))
        
        event = {
            'check_time': test_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertFalse(body['is_business_hours'])
    
    def test_current_time_default(self):
        """현재 시간 기본값 테스트"""
        event = {}
        
        with patch('business_hours.datetime') as mock_datetime:
            # 평일 업무시간으로 설정
            mock_now = self.kst.localize(datetime(2025, 1, 15, 10, 0))
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertIsNotNone(body['current_time'])
    
    def test_invalid_time_format(self):
        """잘못된 시간 형식 테스트"""
        event = {
            'check_time': 'invalid-time-format'
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertTrue(body['error'])
    
    def test_is_holiday_function(self):
        """공휴일 확인 함수 테스트"""
        # 신정
        self.assertTrue(is_holiday('2025-01-01'))
        
        # 설날
        self.assertTrue(is_holiday('2025-01-29'))
        
        # 일반 평일
        self.assertFalse(is_holiday('2025-01-15'))
        
        # 존재하지 않는 날짜
        self.assertFalse(is_holiday('2025-02-30'))
    
    def test_check_business_hours_function(self):
        """업무시간 확인 함수 직접 테스트"""
        # 평일 업무시간
        weekday_business = self.kst.localize(datetime(2025, 1, 15, 10, 0))
        self.assertTrue(check_business_hours(weekday_business))
        
        # 평일 업무시간 외
        weekday_non_business = self.kst.localize(datetime(2025, 1, 15, 8, 0))
        self.assertFalse(check_business_hours(weekday_non_business))
        
        # 주말
        weekend = self.kst.localize(datetime(2025, 1, 18, 10, 0))
        self.assertFalse(check_business_hours(weekend))
        
        # 공휴일
        holiday = self.kst.localize(datetime(2025, 1, 1, 10, 0))
        self.assertFalse(check_business_hours(holiday))
    
    def test_get_next_business_day(self):
        """다음 업무일 계산 테스트"""
        # 평일 업무시간 중 - 현재 날짜 반환
        current_business = self.kst.localize(datetime(2025, 1, 15, 10, 0))
        next_day = get_next_business_day(current_business)
        self.assertEqual(next_day.date(), current_business.date())
        self.assertEqual(next_day.hour, 9)
        
        # 평일 업무시간 후 - 다음 업무일 반환
        after_business = self.kst.localize(datetime(2025, 1, 15, 19, 0))
        next_day = get_next_business_day(after_business)
        self.assertEqual(next_day.date(), datetime(2025, 1, 16).date())
        self.assertEqual(next_day.hour, 9)
        
        # 금요일 업무시간 후 - 다음 월요일 반환
        friday_after = self.kst.localize(datetime(2025, 1, 17, 19, 0))
        next_day = get_next_business_day(friday_after)
        self.assertEqual(next_day.date(), datetime(2025, 1, 20).date())
        self.assertEqual(next_day.hour, 9)
    
    def test_timezone_conversion(self):
        """시간대 변환 테스트"""
        # UTC 시간으로 입력
        utc_time = datetime(2025, 1, 15, 1, 0, tzinfo=pytz.UTC)  # UTC 01:00 = KST 10:00
        
        event = {
            'check_time': utc_time.isoformat()
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['is_business_hours'])  # KST 10:00는 업무시간
    
    def test_caching_functionality(self):
        """캐싱 기능 테스트"""
        test_time = self.kst.localize(datetime(2025, 1, 15, 10, 0))
        
        # 첫 번째 호출
        result1 = get_cached_business_hours(test_time)
        
        # 두 번째 호출 (캐시 사용)
        result2 = get_cached_business_hours(test_time)
        
        self.assertEqual(result1, result2)
        self.assertTrue(result1)  # 업무시간이므로 True


if __name__ == '__main__':
    unittest.main()