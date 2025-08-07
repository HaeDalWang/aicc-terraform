# 전화번호 발급

resource "aws_connect_phone_number" "main_number" {
  depends_on   = [aws_connect_instance.aicc_instance]
  country_code = var.phone_number_country_code
  type         = var.phone_number_type
  target_arn   = aws_connect_instance.aicc_instance.arn
  description  = "솔트 금융지주 AICC 대표 전화번호"

  tags = {
    Name        = "${var.project_name}-main-phone"
    Environment = var.environment
  }
}
