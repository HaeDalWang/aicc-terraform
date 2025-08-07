#!/usr/bin/env python3
"""
Script to verify the populated test data in DynamoDB tables
"""

import boto3
import json
from datetime import datetime

def verify_table_data(table_name, description):
    """Verify data in a specific table"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.scan(Limit=5)
        items = response.get('Items', [])
        
        print(f"\n=== {description} ===")
        print(f"테이블명: {table_name}")
        print(f"데이터 개수: {len(items)}개")
        
        if items:
            print("샘플 데이터:")
            for i, item in enumerate(items[:3], 1):
                print(f"  {i}. {json.dumps(item, ensure_ascii=False, indent=4, default=str)}")
        else:
            print("데이터가 없습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")

def main():
    """Main verification function"""
    print("DynamoDB 테이블 데이터 확인")
    print("=" * 50)
    
    # Verify each table
    verify_table_data('dev-saltware-customers', '고객 정보 테이블')
    verify_table_data('dev-saltware-engineers', '엔지니어 정보 테이블')
    verify_table_data('dev-saltware-call-logs', '통화 로그 테이블')

if __name__ == "__main__":
    main()