# Amazon Connect 인스턴스 생성
resource "aws_connect_instance" "aicc_instance" {
  identity_management_type      = var.connect_identity_management_type
  inbound_calls_enabled         = var.connect_inbound_calls_enabled
  outbound_calls_enabled        = var.connect_outbound_calls_enabled
  instance_alias                = var.connect_instance_alias
  contact_flow_logs_enabled     = var.connect_contact_flow_logs_enabled
  contact_lens_enabled          = var.connect_contact_lens_enabled
  
  tags = {
    Name        = "${var.project_name}-connect-instance"
    Environment = var.environment
    Project     = "솔트금융지주-AICC"
  }
}