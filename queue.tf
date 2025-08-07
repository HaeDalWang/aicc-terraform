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

# 일반 고객 큐
resource "aws_connect_queue" "general_customer_queue" {
  depends_on            = [aws_connect_instance.aicc_instance]
  instance_id           = aws_connect_instance.aicc_instance.id
  name                  = "일반 고객 큐"
  description           = "일반 고객 문의 처리 큐"
  hours_of_operation_id = aws_connect_hours_of_operation.basic_hours.hours_of_operation_id

  tags = {
    Name        = "${var.project_name}-general-customer-queue"
    Environment = var.environment
  }
}

# VIP 큐
resource "aws_connect_queue" "vip_customer_queue" {
  depends_on            = [aws_connect_instance.aicc_instance]
  instance_id           = aws_connect_instance.aicc_instance.id
  name                  = "VIP 큐"
  description           = "VIP 고객 상황 처리 큐"
  hours_of_operation_id = aws_connect_hours_of_operation.basic_hours.hours_of_operation_id

  tags = {
    Name        = "${var.project_name}-vip-customer-queue"
    Environment = var.environment
  }
}

# 업무시간 외 큐
resource "aws_connect_queue" "after_hours_queue" {
  depends_on            = [aws_connect_instance.aicc_instance]
  instance_id           = aws_connect_instance.aicc_instance.id
  name                  = "업무시간 외 큐"
  description           = "업무시간 외 문의 처리 큐"
  hours_of_operation_id = aws_connect_hours_of_operation.basic_hours.hours_of_operation_id

  tags = {
    Name        = "${var.project_name}-after-hours-queue"
    Environment = var.environment
  }
}
