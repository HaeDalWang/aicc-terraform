# OO금융지주 AI 기반 클라우드 컨택센터(AICC) 시스템

Amazon Connect를 기반으로 한 차세대 AI 기반 클라우드 컨택센터 시스템입니다.

## 시스템 개요

- **프로젝트**: OO금융지주 AI 기반 클라우드 컨택센터(AICC) 시스템
- **규모**: 12억원 (부가세 포함)
- **기간**: 5개월 (2024.01 ~ 2024.05)
- **목표**: 온프레미스 → 클라우드 전환, AI 기술 도입, 운영 효율화

## 주요 기능

### 1단계: Amazon Connect 기반 클라우드 인프라 구축 ✅
- [x] Amazon Connect 인스턴스 생성 및 기본 구성
- [x] 고객 유형별 큐 시스템 (MSP 긴급, MSP 일반, VIP, 일반, 업무시간 외)
- [x] 라우팅 프로필 및 우선순위 설정
- [x] IAM 역할 및 보안 정책 구성
- [x] DynamoDB 테이블 (고객, 통화로그, 엔지니어, 대화이력, 지식베이스)
- [x] CloudWatch 모니터링 및 알림 시스템
- [x] VPC 및 네트워크 보안 설정 (프로덕션 환경)

### 2단계: AI 서비스 통합 (예정)
- [ ] 실시간 STT (Amazon Transcribe)
- [ ] GenAI 자동 응답 시스템
- [ ] TTS (Amazon Polly)
- [ ] 감정 분석 (Amazon Comprehend)
- [ ] 음성봇 (Amazon Lex)

### 3단계: 지식 관리 시스템 (예정)
- [ ] Amazon Kendra 지식 검색
- [ ] Vector DB 기반 유사도 검색
- [ ] 상담원 응답 추천 시스템

## 아키텍처

```
고객 전화 → Amazon Connect → AI 음성봇(Lex) → 실시간 STT(Transcribe)
                ↓                                    ↓
        Contact Flow 라우팅                    GenAI 응답 생성
                ↓                                    ↓
        감정 분석(Comprehend)                  TTS 음성 변환(Polly)
                ↓                                    ↓
        지식 검색(Kendra)                     상담원 Dashboard
                ↓                                    ↓
        Vector DB 검색                        CRM/DB 연동
```

## 배포 가이드

### 사전 요구사항

1. **AWS CLI 설정**
   ```bash
   aws configure
   aws sts get-caller-identity
   ```

2. **Terraform 설치**
   ```bash
   # macOS
   brew install terraform
   
   # 버전 확인
   terraform version
   ```

### 배포 단계

1. **설정 파일 준비**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # terraform.tfvars 파일을 실제 환경에 맞게 수정
   ```

2. **Terraform 초기화**
   ```bash
   terraform init
   ```

3. **배포 계획 확인**
   ```bash
   terraform plan
   ```

4. **인프라 배포**
   ```bash
   terraform apply
   ```

### 환경별 배포

#### 개발 환경
```bash
terraform workspace new dev
terraform apply -var="environment=dev"
```

#### 프로덕션 환경
```bash
terraform workspace new prod
terraform apply -var="environment=prod"
```

## 생성되는 리소스

### Amazon Connect
- Connect 인스턴스
- 전화번호 (무료 전화)
- 큐 시스템 (6개 큐)
- 라우팅 프로필 (3개)
- Contact Flow (4개)
- 업무 시간 설정

### 데이터 저장소
- DynamoDB 테이블 (5개)
- S3 버킷 (녹음, 감사로그)
- CloudWatch 로그 그룹

### 보안
- IAM 역할 및 정책
- KMS 암호화 키
- VPC 및 보안 그룹 (프로덕션)
- CloudTrail 감사 로그

### 모니터링
- CloudWatch 대시보드
- 알람 (통화량, 대기시간, 오류율)
- SNS 알림 토픽

## 큐 시스템 구조

| 큐 이름 | 우선순위 | SLA | 대상 고객 |
|---------|----------|-----|-----------|
| MSP 긴급 장애 큐 | 최고 | 15분 | MSP 고객 긴급 상황 |
| MSP 일반 문의 큐 | 높음 | 30분 | MSP 고객 일반 문의 |
| VIP 고객 큐 | 높음 | 30분 | VIP 고객 |
| 일반 고객 큐 | 보통 | 1시간 | 일반 고객 |
| 업무시간 외 큐 | 낮음 | 다음 업무일 | 업무시간 외 문의 |
| 콜백 요청 큐 | 보통 | - | 콜백 요청 |

## 라우팅 프로필

1. **기본 라우팅 프로필**: 모든 큐 처리 가능
2. **MSP 전용 라우팅 프로필**: MSP 고객 전담
3. **시니어 상담원 라우팅 프로필**: 복잡한 문의 및 감정 분석 기반 라우팅

## 보안 설정

### 데이터 암호화
- 모든 DynamoDB 테이블 KMS 암호화
- S3 버킷 서버 사이드 암호화
- 통화 녹음 암호화 저장

### 접근 제어
- IAM 역할 기반 접근 제어
- Connect 보안 프로필
- VPC 및 보안 그룹 (프로덕션)

### 감사 및 모니터링
- CloudTrail 감사 로그
- VPC Flow Logs (프로덕션)
- CloudWatch 메트릭 및 알람

## 모니터링 대시보드

### 주요 지표
- 실시간 통화량
- 큐별 대기시간
- 상담원 가용성
- AI 서비스 성능
- 시스템 오류율

### 알림 설정
- 높은 통화량 감지
- 큐 대기시간 초과 (5분)
- Lambda 함수 오류율 증가
- 시스템 장애 감지

## 다음 구현 단계

1. **AI 서비스 구현**
   - 실시간 STT/TTS 연동
   - GenAI 응답 시스템
   - 감정 분석 및 라우팅

2. **Lambda 함수 개발**
   - AI 처리 로직
   - 고객 조회 및 분류
   - CRM 연동

3. **Amazon Lex 봇 구성**
   - 자연어 이해 모델
   - 의도 분석 및 응답

4. **지식 검색 시스템**
   - Amazon Kendra 설정
   - Vector DB 구축
   - 응답 추천 시스템

5. **상담원 대시보드**
   - 실시간 정보 표시
   - AI 지원 도구
   - CRM 연동 화면

## 문제 해결

### 일반적인 문제

1. **전화번호 할당 실패**
   - AWS Support에 전화번호 할당 요청
   - 리전별 가용성 확인

2. **Connect 인스턴스 생성 실패**
   - 서비스 한도 확인
   - IAM 권한 확인

3. **DynamoDB 테이블 생성 실패**
   - 테이블 이름 중복 확인
   - 리전별 서비스 가용성 확인

### 로그 확인

```bash
# CloudWatch 로그 확인
aws logs describe-log-groups --log-group-name-prefix "/aws/connect"

# Terraform 상태 확인
terraform show
terraform state list
```

## 지원 및 문의

- **개발팀**: Saltware 개발팀
- **프로젝트 관리**: OO금융지주 IT팀
- **기술 지원**: AWS Support (Business/Enterprise)

## 라이선스

이 프로젝트는 OO금융지주의 소유이며, 상업적 목적으로 사용됩니다.