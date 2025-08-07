# Project Structure

## Root Directory Organization

### Terraform Configuration Files
- `main.tf` - Provider configuration and backend setup
- `variables.tf` - Input variables with defaults and descriptions
- `outputs.tf` - Output values for deployed resources
- `terraform.tfvars` - Environment-specific variable values (gitignored)
- `terraform.tfvars.example` - Template for configuration

### Infrastructure Modules
```
modules/
├── connect/                # Amazon Connect infrastructure
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ai-services/           # AI services (Lex, Transcribe, etc.)
├── vector-db/             # Vector database setup
├── monitoring/            # CloudWatch, dashboards
└── security/              # IAM, VPC, security groups
```

### Resource-Specific Terraform Files
- `connect.tf` - Amazon Connect instance and configuration
- `ai-services.tf` - Lex, Transcribe, Polly, Comprehend, Kendra
- `lambda.tf` - AI processing Lambda functions
- `vector-db.tf` - OpenSearch/Pinecone vector database
- `flows.tf` - Amazon Connect contact flows
- `integration.tf` - External system integrations (CRM, Oracle DB)
- `monitoring.tf` - CloudWatch dashboards, alarms, and metrics
- `security.tf` - IAM roles, policies, and security configurations

### Application Code
```
lambda/
├── genai-response/        # GenAI response generation
│   ├── handler.py
│   ├── requirements.txt
│   └── utils/
├── stt-processor/         # Real-time STT processing
├── emotion-analyzer/      # Sentiment analysis
├── knowledge-search/      # Vector DB search
├── crm-integration/       # External system integration
└── shared/                # Common utilities and libraries
    ├── auth.py
    ├── logging.py
    └── models.py
```

### Contact Flow Definitions
```
contact_flows/
├── ai-voice-bot.json      # Main AI voice bot flow
├── stt-genai-flow.json    # STT + GenAI processing flow
├── emotion-routing.json   # Emotion-based routing
├── knowledge-search.json  # Knowledge search flow
├── agent-handoff.json     # Agent handoff flow
└── after-hours.json       # After hours handling
```

### Frontend Applications
```
frontend/
├── agent-dashboard/       # React-based agent workstation
│   ├── src/
│   ├── public/
│   └── package.json
├── admin-console/         # Management console
└── knowledge-manager/     # Knowledge base management
```

### Data & Configuration
```
data/
├── knowledge-base/        # Initial knowledge documents
│   ├── faq/
│   ├── policies/
│   └── procedures/
├── training-data/         # AI model training data
└── test-data/             # Test datasets
```

### Utility Scripts
```
scripts/
├── setup/
│   ├── init-knowledge-base.py    # Initialize vector DB
│   ├── populate-test-data.py     # Test data setup
│   └── configure-ai-models.py    # AI model configuration
├── deployment/
│   ├── deploy-by-phase.sh        # Phased deployment
│   └── health-check.py           # Post-deployment validation
└── maintenance/
    ├── backup-data.py            # Data backup
    └── performance-tuning.py     # Performance optimization
```

### Documentation
- `README.md` - Main project documentation (Korean)
- `ARCHITECTURE.md` - System architecture guide
- `DEPLOYMENT.md` - Deployment procedures
- `API.md` - API documentation
- `TROUBLESHOOTING.md` - Common issues and solutions
- `scenario.md` - Business requirements and scenarios

### Configuration Files
- `.github/workflows/` - CI/CD pipeline definitions
- `docker-compose.yml` - Local development environment
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

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