# DynamoDB Tables for Saltware IVR System

# Customer Information Table
resource "aws_dynamodb_table" "customers" {
  name           = "${var.environment}-saltware-customers"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "customer_id"

  attribute {
    name = "customer_id"
    type = "S"
  }

  attribute {
    name = "company_name"
    type = "S"
  }

  attribute {
    name = "aws_account_id"
    type = "S"
  }

  # GSI for company name lookup
  global_secondary_index {
    name            = "CompanyNameIndex"
    hash_key        = "company_name"
    projection_type = "ALL"
  }

  # GSI for AWS Account ID lookup
  global_secondary_index {
    name            = "AwsAccountIdIndex"
    hash_key        = "aws_account_id"
    projection_type = "ALL"
  }

  tags = {
    Name        = "${var.environment}-saltware-customers"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}
# Call Log Table
resource "aws_dynamodb_table" "call_logs" {
  name           = "${var.environment}-saltware-call-logs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "call_id"

  attribute {
    name = "call_id"
    type = "S"
  }

  attribute {
    name = "customer_id"
    type = "S"
  }

  attribute {
    name = "call_start_time"
    type = "S"
  }

  # GSI for customer-based queries
  global_secondary_index {
    name            = "CustomerCallsIndex"
    hash_key        = "customer_id"
    range_key       = "call_start_time"
    projection_type = "ALL"
  }

  # TTL configuration for automatic log cleanup (90 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name        = "${var.environment}-saltware-call-logs"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}# Engineer Information Table
resource "aws_dynamodb_table" "engineers" {
  name           = "${var.environment}-saltware-engineers"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "engineer_id"

  attribute {
    name = "engineer_id"
    type = "S"
  }

  attribute {
    name = "part"
    type = "S"
  }

  attribute {
    name = "is_available"
    type = "S"
  }

  # GSI for part-based queries
  global_secondary_index {
    name            = "PartIndex"
    hash_key        = "part"
    projection_type = "ALL"
  }

  # GSI for availability queries
  global_secondary_index {
    name            = "AvailabilityIndex"
    hash_key        = "is_available"
    projection_type = "ALL"
  }

  tags = {
    Name        = "${var.environment}-saltware-engineers"
    Environment = var.environment
    Project     = "Saltware-IVR"
  }
}