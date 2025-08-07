# IVR Story 1: 기본 환영 및 메뉴 시스템 (임시 주석 처리)
resource "aws_connect_contact_flow" "ivr_story_1" {
  instance_id = aws_connect_instance.saltware_contact_center.id
  name        = "Saltware IVR Story 1"
  description = "기본 환영 및 메뉴 시스템"
  type        = "CONTACT_FLOW"

  content = templatefile("${path.module}/contact_flows/ivr-story-1.json", {
    engineer_queue_id = aws_connect_queue.engineer_queue.queue_id
  })

  tags = {
    Name = "IVR Story 1"
    Story = "Basic Welcome and Menu"
  }
}

# Main Entry Contact Flow - 초기 접수 및 업무시간 확인
resource "aws_connect_contact_flow" "main_entry_flow" {
  instance_id = aws_connect_instance.saltware_contact_center.id
  name        = "Saltware Main Entry Flow"
  description = "초기 접수 및 업무시간 확인 후 적절한 Flow로 라우팅"
  type        = "CONTACT_FLOW"

  content = templatefile("${path.module}/contact_flows/main_entry_flow.json", {
    aws_account_id = data.aws_caller_identity.current.account_id
    environment = var.environment
    customer_auth_flow_id = "placeholder-customer-auth-flow-id"
    after_hours_flow_id = "placeholder-after-hours-flow-id"
    general_queue_id = aws_connect_queue.general_queue.queue_id
  })

  tags = {
    Name = "Main Entry Flow"
    Purpose = "Initial routing and business hours check"
  }
}

# 기존 간단한 테스트 플로우 (백업용)
resource "aws_connect_contact_flow" "test_flow" {
  instance_id = aws_connect_instance.saltware_contact_center.id
  name        = "Saltware Test Flow"
  description = "간단한 테스트 플로우"
  type        = "CONTACT_FLOW"

  content = file("${path.module}/contact_flows/main_ivr.json")

  tags = {
    Name = "Test Flow"
  }
}
