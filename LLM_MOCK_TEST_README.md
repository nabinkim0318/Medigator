# 🏥 BBB Medical LLM Mock Data Testing

This document `data/intake/mock_patient.json` explains 파일을 사용하여 LLM 서비스를 테스트하는 방법을 설명합니다.

## 📁 Mock Data 파일

### `data/intake/mock_patient.json`
```json
{
    "Q1_When_did_the_pain_start": "Earlier today",
    "Q2_Where_is_the_pain": ["Middle of chest", "Spreads to left arm / jaw / neck / back"],
    "Q3_Pain_character": ["Pressure or squeezing", "Tightness / heaviness"],
    "Q4_Worse_with": ["Physical activity", "Stress or anxiety"],
    "Q5_Better_with": ["Rest", "Stopping activity"],
    "Q6_Associated_symptoms": ["Shortness of breath", "Sweating", "Nausea or vomiting"],
    "Q7_Duration": "5–30 minutes",
    "Q8_Frequency": "A few times a week",
    "Q9_Severity_0_10": "6–7 (severe)"
}
```

## 🧪 테스트 스크립트들

### 1. `test_llm_mock.py` - 전체 기능 테스트
```bash
python test_llm_mock.py
```

**기능:**
- ✅ Mock 데이터 로딩
- ✅ LLM 요약 생성
- ✅ 의료 분석
- ✅ 엔티티 추출
- ✅ 채팅 완성
- ✅ 다중 시나리오 테스트

**출력 예시:**
```
🏥 MEDICAL SUMMARY GENERATED FROM MOCK DATA
============================================================

📝 History of Present Illness (HPI):
   Patient reports chest pain that started earlier today, described as pressure or squeezing with tightness and heaviness...

🚩 Clinical Flags:
   Ischemic Features: ✅ YES
   Dm Followup: ❌ NO
   Labs A1C Needed: ❌ NO
```

### 2. `test_simple_mock.py` - 간단한 테스트
```bash
python test_simple_mock.py
```

**기능:**
- ✅ 빠른 Mock 데이터 테스트
- ✅ 기본 요약 생성
- ✅ 핵심 플래그 확인

### 3. `test_api_mock.py` - API 엔드포인트 테스트
```bash
python test_api_mock.py
```

**기능:**
- ✅ `/api/v1/summary` 엔드포인트 테스트
- ✅ `/api/v1/evidence` 엔드포인트 테스트
- ✅ HTTP 응답 검증

## 🎯 테스트 시나리오

### 시나리오 1: 급성 흉통 (High Urgency)
```json
{
    "Q1_When_did_the_pain_start": "Just now (within the last hour)",
    "Q2_Where_is_the_pain": ["Middle of chest"],
    "Q3_Pain_character": ["Pressure or squeezing"],
    "Q9_Severity_0_10": "8–10 (very severe / worst ever)"
}
```
**예상 결과:** `ischemic_features: true` 🚨

### 시나리오 2: 만성 흉통 (Moderate Urgency)
```json
{
    "Q1_When_did_the_pain_start": "Several days ago",
    "Q3_Pain_character": ["Sharp or stabbing"],
    "Q9_Severity_0_10": "3–5 (moderate)"
}
```
**예상 결과:** `ischemic_features: false` 🟡

## 🔧 사용법

### 환경 설정
```bash
# 가상환경 활성화
source venv/bin/activate

# 환경 변수 설정 (필요시)
export OPENAI_API_KEY="your-api-key"
```

### 기본 테스트 실행
```bash
# 전체 기능 테스트
python test_llm_mock.py

# 간단한 테스트
python test_simple_mock.py

# API 테스트
python test_api_mock.py
```

## 📊 예상 결과

### Mock Patient 데이터 분석 결과:
- **HPI**: 흉통 증상의 상세한 의료 기록
- **ROS**: 심혈관, 호흡기, 전신 증상 검토
- **Clinical Flags**:
  - `ischemic_features: true` (허혈성 특징)
  - `dm_followup: false` (당뇨 추적 불필요)
  - `labs_a1c_needed: false` (A1C 검사 불필요)

## 🚀 확장 가능성

### 추가 Mock 데이터 생성
1. `data/intake/mock_patient_*.json` 파일 생성
2. 다양한 의료 시나리오 추가
3. 테스트 스크립트에서 자동 로딩

### 테스트 케이스 추가
1. 다양한 연령대 환자 데이터
2. 다양한 증상 조합
3. 응급 상황 시뮬레이션

## 🔍 디버깅

### 로그 확인
```bash
# 상세 로그와 함께 실행
PYTHONPATH=. python test_llm_mock.py
```

### 캐시 클리어
```python
from api.services.llm.client import clear_cache
clear_cache()
```

### API 키 확인
```python
from api.core.config import settings
print(f"API Key: {settings.OPENAI_API_KEY[:10]}...")
```

## 📝 주의사항

1. **API 키**: OpenAI API 키가 필요합니다
2. **네트워크**: 인터넷 연결이 필요합니다
3. **비용**: API 호출 시 비용이 발생할 수 있습니다
4. **캐싱**: 테스트 간 캐시가 유지될 수 있습니다

## 🎉 성공적인 테스트 결과

```
🎉 All LLM mock data tests completed successfully!

📋 Test Summary:
   ✅ Mock data loading
   ✅ LLM summary generation
   ✅ Medical analysis
   ✅ Entity extraction
   ✅ Chat completion
   ✅ Multiple scenarios
```

이제 `data/intake/mock_patient.json` 파일을 사용하여 LLM 서비스를 안전하고 효과적으로 테스트할 수 있습니다! 🏥✨
