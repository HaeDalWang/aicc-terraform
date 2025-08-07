# IAM Roles and Policies for Saltware IVR System

# Lambda execution role
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.environment}-saltware-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-saltware-lambda-execution-role"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}

# Basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB access policy for Lambda functions
resource "aws_iam_policy" "lambda_dynamodb_policy" {
  name        = "${var.environment}-saltware-lambda-dynamodb-policy"
  description = "Policy for Lambda functions to access DynamoDB tables"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.customers.arn,
          "${aws_dynamodb_table.customers.arn}/index/*",
          aws_dynamodb_table.call_logs.arn,
          "${aws_dynamodb_table.call_logs.arn}/index/*",
          aws_dynamodb_table.engineers.arn,
          "${aws_dynamodb_table.engineers.arn}/index/*"
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-saltware-lambda-dynamodb-policy"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}

# Attach DynamoDB policy to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_dynamodb_policy.arn
}
# CloudWatch Logs policy for Lambda functions
resource "aws_iam_policy" "lambda_cloudwatch_policy" {
  name        = "${var.environment}-saltware-lambda-cloudwatch-policy"
  description = "Policy for Lambda functions to write to CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:*"
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-saltware-lambda-cloudwatch-policy"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}

# Attach CloudWatch policy to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_policy.arn
}