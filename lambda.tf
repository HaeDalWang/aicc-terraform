# AI 응답을 위한 Lambda 함수 IAM 역할
resource "aws_iam_role" "lambda_connect_role" {
  name = "lambda-connect-role"

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
}

resource "aws_iam_role_policy" "lambda_connect_policy" {
  name = "lambda-connect-policy"
  role = aws_iam_role.lambda_connect_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "connect:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda 함수 코드 압축
data "archive_file" "ai_response_zip" {
  type        = "zip"
  output_path = "ai_response.zip"
  source {
    content = templatefile("${path.module}/lambda/ai_response.py", {
      # 필요한 변수들을 여기에 추가
    })
    filename = "index.py"
  }
}

# AI 응답 Lambda 함수
resource "aws_lambda_function" "ai_response" {
  filename      = "ai_response.zip"
  function_name = "saltware-ai-response"
  role          = aws_iam_role.lambda_connect_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"
  timeout       = 30

  depends_on = [data.archive_file.ai_response_zip]

  tags = {
    Name = "Saltware AI Response"
  }
}

# 업무시간 확인 Lambda 함수 코드 압축
data "archive_file" "business_hours_zip" {
  type        = "zip"
  output_path = "business_hours.zip"
  source {
    content = templatefile("${path.module}/lambda/business_hours.py", {
      # 필요한 변수들을 여기에 추가
    })
    filename = "index.py"
  }
}

# 업무시간 확인 Lambda 함수
resource "aws_lambda_function" "business_hours" {
  filename      = "business_hours.zip"
  function_name = "${var.environment}-saltware-business-hours"
  role          = aws_iam_role.lambda_connect_role.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.9"
  timeout       = 10

  depends_on = [data.archive_file.business_hours_zip]

  tags = {
    Name = "Saltware Business Hours Check"
  }
}

# Connect에서 Lambda 함수 호출 권한
resource "aws_lambda_permission" "allow_connect" {
  statement_id  = "AllowExecutionFromConnect"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_response.function_name
  principal     = "connect.amazonaws.com"
  source_arn    = "${aws_connect_instance.saltware_contact_center.arn}/*"
}

# Connect에서 업무시간 확인 Lambda 함수 호출 권한
resource "aws_lambda_permission" "allow_connect_business_hours" {
  statement_id  = "AllowExecutionFromConnect"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.business_hours.function_name
  principal     = "connect.amazonaws.com"
  source_arn    = "${aws_connect_instance.saltware_contact_center.arn}/*"
}