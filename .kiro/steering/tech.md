# Technology Stack

## Infrastructure as Code
- **Terraform**: Primary IaC tool for AWS resource provisioning
- **Provider**: AWS Provider ~> 5.0
- **State Management**: S3 backend with DynamoDB locking
- **Modules**: Modular architecture for reusability

## Core AWS Services
- **Amazon Connect**: Cloud contact center platform
- **Amazon Lex**: Conversational AI and chatbots
- **Amazon Transcribe**: Real-time speech-to-text
- **Amazon Polly**: Text-to-speech synthesis
- **Amazon Comprehend**: Natural language processing and sentiment analysis
- **Amazon Kendra**: Enterprise search service
- **Amazon Bedrock/OpenAI**: Generative AI for responses

## Data & Storage
- **DynamoDB**: Customer data, call logs, conversation history
- **OpenSearch/Pinecone**: Vector database for knowledge search
- **S3**: Document storage, call recordings, model artifacts
- **RDS/Aurora**: Structured data for CRM integration

## Compute & Processing
- **Lambda**: Serverless functions for AI processing
- **ECS/Fargate**: Containerized services for heavy workloads
- **API Gateway**: RESTful APIs for external integrations
- **EventBridge**: Event-driven architecture

## Monitoring & Analytics
- **CloudWatch**: Logging, monitoring, and dashboards
- **X-Ray**: Distributed tracing for performance analysis
- **QuickSight**: Business intelligence and reporting
- **Grafana**: Custom dashboards and visualization

## Security & Compliance
- **IAM**: Role-based access control
- **KMS**: Encryption key management
- **WAF**: Web application firewall
- **VPC**: Network isolation and security
- **Secrets Manager**: Secure credential storage

## Programming Languages & Frameworks
- **Python 3.11**: Lambda functions, AI/ML processing
- **TypeScript/Node.js**: Frontend and API development
- **React**: Web-based agent dashboard
- **HCL**: Terraform infrastructure code
- **SQL**: Database queries and analytics

## Development Environment
- **Region**: ap-northeast-2 (Seoul) - Primary
- **Multi-AZ**: High availability deployment
- **Environment**: dev/staging/prod with automated promotion
- **CI/CD**: GitHub Actions for automated deployment

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