# OO금융지주 AI 기반 클라우드 컨택센터(AICC) 시스템

Amazon Connect를 기반으로 한 차세대 AI 기반 클라우드 컨택센터 시스템입니다. 실시간 STT/TTS, GenAI 응답, 감정 분석, 지식 검색 등 최신 AI 기술을 통합하여 고객 경험을 혁신합니다.

## 🏗️ 시스템 아키텍처

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
                ↓                                    ↓
        상담원 연결                           리포트/통계
```

## 🚀 핵심 기능

### 1. **AI 기반 자동 응답 시스템**
- **실시간 STT**: Amazon Transcribe를 통한 실시간 음성 인식
- **GenAI 응답**: 고객 질의에 대한 AI 기반 즉시 응답
- **TTS 변환**: Amazon Polly를 통한 자연스러운 음성 합성
- **컨텍스트 관리**: 대화 이력 기반 개인화 응답

### 2. **지능형 음성봇 및 챗봇**
- **Amazon Lex**: 자연어 이해 기반 음성봇
- **의도 분석**: 고객 문의 유형 자동 분류
- **멀티채널**: 음성, 웹채팅, 모바일 앱 통합 지원
- **자동 라우팅**: 문의 복잡도에 따른 자동 상담원 연결

### 3. **실시간 감정 분석 및 라우팅**
- **Amazon Comprehend**: 실시간 감정 상태 분석
- **스마트 라우팅**: 감정 상태 기반 최적 상담원 배정
- **에스컬레이션**: 부정적 감정 감지 시 우선 처리
- **실시간 알림**: 관리자 즉시 알림 시스템

### 4. **지식 검색 및 응답 추천**
- **Amazon Kendra**: 엔터프라이즈 검색 엔진
- **Vector DB**: 유사도 기반 지식 검색
- **실시간 추천**: 상담원 화면 응답 추천
- **지식 관리**: 자동 문서 인덱싱 및 업데이트

### 5. **통합 대시보드 및 분석**
- **실시간 모니터링**: Connect Dashboard 커스터마이징
- **상담원 워크스테이션**: 통합 고객 정보 및 AI 지원
- **성과 분석**: AI 성능 지표 및 운영 통계
- **예측 분석**: 통화량 예측 및 리소스 최적화

## 🚀 시스템 구축 방법

### 1. 사전 준비사항
```bash
# AWS CLI 설정 (ap-northeast-2 리전)
aws configure set region ap-northeast-2

# Terraform 설치 확인 (v1.0 이상)
terraform --version

# Python 환경 설정 (Lambda 함수용)
python3 --version
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# 설정 파일 복사 및 수정
cp terraform.tfvars.example terraform.tfvars

# 필수 설정 항목
vi terraform.tfvars
```

**terraform.tfvars 주요 설정:**
```hcl
# 기본 설정
environment = "prod"
aws_region = "ap-northeast-2"
connect_instance_alias = "oo-financial-aicc"

# AI 서비스 설정
enable_transcribe = true
enable_comprehend = true
enable_kendra = true
enable_lex = true

# 외부 시스템 연동
oracle_db_endpoint = "your-oracle-endpoint"
crm_api_endpoint = "your-crm-endpoint"
sms_api_key = "your-sms-api-key"
```

### 3. 단계별 배포

#### Phase 1: 기본 인프라 구축
```bash
terraform init
terraform plan -target=module.connect_infrastructure
terraform apply -target=module.connect_infrastructure
```

#### Phase 2: AI 서비스 배포
```bash
terraform plan -target=module.ai_services
terraform apply -target=module.ai_services
```

#### Phase 3: 통합 시스템 배포
```bash
terraform plan
terraform apply
```

### 4. 초기 데이터 설정
```bash
# 지식 베이스 초기 데이터 업로드
cd scripts
python3 setup_knowledge_base.py

# 테스트 데이터 생성
python3 populate_test_data.py
```

## 📊 시스템 사용법

### 관리자 콘솔
```bash
# 배포 완료 후 출력되는 URL로 접속
echo $(terraform output connect_admin_url)
```
- **실시간 대시보드**: 통화량, 대기시간, AI 성능 지표 모니터링
- **상담원 관리**: 상담원 등록, 권한 설정, 스킬 배정
- **시스템 설정**: 라우팅 규칙, AI 모델 설정, 알림 구성

### 상담원 워크스테이션
```bash
# 상담원 전용 클라이언트 URL
echo $(terraform output agent_client_url)
```
- **통합 고객 정보**: CRM 연동 고객 데이터 실시간 표시
- **AI 지원 기능**: 실시간 STT, 감정 분석, 응답 추천
- **지식 검색**: 실시간 관련 문서 및 FAQ 검색
- **통화 기록**: 자동 요약 및 후속 조치 관리

### 지식 관리 시스템
```bash
# 지식 베이스 관리 콘솔
echo $(terraform output knowledge_management_url)
```
- **문서 업로드**: 자동 인덱싱 및 Vector 임베딩
- **검색 테스트**: 지식 검색 정확도 테스트
- **성능 분석**: 검색 활용도 및 정확도 분석

## 🔧 시스템 커스터마이징

### AI 모델 설정
```python
# lambda/genai_response.py - GenAI 모델 설정
GENAI_CONFIG = {
    "model": "claude-3-sonnet",  # 또는 "gpt-4", "bedrock-titan"
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": "금융 전문 상담원으로서 정확하고 친절하게 답변하세요."
}
```

### Contact Flow 커스터마이징
```json
// contact_flows/ai_voice_bot.json - 음성봇 플로우 수정
{
  "Version": "2019-10-30",
  "StartAction": "ai-greeting",
  "Actions": [
    {
      "Identifier": "ai-greeting",
      "Type": "InvokeLexBot",
      "Parameters": {
        "BotName": "OOFinancial-CustomerBot",
        "BotAlias": "PROD"
      }
    }
  ]
}
```

### Vector DB 최적화
```python
# scripts/optimize_vector_search.py
VECTOR_CONFIG = {
    "embedding_model": "text-embedding-ada-002",
    "vector_dimension": 1536,
    "similarity_threshold": 0.8,
    "max_results": 5
}
```

### 외부 시스템 연동 설정
```python
# lambda/crm_integration.py - CRM 연동 설정
CRM_CONFIG = {
    "endpoint": "https://your-crm-api.com",
    "auth_method": "oauth2",
    "timeout": 30,
    "retry_count": 3
}
```

## 📞 AI 기반 고객 응대 플로우

### 1단계: AI 음성봇 초기 응대
```
고객 전화 → "안녕하세요! OO금융지주 고객센터입니다. 무엇을 도와드릴까요?"
           ↓
    Amazon Lex 음성봇이 자연어로 문의 내용 파악
           ↓
    문의 유형 자동 분류 (계좌, 대출, 카드, 투자 등)
```

### 2단계: 실시간 STT 및 AI 응답
```
고객 음성 → Transcribe 실시간 STT → GenAI 분석 → 즉시 응답 생성
                                              ↓
                                    Polly TTS 음성 변환
                                              ↓
                                        고객에게 음성 응답
```

### 3단계: 감정 분석 기반 라우팅
```
통화 중 감정 분석 → 부정적 감정 감지 → 우선 상담원 연결
                                    ↓
                            경험 많은 상담원 자동 배정
                                    ↓
                              관리자 실시간 알림
```

### 4단계: 지식 검색 및 상담원 지원
```
복잡한 문의 → 상담원 연결 → 실시간 지식 검색 → 추천 답변 제공
                      ↓              ↓
                고객 정보 표시    감정 상태 모니터링
                      ↓              ↓
                통화 내용 기록    CRM 자동 업데이트
```

### 5단계: 사후 처리 및 학습
```
통화 종료 → 자동 요약 생성 → 고객 만족도 분석 → AI 모델 학습 데이터 수집
              ↓                    ↓                    ↓
        후속 조치 알림        성과 지표 업데이트      시스템 성능 개선
```