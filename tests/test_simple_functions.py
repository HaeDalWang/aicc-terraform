import unittest
import sys
import os
from datetime import datetime
import pytz

# Lambda 함수 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from customer_lookup import classify_customer
from business_hours import check_business_hours, is_holiday, get_next_business_day
from call_logging import generate_call_id, mask_phone_number, hash_phone_number


class TestSimpleFunctions(unittest.TestCase):
    """간단한 유틸리티 함수들 테스트"""
    
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
        
        # 빈 딕셔너리
        empty_customer = {}
        self.assertEqual(classify_customer(empty_customer), 'General')
    
    def test_mask_phone_number(self):
        """전화번호 마스킹 테스트"""
        # 일반적인 휴대폰 번호 (13자리) - 7자리 초과
        phone1 = '010-1234-5678'  # 13자리
        masked1 = mask_phone_number(phone1)
        # 앞 3자리 + 마스킹(13-7=6개) + 뒤 4자리
        self.assertEqual(masked1, '010******5678')
        
        # 4자리 이하 - 모두 마스킹
        phone2 = '1234'
        masked2 = mask_phone_number(phone2)
        self.assertEqual(masked2, '****')
        
        # 7자리 - 경계값
        phone3 = '1234567'
        masked3 = mask_phone_number(phone3)
        # 앞 2자리 + 마스킹(7-4=3개) + 뒤 2자리
        self.assertEqual(masked3, '12***67')
        
        # 2자리 - 모두 마스킹
        phone4 = '12'
        masked4 = mask_phone_number(phone4)
        self.assertEqual(masked4, '**')
        
        # 8자리 - 7자리 초과
        phone5 = '12345678'
        masked5 = mask_phone_number(phone5)
        # 앞 3자리 + 마스킹(8-7=1개) + 뒤 4자리
        self.assertEqual(masked5, '123*5678')
    
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
    
    def test_check_business_hours(self):
        """업무시간 확인 함수 테스트"""
        kst = pytz.timezone('Asia/Seoul')
        
        # 평일 업무시간
        weekday_business = kst.localize(datetime(2025, 1, 15, 10, 0))  # 수요일 10시
        self.assertTrue(check_business_hours(weekday_business))
        
        # 평일 업무시간 외 (이른 아침)
        weekday_early = kst.localize(datetime(2025, 1, 15, 8, 0))  # 수요일 8시
        self.assertFalse(check_business_hours(weekday_early))
        
        # 평일 업무시간 외 (늦은 저녁)
        weekday_late = kst.localize(datetime(2025, 1, 15, 19, 0))  # 수요일 19시
        self.assertFalse(check_business_hours(weekday_late))
        
        # 주말 (토요일)
        weekend_saturday = kst.localize(datetime(2025, 1, 18, 10, 0))  # 토요일 10시
        self.assertFalse(check_business_hours(weekend_saturday))
        
        # 주말 (일요일)
        weekend_sunday = kst.localize(datetime(2025, 1, 19, 10, 0))  # 일요일 10시
        self.assertFalse(check_business_hours(weekend_sunday))
    
    def test_is_holiday(self):
        """공휴일 확인 함수 테스트"""
        # 신정
        self.assertTrue(is_holiday('2025-01-01'))
        
        # 설날
        self.assertTrue(is_holiday('2025-01-29'))
        
        # 삼일절
        self.assertTrue(is_holiday('2025-03-01'))
        
        # 일반 평일
        self.assertFalse(is_holiday('2025-01-15'))
        
        # 존재하지 않는 공휴일
        self.assertFalse(is_holiday('2025-02-14'))
    
    def test_get_next_business_day(self):
        """다음 업무일 계산 테스트"""
        kst = pytz.timezone('Asia/Seoul')
        
        # 평일 업무시간 중 - 현재 날짜의 9시 반환
        current_business = kst.localize(datetime(2025, 1, 15, 10, 0))  # 수요일 10시
        next_day = get_next_business_day(current_business)
        self.assertEqual(next_day.date(), current_business.date())
        self.assertEqual(next_day.hour, 9)
        self.assertEqual(next_day.minute, 0)
        
        # 평일 업무시간 전 - 현재 날짜의 9시 반환
        before_business = kst.localize(datetime(2025, 1, 15, 8, 0))  # 수요일 8시
        next_day = get_next_business_day(before_business)
        self.assertEqual(next_day.date(), before_business.date())
        self.assertEqual(next_day.hour, 9)
        
        # 평일 업무시간 후 - 다음 업무일의 9시 반환
        after_business = kst.localize(datetime(2025, 1, 15, 19, 0))  # 수요일 19시
        next_day = get_next_business_day(after_business)
        self.assertEqual(next_day.date(), datetime(2025, 1, 16).date())  # 목요일
        self.assertEqual(next_day.hour, 9)
    
    def test_generate_call_id(self):
        """통화 ID 생성 테스트"""
        call_id1 = generate_call_id()
        call_id2 = generate_call_id()
        
        # 고유성 확인
        self.assertNotEqual(call_id1, call_id2)
        
        # 형식 확인
        self.assertTrue(call_id1.startswith('call_'))
        self.assertTrue(call_id2.startswith('call_'))
        
        # 길이 확인 (call_ + 14자리 타임스탬프 + _ + 8자리 UUID)
        self.assertGreater(len(call_id1), 20)
        self.assertGreater(len(call_id2), 20)


if __name__ == '__main__':
    unittest.main()