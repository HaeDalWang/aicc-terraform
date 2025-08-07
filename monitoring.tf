# CloudWatch Log Groups for Saltware IVR System

# Log group for customer lookup Lambda function
resource "aws_cloudwatch_log_group" "customer_lookup_logs" {
  name              = "/aws/lambda/${var.environment}-saltware-customer-lookup"
  retention_in_days = 30

  tags = {
    Name        = "${var.environment}-saltware-customer-lookup-logs"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}

# Log group for business hours check Lambda function
resource "aws_cloudwatch_log_group" "business_hours_logs" {
  name              = "/aws/lambda/${var.environment}-saltware-business-hours"
  retention_in_days = 30

  tags = {
    Name        = "${var.environment}-saltware-business-hours-logs"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}

# Log group for call logging Lambda function
resource "aws_cloudwatch_log_group" "call_logging_logs" {
  name              = "/aws/lambda/${var.environment}-saltware-call-logging"
  retention_in_days = 90  # Keep call logs longer for audit purposes

  tags = {
    Name        = "${var.environment}-saltware-call-logging-logs"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}

# Log group for Connect instance
resource "aws_cloudwatch_log_group" "connect_logs" {
  name              = "/aws/connect/${var.connect_instance_alias}"
  retention_in_days = 30

  tags = {
    Name        = "${var.environment}-saltware-connect-logs"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}