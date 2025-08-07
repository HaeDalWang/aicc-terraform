#!/usr/bin/env python3
"""
Script to populate DynamoDB tables with initial test data for Saltware IVR System
"""

import boto3
import json
import uuid
from datetime import datetime, timedelta
import os

def get_table_name(base_name, environment='dev'):
    """Generate table name with environment prefix"""
    return f"{environment}-saltware-{base_name}"

def populate_customers_table(dynamodb, environment='dev'):
    """Populate customers table with test data"""
    table_name = get_table_name('customers', environment)
    table = dynamodb.Table(table_name)
    
    customers = [
        {
            'customer_id': str(uuid.uuid4()),
            'company_name': '백패커',
            'aws_account_id': '123456789012',
            'support_level': 'MSP',
            'assigned_engineer': 'eng-001',
            'contact_info': {
                'phone': '+82-2-1234-5678',
                'email': 'contact@abc-corp.com'
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'customer_id': str(uuid.uuid4()),
            'company_name': '이동의즐거움',
            'aws_account_id': '987654321098',
            'support_level': 'General',
            'assigned_engineer': 'eng-002',
            'contact_info': {
                'phone': '+82-2-9876-5432',
                'email': 'support@xyz-tech.com'
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'customer_id': str(uuid.uuid4()),
            'company_name': '오마이호텔',
            'aws_account_id': '555666777888',
            'support_level': 'General',
            'contact_info': {
                'phone': '+82-2-5555-6666',
                'email': 'hello@startupco.com'
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    for customer in customers:
        try:
            table.put_item(Item=customer)
            print(f"Added customer: {customer['company_name']}")
        except Exception as e:
            print(f"Error adding customer {customer['company_name']}: {e}")

def populate_engineers_table(dynamodb, environment='dev'):
    """Populate engineers table with test data based on COC guide"""
    table_name = get_table_name('engineers', environment)
    table = dynamodb.Table(table_name)
    
    engineers = [
        {
            'engineer_id': 'eng-001',
            'name': '이주엽',
            'phone': '+82-10-1111-2222',
            'email': 'leader.kim@saltware.co.kr',
            'part': 'Leaf',
            'role': 'Leader',
            'is_available': 'true',
            'current_load': 2,
            'specialties': ['AWS', 'Kubernetes', 'DevOps'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'engineer_id': 'eng-002',
            'name': '김범중',
            'phone': '+82-10-3333-4444',
            'email': 'engineer.park@saltware.co.kr',
            'part': 'Tiger',
            'role': 'Member',
            'is_available': 'true',
            'current_load': 1,
            'specialties': ['AWS', 'Database', 'Monitoring'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'engineer_id': 'eng-003',
            'name': '김희수',
            'phone': '+82-10-5555-6666',
            'email': 'senior.lee@saltware.co.kr',
            'part': 'Aqua',
            'role': 'Member',
            'is_available': 'false',
            'current_load': 5,
            'specialties': ['Security', 'Networking', 'Compliance'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'engineer_id': 'eng-004',
            'name': '김이현',
            'phone': '+82-10-7777-8888',
            'email': 'junior.choi@saltware.co.kr',
            'part': 'Leaf',
            'role': 'Member',
            'is_available': 'true',
            'current_load': 0,
            'specialties': ['AWS', 'Lambda', 'API Gateway'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
    
    for engineer in engineers:
        try:
            table.put_item(Item=engineer)
            print(f"Added engineer: {engineer['name']} ({engineer['part']} - {engineer['role']})")
        except Exception as e:
            print(f"Error adding engineer {engineer['name']}: {e}")

def populate_sample_call_logs(dynamodb, environment='dev'):
    """Populate call logs table with sample data"""
    table_name = get_table_name('call-logs', environment)
    table = dynamodb.Table(table_name)
    
    # Generate sample call logs for the past week
    base_time = datetime.now() - timedelta(days=7)
    
    call_logs = []
    for i in range(10):
        call_time = base_time + timedelta(hours=i*6, minutes=i*15)
        ttl_time = call_time + timedelta(days=90)  # 90 days retention
        
        call_log = {
            'call_id': str(uuid.uuid4()),
            'customer_id': f'customer-{i%3 + 1}',
            'phone_number': f'+82-10-{1000+i:04d}-{5678+i:04d}',
            'call_start_time': call_time.isoformat(),
            'call_end_time': (call_time + timedelta(minutes=5+i)).isoformat(),
            'flow_path': ['MainEntry', 'CustomerAuth', 'MSPCustomer' if i%2 == 0 else 'GeneralCustomer'],
            'resolution': 'Connected to engineer' if i%3 != 0 else 'Left voicemail',
            'assigned_to': f'eng-{(i%4)+1:03d}',
            'notes': f'Sample call log entry {i+1}',
            'ttl': int(ttl_time.timestamp()),
            'created_at': call_time.isoformat()
        }
        call_logs.append(call_log)
    
    for call_log in call_logs:
        try:
            table.put_item(Item=call_log)
            print(f"Added call log: {call_log['call_id'][:8]}...")
        except Exception as e:
            print(f"Error adding call log: {e}")

def main():
    """Main function to populate all tables"""
    # Get environment from environment variable or default to 'dev'
    environment = os.getenv('ENVIRONMENT', 'dev')
    
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    
    print(f"Populating test data for environment: {environment}")
    print("=" * 50)
    
    # Populate tables
    print("Populating customers table...")
    populate_customers_table(dynamodb, environment)
    
    print("\nPopulating engineers table...")
    populate_engineers_table(dynamodb, environment)
    
    print("\nPopulating sample call logs...")
    populate_sample_call_logs(dynamodb, environment)
    
    print("\nTest data population completed!")

if __name__ == "__main__":
    main()