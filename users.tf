# AWS Connect에서 기본 제공하는 Admin 보안 프로필 사용
data "aws_connect_security_profile" "admin_profile" {
  instance_id = aws_connect_instance.aicc_instance.id
  name        = "Admin"
}
# 참고 Connect 프로필은
# Admin, Agent, CallCenterManager, QualityAnalyst가 있다

# 관리자 라우팅 프로필 생성
resource "aws_connect_routing_profile" "admin_routing" {
  instance_id               = aws_connect_instance.aicc_instance.id
  name                      = "Admin Routing Profile"
  description               = "관리자용 라우팅 프로필"
  default_outbound_queue_id = aws_connect_queue.basic_queue.queue_id

  media_concurrencies {
    channel     = "VOICE"
    concurrency = 1
  }

  queue_configs {
    channel  = "VOICE"
    delay    = 0
    priority = 1
    queue_id = aws_connect_queue.basic_queue.queue_id
  }

  tags = {
    Name = "Admin Routing Profile"
  }
}

# 관리자 사용자 생성
resource "aws_connect_user" "admin_user" {
  instance_id = aws_connect_instance.aicc_instance.id
  name        = var.admin_username
  password    = var.admin_password

  identity_info {
    first_name = var.admin_first_name
    last_name  = var.admin_last_name
    email      = var.admin_email
  }

  security_profile_ids = [
    data.aws_connect_security_profile.admin_profile.security_profile_id
  ]

  phone_config {
    after_contact_work_time_limit = 0
    phone_type                    = "SOFT_PHONE"
  }

  routing_profile_id = aws_connect_routing_profile.admin_routing.routing_profile_id

  tags = {
    Name = "Saltware Admin"
  }
}

