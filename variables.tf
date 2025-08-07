# 변수 정의

variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "environment" {
  description = "환경 (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "프로젝트 명"
  type        = string
  default     = "oo-aicc"
}

variable "connect_instance_alias" {
  description = "Amazon Connect 인스턴스 별칭"
  type        = string
  default     = "salt-financial-aicc"
}

variable "connect_identity_management_type" {
  description = "Connect 사용자 관리 방식"
  type        = string
  default     = "CONNECT_MANAGED"
  validation {
    condition     = contains(["CONNECT_MANAGED", "SAML", "EXISTING_DIRECTORY"], var.connect_identity_management_type)
    error_message = "Identity management type must be CONNECT_MANAGED, SAML, or EXISTING_DIRECTORY."
  }
}

variable "connect_inbound_calls_enabled" {
  description = "인바운드 콜 활성화 여부"
  type        = bool
  default     = true
}

variable "connect_outbound_calls_enabled" {
  description = "아웃바운드 콜 활성화 여부"
  type        = bool
  default     = true
}

variable "connect_contact_flow_logs_enabled" {
  description = "Contact Flow 로그 활성화 여부"
  type        = bool
  default     = true
}

variable "connect_contact_lens_enabled" {
  description = "Contact Lens 활성화 여부"
  type        = bool
  default     = true
}

variable "business_hours" {
  description = "업무 시간 설정"
  type = object({
    timezone = string
    start_time = object({
      hours   = number
      minutes = number
    })
    end_time = object({
      hours   = number
      minutes = number
    })
    days = list(string)
  })
  default = {
    timezone = "Asia/Seoul"
    start_time = {
      hours   = 9
      minutes = 0
    }
    end_time = {
      hours   = 18
      minutes = 0
    }
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
  }
}

variable "phone_number_country_code" {
  description = "전화번호 국가 코드"
  type        = string
  default     = "KR"
}

variable "phone_number_type" {
  description = "전화번호 타입"
  type        = string
  default     = "TOLL_FREE"
  validation {
    condition     = contains(["TOLL_FREE", "DID"], var.phone_number_type)
    error_message = "Phone number type must be TOLL_FREE or DID."
  }
}

variable "admin_email" {
  description = "관리자 이메일"
  type        = string
}

variable "admin_first_name" {
  description = "관리자 이름"
  type        = string

}

variable "admin_last_name" {
  description = "관리자 이름"
  type        = string

}

variable "admin_password" {
  description = "관리자 비밀번호"
  type        = string

}

variable "admin_username" {
  description = "관리자 아이디"
  type        = string
}