# 기본 업무시간 설정
resource "aws_connect_hours_of_operation" "basic_hours" {
  instance_id = aws_connect_instance.aicc_instance.id
  name        = "기본 업무시간"
  description = "평일 업무시간"
  time_zone   = var.business_hours.timezone

  dynamic "config" {
    for_each = var.business_hours.days
    content {
      day = config.value
      end_time {
        hours   = var.business_hours.end_time.hours
        minutes = var.business_hours.end_time.minutes
      }
      start_time {
        hours   = var.business_hours.start_time.hours
        minutes = var.business_hours.start_time.minutes
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-basic-hours"
    Environment = var.environment
  }
}

# 기본 큐 생성
resource "aws_connect_queue" "basic_queue" {
  depends_on           = [aws_connect_instance.aicc_instance]
  instance_id          = aws_connect_instance.aicc_instance.id
  name                 = "기본 큐"
  description          = "기본 고객 문의 큐"
  hours_of_operation_id = aws_connect_hours_of_operation.basic_hours.hours_of_operation_id

  tags = {
    Name        = "${var.project_name}-basic-queue"
    Environment = var.environment
  }
}
