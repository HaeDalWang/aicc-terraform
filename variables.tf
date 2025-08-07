variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"  # 서울 리전
}

variable "environment" {
  description = "환경 (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "connect_instance_alias" {
  description = "Connect 인스턴스 별칭"
  type        = string
  default     = "saltware-contact-center"
}

variable "engineer_username" {
  description = "엔지니어 사용자명"
  type        = string
  default     = "engineer1"
}

variable "engineer_password" {
  description = "엔지니어 초기 비밀번호"
  type        = string
  sensitive   = true
}

variable "engineer_first_name" {
  description = "엔지니어 이름"
  type        = string
  default     = "김"
}

variable "engineer_last_name" {
  description = "엔지니어 성"
  type        = string
  default     = "엔지니어"
}

variable "engineer_email" {
  description = "엔지니어 이메일"
  type        = string
}

variable "company_name" {
  description = "회사명"
  type        = string
  default     = "Saltware"
}

variable "alert_email" {
  description = "알림을 받을 이메일 주소"
  type        = string
  default     = ""
}

# 관리자 계정 변수들
variable "admin_username" {
  description = "관리자 사용자명"
  type        = string
  default     = "admin"
}

variable "admin_password" {
  description = "관리자 초기 비밀번호"
  type        = string
  sensitive   = true
}

variable "admin_first_name" {
  description = "관리자 이름"
  type        = string
  default     = "관리자"
}

variable "admin_last_name" {
  description = "관리자 성"
  type        = string
  default     = "Saltware"
}

variable "admin_email" {
  description = "관리자 이메일"
  type        = string
}