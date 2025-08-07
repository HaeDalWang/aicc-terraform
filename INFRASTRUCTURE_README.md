# Saltware IVR System Infrastructure

## Overview
This infrastructure setup creates the foundational components for the Saltware IVR system including DynamoDB tables, IAM roles, and CloudWatch log groups.

## Components Created

### DynamoDB Tables

1. **Customers Table** (`{environment}-saltware-customers`)
   - Primary Key: `customer_id`
   - Global Secondary Indexes:
     - `CompanyNameIndex`: For company name lookups
     - `AwsAccountIdIndex`: For AWS Account ID lookups
   - Contains customer information, support levels, and contact details

2. **Call Logs Table** (`{environment}-saltware-call-logs`)
   - Primary Key: `call_id`
   - Global Secondary Index: `CustomerCallsIndex` (customer_id + call_start_time)
   - TTL enabled for automatic cleanup after 90 days
   - Stores all call interaction logs

3. **Engineers Table** (`{environment}-saltware-engineers`)
   - Primary Key: `engineer_id`
   - Global Secondary Indexes:
     - `PartIndex`: For part-based queries (Leaf, Tiger, Aqua)
     - `AvailabilityIndex`: For availability-based queries
   - Contains engineer information, availability, and specialties

### IAM Roles and Policies

- **Lambda Execution Role**: `{environment}-saltware-lambda-execution-role`
  - Basic Lambda execution permissions
  - DynamoDB read/write access to all IVR tables
  - CloudWatch Logs permissions

### CloudWatch Log Groups

- `/aws/lambda/{environment}-saltware-customer-lookup`
- `/aws/lambda/{environment}-saltware-business-hours`
- `/aws/lambda/{environment}-saltware-call-logging`
- `/aws/connect/{connect_instance_alias}`

## Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform installed (version 1.0+)

### Steps

1. **Initialize Terraform**
   ```bash
   terraform init
   ```

2. **Review the plan**
   ```bash
   terraform plan
   ```

3. **Apply the infrastructure**
   ```bash
   terraform apply
   ```

4. **Populate test data** (optional)
   ```bash
   cd scripts
   python3 populate_test_data.py
   ```

## Environment Variables

The following variables can be configured in `terraform.tfvars`:

- `environment`: Environment name (dev, staging, prod)
- `aws_region`: AWS region (default: ap-northeast-2)
- `connect_instance_alias`: Connect instance alias

## Test Data

The `scripts/populate_test_data.py` script creates sample data:

### Sample Customers
- ABC Corporation (MSP customer)
- XYZ Tech (General customer)  
- StartupCo (General customer)

### Sample Engineers
- 김리더 (Leaf team leader)
- 박엔지니어 (Tiger team member)
- 이시니어 (Aqua team member)
- 최주니어 (Leaf team member)

### Sample Call Logs
- 10 sample call records with various flow paths and resolutions

## Usage

### Accessing Tables
Use the output values to reference tables in Lambda functions:

```python
import boto3

# Get table names from environment variables or Terraform outputs
customers_table = boto3.resource('dynamodb').Table('dev-saltware-customers')
call_logs_table = boto3.resource('dynamodb').Table('dev-saltware-call-logs')
engineers_table = boto3.resource('dynamodb').Table('dev-saltware-engineers')
```

### IAM Role for Lambda Functions
Use the created IAM role ARN when creating Lambda functions:
- Role ARN: Available in Terraform outputs as `lambda_execution_role_arn`

## Monitoring

CloudWatch log groups are automatically created for:
- Lambda function logs (30-day retention for most, 90-day for call logs)
- Connect instance logs (30-day retention)

## Security Considerations

- All tables use encryption at rest (AWS managed keys)
- IAM policies follow least privilege principle
- TTL configured on call logs for automatic data cleanup
- Sensitive data should be encrypted before storage

## Cleanup

To destroy the infrastructure:
```bash
terraform destroy
```

**Warning**: This will permanently delete all data in the DynamoDB tables.