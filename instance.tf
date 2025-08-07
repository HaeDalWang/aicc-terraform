# Connect 인스턴스 생성
resource "aws_connect_instance" "saltware_contact_center" {
  identity_management_type = "CONNECT_MANAGED"
  inbound_calls_enabled    = true
  outbound_calls_enabled   = true
  instance_alias           = var.connect_instance_alias

  tags = {
    Name        = "Saltware Contact Center"
    Environment = var.environment
  }
}

# 운영 시간 설정
resource "aws_connect_hours_of_operation" "business_hours" {
  instance_id = aws_connect_instance.saltware_contact_center.id
  name        = "Business Hours"
  description = "Saltware 운영시간"
  time_zone   = "Asia/Seoul"

  config {
    day = "MONDAY"
    end_time {
      hours   = 18
      minutes = 0
    }
    start_time {
      hours   = 9
      minutes = 0
    }
  }

  config {
    day = "TUESDAY"
    end_time {
      hours   = 18
      minutes = 0
    }
    start_time {
      hours   = 9
      minutes = 0
    }
  }

  config {
    day = "WEDNESDAY"
    end_time {
      hours   = 18
      minutes = 0
    }
    start_time {
      hours   = 9
      minutes = 0
    }
  }

  config {
    day = "THURSDAY"
    end_time {
      hours   = 18
      minutes = 0
    }
    start_time {
      hours   = 9
      minutes = 0
    }
  }

  config {
    day = "FRIDAY"
    end_time {
      hours   = 18
      minutes = 0
    }
    start_time {
      hours   = 9
      minutes = 0
    }
  }

  tags = {
    Name = "Saltware Business Hours"
  }
}

# 기본 큐 생성 (엔지니어 연결용)
resource "aws_connect_queue" "engineer_queue" {
  instance_id           = aws_connect_instance.saltware_contact_center.id
  name                  = "Engineer Queue"
  description           = "전담 엔지니어 연결 큐"
  hours_of_operation_id = aws_connect_hours_of_operation.business_hours.hours_of_operation_id

  tags = {
    Name = "Engineer Queue"
  }
}

# 일반 고객 큐 생성 (폴백용)
resource "aws_connect_queue" "general_queue" {
  instance_id           = aws_connect_instance.saltware_contact_center.id
  name                  = "General Queue"
  description           = "일반 고객 및 폴백 처리 큐"
  hours_of_operation_id = aws_connect_hours_of_operation.business_hours.hours_of_operation_id

  tags = {
    Name = "General Queue"
  }
}