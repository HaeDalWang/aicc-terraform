# Technology Stack

## Infrastructure as Code
- **Terraform**: Primary IaC tool for AWS resource provisioning
- **Provider**: AWS Provider ~> 5.0
- **State Management**: Local terraform.tfstate files

## AWS Services
- **Amazon Connect**: Core call center platform
- **Lambda**: Python 3.9 runtime for AI response functions
- **DynamoDB**: Customer data, call logs, and engineer information storage
- **CloudWatch**: Logging, monitoring, and dashboards
- **SNS**: Alert notifications
- **IAM**: Role-based access control

## Programming Languages
- **Python 3.9**: Lambda functions and utility scripts
- **HCL**: Terraform configuration files
- **JSON**: Contact flow definitions

## Development Environment
- **Region**: ap-northeast-2 (Seoul)
- **Environment**: dev/staging/prod separation via variables

## Common Commands

### Terraform Operations
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure
terraform destroy
```

### Development Setup
```bash
# Copy configuration template
cp terraform.tfvars.example terraform.tfvars

# Populate test data
cd scripts
python3 populate_test_data.py
```

### AWS CLI Requirements
```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

## Code Standards
- Python functions use logging for CloudWatch integration
- Terraform resources follow naming convention: `{environment}-saltware-{resource}`
- All sensitive variables marked with `sensitive = true`
- Korean language support in user-facing messages
- Error handling with graceful fallbacks in Lambda functions