output "connect_instance_id" {
  description = "Amazon Connect 인스턴스 ID"
  value       = aws_connect_instance.saltware_contact_center.id
}

output "connect_instance_arn" {
  description = "Amazon Connect 인스턴스 ARN"
  value       = aws_connect_instance.saltware_contact_center.arn
}

output "connect_admin_url" {
  description = "Connect 관리자 콘솔 URL"
  value       = "https://${var.connect_instance_alias}.my.connect.aws/connect/home"
}

output "agent_workspace_url" {
  description = "상담원 워크스페이스 URL (엔지니어가 사용)"
  value       = "https://${var.connect_instance_alias}.my.connect.aws/connect/ccp-v2/"
}

output "engineer_username" {
  description = "엔지니어 사용자명"
  value       = aws_connect_user.engineer_user.name
}

output "lambda_function_name" {
  description = "AI 응답 Lambda 함수명"
  value       = aws_lambda_function.ai_response.function_name
}

output "queue_id" {
  description = "엔지니어 큐 ID"
  value       = aws_connect_queue.engineer_queue.queue_id
}

output "admin_username" {
  description = "관리자 사용자명"
  value       = aws_connect_user.admin_user.name
}

output "admin_login_url" {
  description = "관리자 로그인 URL"
  value       = "https://${var.connect_instance_alias}.my.connect.aws/connect/login"
}

# DynamoDB Table Outputs
output "customers_table_name" {
  description = "고객 정보 DynamoDB 테이블명"
  value       = aws_dynamodb_table.customers.name
}

output "customers_table_arn" {
  description = "고객 정보 DynamoDB 테이블 ARN"
  value       = aws_dynamodb_table.customers.arn
}

output "call_logs_table_name" {
  description = "통화 로그 DynamoDB 테이블명"
  value       = aws_dynamodb_table.call_logs.name
}

output "call_logs_table_arn" {
  description = "통화 로그 DynamoDB 테이블 ARN"
  value       = aws_dynamodb_table.call_logs.arn
}

output "engineers_table_name" {
  description = "엔지니어 정보 DynamoDB 테이블명"
  value       = aws_dynamodb_table.engineers.name
}

output "engineers_table_arn" {
  description = "엔지니어 정보 DynamoDB 테이블 ARN"
  value       = aws_dynamodb_table.engineers.arn
}

# IAM Role Outputs
output "lambda_execution_role_arn" {
  description = "Lambda 실행 역할 ARN"
  value       = aws_iam_role.lambda_execution_role.arn
}

output "lambda_execution_role_name" {
  description = "Lambda 실행 역할명"
  value       = aws_iam_role.lambda_execution_role.name
}

# CloudWatch Log Groups
output "cloudwatch_log_groups" {
  description = "생성된 CloudWatch 로그 그룹들"
  value = {
    customer_lookup = aws_cloudwatch_log_group.customer_lookup_logs.name
    business_hours  = aws_cloudwatch_log_group.business_hours_logs.name
    call_logging    = aws_cloudwatch_log_group.call_logging_logs.name
    connect         = aws_cloudwatch_log_group.connect_logs.name
  }
}