# 출력
output "main_phone_number" {
  description = "메인 전화번호"
  value       = aws_connect_phone_number.main_number.phone_number
  sensitive   = true
}