# 🏥 BBB Medical LLM Mock Data Testing

This document explains how to test LLM services using the `data/intake/mock_patient.json` file.

## 📁 Mock Data Files

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

## 🧪 Test Scripts

### 1. `test_llm_mock.py` - Full functionality test
```bash
python test_llm_mock.py
```

**Features:**
- ✅ Mock data loading
- ✅ LLM summary generation
- ✅ Medical analysis
- ✅ Entity extraction
- ✅ Chat completion
- ✅ Multiple scenario testing

**Output Example:**
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

### 2. `test_simple_mock.py` - Simple test
```bash
python test_simple_mock.py
```

**Features:**
- ✅ Quick mock data testing
- ✅ Basic summary generation
- ✅ Core flag verification

### 3. `test_api_mock.py` - API endpoint test
```bash
python test_api_mock.py
```

**Features:**
- ✅ `/api/v1/summary` endpoint testing
- ✅ `/api/v1/evidence` endpoint testing
- ✅ HTTP response validation

## 🎯 Test Scenarios

### Scenario 1: Acute Chest Pain (High Urgency)
```json
{
    "Q1_When_did_the_pain_start": "Just now (within the last hour)",
    "Q2_Where_is_the_pain": ["Middle of chest"],
    "Q3_Pain_character": ["Pressure or squeezing"],
    "Q9_Severity_0_10": "8–10 (very severe / worst ever)"
}
```
**Expected Result:** `ischemic_features: true` 🚨

### Scenario 2: Chronic Chest Pain (Moderate Urgency)
```json
{
    "Q1_When_did_the_pain_start": "Several days ago",
    "Q3_Pain_character": ["Sharp or stabbing"],
    "Q9_Severity_0_10": "3–5 (moderate)"
}
```
**Expected Result:** `ischemic_features: false` 🟡

## 🔧 Usage

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables (if needed)
export OPENAI_API_KEY="your-api-key"
```

### Basic Test Execution
```bash
# Full functionality test
python test_llm_mock.py

# Simple test
python test_simple_mock.py

# API test
python test_api_mock.py
```

## 📊 Expected Results

### Mock Patient Data Analysis Results:
- **HPI**: Detailed medical record of chest pain symptoms
- **ROS**: Cardiovascular, respiratory, constitutional symptom review
- **Clinical Flags**:
  - `ischemic_features: true` (ischemic features)
  - `dm_followup: false` (no diabetes follow-up needed)
  - `labs_a1c_needed: false` (no A1C test needed)

## 🚀 Extensibility

### Additional Mock Data Generation
1. Create `data/intake/mock_patient_*.json` files
2. Add various medical scenarios
3. Auto-load in test scripts

### Add Test Cases
1. Patient data across various age groups
2. Various symptom combinations
3. Emergency situation simulation

## 🔍 Debugging

### Check Logs
```bash
# Run with detailed logs
PYTHONPATH=. python test_llm_mock.py
```

### Clear Cache
```python
from api.services.llm.client import clear_cache
clear_cache()
```

### Check API Key
```python
from api.core.config import settings
print(f"API Key: {settings.OPENAI_API_KEY[:10]}...")
```

## 📝 Notes

1. **API Key**: OpenAI API key is required
2. **Network**: Internet connection is required
3. **Cost**: API calls may incur costs
4. **Caching**: Cache may persist between tests

## 🎉 Successful Test Results

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

Now you can safely and effectively test LLM services using the `data/intake/mock_patient.json` file! 🏥✨
