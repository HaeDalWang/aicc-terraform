# Amazon Connect Contact Flows
# OO금융지주 AICC 시스템 - Contact Flow 기본 구성

# 메인 입구 Contact Flow
resource "aws_connect_contact_flow" "main_entry_flow" {
  depends_on  = [aws_connect_instance.aicc_instance, aws_lambda_function.business_hours_check]
  instance_id = aws_connect_instance.aicc_instance.id
  name        = "메인 입구 플로우"
  description = "고객 전화 접수 시 최초 진입 플로우 - 업무시간 체크 및 라우팅"
  type        = "CONTACT_FLOW"

  content = templatefile("${path.module}/contact_flows/main-entry-flow.json", {
    ACCOUNT_ID           = data.aws_caller_identity.current.account_id,
    INSTANCE_ID          = aws_connect_instance.aicc_instance.id,
    PROJECT_NAME         = var.project_name,
    GENERAL_QUEUE_ID     = aws_connect_queue.general_customer_queue.queue_id,
    VIP_QUEUE_ID         = aws_connect_queue.vip_customer_queue.queue_id,
    AFTER_HOURS_QUEUE_ID = aws_connect_queue.after_hours_queue.queue_id
  })

  tags = {
    Name = "${var.project_name}-main-entry-flow"
  }
}

# # 업무시간 외 Contact Flow
# resource "aws_connect_contact_flow" "after_hours_flow" {
#   depends_on  = [aws_connect_instance.aicc_instance]
#   instance_id = aws_connect_instance.aicc_instance.id
#   name        = "업무시간 외 플로우"
#   description = "업무시간 외 고객 응대 플로우"
#   type        = "CONTACT_FLOW"

#   content = replace(
#     replace(
#       replace(
#         replace(
#           file("${path.module}/contact_flows/after-hours-flow.json"),
#           "ACCOUNT_ID", data.aws_caller_identity.current.account_id
#         ),
#         "INSTANCE_ID", aws_connect_instance.aicc_instance.id
#       ),
#       "EMERGENCY_QUEUE_ID", aws_connect_queue.msp_emergency_queue.queue_id
#     ),
#     "AFTER_HOURS_QUEUE_ID", aws_connect_queue.after_hours_queue.queue_id
#   )

#   tags = {
#     Name = "${var.project_name}-after-hours-flow"
#   }
# }

# # 긴급 에스컬레이션 Contact Flow
# resource "aws_connect_contact_flow" "emergency_escalation" {
#   depends_on  = [aws_connect_instance.aicc_instance]
#   instance_id = aws_connect_instance.aicc_instance.id
#   name        = "긴급 에스컬레이션 플로우"
#   description = "긴급 상황 에스컬레이션 처리 플로우"
#   type        = "CONTACT_FLOW"

#   content = jsonencode({
#     "Version" : "2019-10-30",
#     "StartAction" : "emergency-start",
#     "Actions" : [
#       {
#         "Identifier" : "emergency-start",
#         "Type" : "MessageParticipant",
#         "Parameters" : {
#           "Text" : "긴급 상황으로 분류되었습니다. 최우선으로 처리하겠습니다."
#         },
#         "Transitions" : {
#           "NextAction" : "set-emergency-queue"
#         }
#       },
#       {
#         "Identifier" : "set-emergency-queue",
#         "Type" : "SetWorkingQueue",
#         "Parameters" : {
#           "Queue" : aws_connect_queue.msp_emergency_queue.arn
#         },
#         "Transitions" : {
#           "NextAction" : "transfer-to-queue"
#         }
#       },
#       {
#         "Identifier" : "transfer-to-queue",
#         "Type" : "TransferToQueue"
#       }
#     ]
#   })

#   tags = {
#     Name = "${var.project_name}-emergency-escalation-flow"
#   }
# }

# # 관리자 에스컬레이션 Contact Flow
# resource "aws_connect_contact_flow" "supervisor_escalation" {
#   depends_on  = [aws_connect_instance.aicc_instance]
#   instance_id = aws_connect_instance.aicc_instance.id
#   name        = "관리자 에스컬레이션 플로우"
#   description = "관리자 에스컬레이션 처리 플로우"
#   type        = "CONTACT_FLOW"

#   content = jsonencode({
#     "Version" : "2019-10-30",
#     "StartAction" : "supervisor-start",
#     "Actions" : [
#       {
#         "Identifier" : "supervisor-start",
#         "Type" : "MessageParticipant",
#         "Parameters" : {
#           "Text" : "관리자에게 연결하겠습니다. 잠시만 기다려 주세요."
#         },
#         "Transitions" : {
#           "NextAction" : "set-supervisor-queue"
#         }
#       },
#       {
#         "Identifier" : "set-supervisor-queue",
#         "Type" : "SetWorkingQueue",
#         "Parameters" : {
#           "Queue" : aws_connect_queue.msp_emergency_queue.arn
#         },
#         "Transitions" : {
#           "NextAction" : "transfer-to-queue"
#         }
#       },
#       {
#         "Identifier" : "transfer-to-queue",
#         "Type" : "TransferToQueue"
#       }
#     ]
#   })

#   tags = {
#     Name = "${var.project_name}-supervisor-escalation-flow"
#   }
# }
# # 테스트 Contact Flow
# resource "aws_connect_contact_flow" "test_flow" {
#   depends_on  = [aws_connect_instance.aicc_instance]
#   instance_id = aws_connect_instance.aicc_instance.id
#   name        = "테스트 플로우"
#   description = "Contact Flow 기본 구성 테스트용 플로우"
#   type        = "CONTACT_FLOW"

#   content = replace(
#     replace(
#       replace(
#         file("${path.module}/contact_flows/test-flow.json"),
#         "ACCOUNT_ID", data.aws_caller_identity.current.account_id
#       ),
#       "INSTANCE_ID", aws_connect_instance.aicc_instance.id
#     ),
#     "GENERAL_QUEUE_ID", aws_connect_queue.general_customer_queue.queue_id
#   )

#   tags = {
#     Name = "${var.project_name}-test-flow"
#   }
# }