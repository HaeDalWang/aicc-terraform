# OO금융지주 AI 기반 클라우드 컨택센터(AICC) 시스템
# Amazon Connect 기반 인프라 구성

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Provider 설정
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "솔트금융지주-AICC"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Saltware"
    }
  }
}

# 데이터 소스: 현재 AWS 계정 정보
data "aws_caller_identity" "current" {}

# 데이터 소스: 현재 리전 정보
data "aws_region" "current" {}