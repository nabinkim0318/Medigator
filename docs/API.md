# 🔌 API Documentation

**Research prototype.** Synthetic/demo data only. Not for diagnosis,
treatment, clinical use, or production. Does **not** claim HIPAA compliance.
This document is a local demo map, not a production OpenAPI contract.

BBB Medical System API endpoints and usage guide.

## 🌐 Base URL

- **Development**: `http://localhost:8082`
- There is no production API host for this research prototype.

## 📋 Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### RAG Query
```http
POST /rag/query
Content-Type: application/json

{
  "query": "chest pain symptoms",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Chest pain evaluation...",
      "score": 0.95,
      "metadata": {
        "source": "guidelines.md",
        "year": 2021
      }
    }
  ]
}
```

### Summary Generation
```http
POST /summary
Content-Type: application/json

{
  "intake_data": {
    "symptoms": ["chest pain", "shortness of breath"],
    "age": 65,
    "gender": "male"
  }
}
```

**Response:**
```json
{
  "summary": {
    "chief_complaint": "Chest pain with shortness of breath",
    "assessment": "Possible cardiac etiology",
    "recommendations": ["ECG", "Troponin", "Chest X-ray"]
  }
}
```

### Evidence Retrieval
```http
GET /evidence?query=chest pain&limit=3
```

**Response:**
```json
{
  "evidence": [
    {
      "title": "Chest Pain Guidelines",
      "content": "Evaluation of chest pain...",
      "relevance_score": 0.92
    }
  ]
}
```

### Report Generation
```http
POST /report/generate
Content-Type: application/json

{
  "patient_data": {
    "name": "John Doe",
    "age": 65,
    "symptoms": ["chest pain"]
  }
}
```

**Response:**
```json
{
  "report_id": "report_123",
  "pdf_url": "/reports/report_123.pdf",
  "status": "generated"
}
```

## 🔧 Frontend Integration

### Patient Interface (Port 3000)
- **Base URL**: `http://localhost:3000`
- **API Endpoint**: `http://localhost:8082`
- **Features**: Symptom input, report viewing

### Doctor Interface (Port 3001)
- **Base URL**: `http://localhost:3001`
- **API Endpoint**: `http://localhost:8082`
- **Features**: Report analysis, code generation

## 🐳 Docker Integration

### Canonical local/demo services
```bash
make docker-up

# Access:
# - API: http://localhost:8082
# - Frontend: http://localhost:3000
```

### Optional separate services
```bash
# Development/demo only; not part of the reproducibility gate
make docker-up-separate

# Access:
# - API: http://localhost:8082
# - Patient: http://localhost:3000
# - Doctor: http://localhost:3001
```

## 🔒 Authentication

### Demo Mode
```bash
# Set environment variable
export DEMO_ACCESS_CODE=demo123
```

### Optional OpenAI API key
```bash
# Only needed for LLM-backed requests, not startup or /health
export OPENAI_API_KEY=<your-local-key>
```

## 📊 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "error_code": "VALIDATION_ERROR"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

## 🧪 Testing

### Test Endpoints
```bash
# Run API tests
make test-api

# Run specific test
pytest api/tests/test_rag.py -v
```

### Mock Data
- **Patient Data**: `data/intake/mock_patient.json`
- **Questions**: `data/intake/mock_questions_cp.json`

## 📈 Performance

### Response Times
- **Health Check**: < 100ms
- **RAG Query**: < 2s
- **Summary**: < 5s
- **Report Generation**: < 10s

### Rate Limits
- **Default**: 100 requests/minute
- **Burst**: 10 requests/second

## 🔍 Monitoring

### Health Checks
```bash
# Check API health
curl http://localhost:8082/health

# Check Docker services
make docker-logs-separate
```

### Logging
- **API Logs**: Console output
- **Docker Logs**: `make docker-logs-separate`
- **Error Logs**: Available in container logs
