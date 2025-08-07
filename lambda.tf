# 업무시간 체크 Lambda 함수 패키징
data "archive_file" "business_hours_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/business-hours-check"
  output_path = "${path.module}/lambda/business-hours-check.zip"
}

# 업무시간 체크 Lambda 함수
resource "aws_lambda_function" "business_hours_check" {
  filename         = data.archive_file.business_hours_lambda.output_path
  function_name    = "${var.project_name}-business-hours-check"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.11"
  timeout          = 10
  source_code_hash = data.archive_file.business_hours_lambda.output_base64sha256

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }

  tags = {
    Name = "${var.project_name}-business-hours-check"
  }
}

# Connect에서 Lambda 함수 호출 권한
resource "aws_lambda_permission" "allow_connect_business_hours" {
  statement_id  = "AllowExecutionFromConnect"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.business_hours_check.function_name
  principal     = "connect.amazonaws.com"
  source_arn    = "${aws_connect_instance.aicc_instance.arn}/*"
}
