# Project Structure

## Root Directory Organization

### Terraform Configuration Files
- `main.tf` - Provider configuration and core setup
- `variables.tf` - Input variables with defaults and descriptions
- `outputs.tf` - Output values for deployed resources
- `terraform.tfvars` - Environment-specific variable values (gitignored)
- `terraform.tfvars.example` - Template for configuration

### Resource-Specific Terraform Files
- `dynamodb.tf` - Customer, call logs, and engineer tables
- `lambda.tf` - AI response Lambda function and IAM roles
- `flows.tf` - Amazon Connect contact flows
- `instance.tf` - Connect instance configuration
- `users.tf` - Connect user management
- `iam.tf` - IAM roles and policies
- `monitoring.tf` - CloudWatch dashboards and alarms

### Application Code
```
lambda/
├── ai_response.py          # Main AI response Lambda function
```

### Contact Flow Definitions
```
contact_flows/
├── main_ivr.json          # Primary IVR flow configuration
├── ivr-story-1.json       # Alternative flow implementation
```

### Utility Scripts
```
scripts/
├── populate_test_data.py   # DynamoDB test data population
```

### Documentation
- `README.md` - Main project documentation (Korean)
- `INFRASTRUCTURE_README.md` - Technical infrastructure guide (English)
- `ivr-story-1.md` - IVR flow documentation
- `coc-basic-task.md` - Call Operations Center procedures

### Generated/Runtime Files
- `.terraform/` - Terraform provider cache and modules
- `terraform.tfstate*` - Terraform state files
- `ai_response.zip` - Lambda deployment package

## Naming Conventions

### Terraform Resources
- Format: `{environment}-saltware-{resource-type}`
- Example: `dev-saltware-customers`, `prod-saltware-lambda-execution-role`

### DynamoDB Tables
- Customers: `{environment}-saltware-customers`
- Call Logs: `{environment}-saltware-call-logs` 
- Engineers: `{environment}-saltware-engineers`

### Lambda Functions
- AI Response: `saltware-ai-response`
- Business Hours: `{environment}-saltware-business-hours`
- Customer Lookup: `{environment}-saltware-customer-lookup`

### CloudWatch Log Groups
- Lambda: `/aws/lambda/{function-name}`
- Connect: `/aws/connect/{instance-alias}`

## File Organization Principles
- Terraform files grouped by AWS service/functionality
- Lambda code in dedicated `lambda/` directory
- Contact flows as JSON in `contact_flows/` directory
- Utility scripts in `scripts/` directory
- Documentation at root level with clear naming