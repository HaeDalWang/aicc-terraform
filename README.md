# Saltware AI 기반 콜센터 (Amazon Connect)

Terraform을 사용하여 Amazon Connect 기반의 AI 콜센터를 구축하는 프로젝트입니다.

## 🏗️ 아키텍처

```
고객 전화 → Amazon Connect → IVR 플로우 → AI 응답 (Lambda) → 엔지니어 연결
                                ↓
                        CloudWatch 대시보드 (실시간 모니터링)
```

## 📋 주요 기능

1. **IVR 시스템**: 고객이 번호를 눌러 원하는 서비스 선택
2. **AI 응답**: Lambda 함수를 통한 자동 상품 설명 및 문의 응답
3. **엔지니어 연결**: 상세 상담이 필요한 경우 전담 엔지니어와 연결
4. **실시간 모니터링**: CloudWatch 대시보드로 큐 상태, 통화량 등 모니터링
5. **알림 시스템**: 대기시간 초과시 SNS를 통한 알림

## 🚀 배포 방법

### 1. 사전 준비
```bash
# AWS CLI 설정
aws configure

# Terraform 설치 확인
terraform --version
```

### 2. 설정 파일 준비
```bash
# 설정 파일 복사 및 수정
cp terraform.tfvars.example terraform.tfvars
vi terraform.tfvars
```

### 3. Terraform 배포
```bash
# 초기화
terraform init

# 계획 확인
terraform plan

# 배포
terraform apply
```

## 📊 사용법

### 엔지니어 워크스페이스 접속
배포 완료 후 출력되는 `agent_workspace_url`로 접속하여 상담원 인터페이스 사용

### 관리자 콘솔 접속
`connect_admin_url`로 접속하여 전체 시스템 관리

### 모니터링 대시보드
AWS CloudWatch 콘솔에서 "Saltware-Contact-Center-Dashboard" 확인

## 🔧 커스터마이징

### AI 응답 개선
`lambda/ai_response.py` 파일을 수정하여 더 정교한 AI 응답 구현:
- OpenAI GPT API 연동
- AWS Bedrock 사용
- 자체 ML 모델 연동

### Contact Flow 수정
`contact_flows/main_ivr.json` 파일을 수정하여 통화 플로우 변경

### 모니터링 확장
추가 CloudWatch 메트릭 및 알람 설정

## 📞 통화 플로우

1. **고객 전화 접수**
2. **환영 메시지**: "안녕하세요! Saltware 고객센터입니다..."
3. **메뉴 선택**:
   - 1번: AI 기반 일반 문의 및 상품 설명
   - 2번: 전담 엔지니어 직접 연결
   - 0번: 상담원 연결
4. **AI 응답 후 추가 선택**:
   - 1번: 전담 엔지니어 연결
   - 2번: 통화 종료

## 💰 비용 예상

- Amazon Connect: 사용량 기반 과금
- Lambda: 호출당 과금
- CloudWatch: 로그 및 메트릭 저장량 기반
- SNS: 알림 발송량 기반

월 예상 비용: 약 10-50만원 (통화량에 따라 변동)

## 🔒 보안 고려사항

- 엔지니어 초기 비밀번호는 반드시 변경
- IAM 역할 최소 권한 원칙 적용
- 고객 개인정보 로깅시 암호화 필요
- VPC 내부 배치 고려

## 📝 추가 개발 아이디어

1. **고객 정보 연동**: CRM 시스템과 연동
2. **음성 인식**: Amazon Transcribe 연동
3. **감정 분석**: Amazon Comprehend 활용
4. **다국어 지원**: Amazon Translate 연동
5. **채팅봇 연동**: Amazon Lex 활용

## 🆘 문제 해결

### 전화번호 할당 실패
- AWS Support에 한국 전화번호 할당 요청 필요
- 사업자 등록증 등 서류 준비 필요

### Lambda 함수 오류
- CloudWatch Logs에서 오류 로그 확인
- IAM 권한 설정 확인

### Connect 인스턴스 생성 실패
- 리전별 서비스 가용성 확인
- 계정 한도 확인

## 📞 지원

문의사항이 있으시면 Saltware 기술팀으로 연락주세요!
- 이메일: tech@saltware.co.kr
- 전화: 02-1234-5678