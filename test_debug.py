import boto3
from moto import mock_aws
import json

@mock_aws
def test_debug():
    # DynamoDB 테이블 생성
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    
    table = dynamodb.create_table(
        TableName='dev-saltware-customers',
        KeySchema=[
            {'AttributeName': 'customer_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'customer_id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    table.wait_until_exists()
    
    # 테스트 데이터 삽입
    table.put_item(Item={
        'customer_id': 'cust_001',
        'company_name': 'ABC Corporation',
        'aws_account_id': '123456781234',
        'support_level': 'MSP',
        'assigned_engineer': 'eng_001'
    })
    
    # 데이터 확인
    response = table.scan()
    print("저장된 데이터:", json.dumps(response['Items'], indent=2, ensure_ascii=False))
    
    # 필터링 테스트
    response = table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('company_name').eq('ABC Corporation')
    )
    print("필터링된 데이터:", json.dumps(response['Items'], indent=2, ensure_ascii=False))
    
    # AWS Account ID 확인
    for item in response['Items']:
        stored_id = item.get('aws_account_id', '')
        print(f"저장된 ID: {stored_id}, 마지막 4자리: {stored_id[-4:]}")
        print(f"1234와 매치: {stored_id.endswith('1234')}")

if __name__ == '__main__':
    test_debug()