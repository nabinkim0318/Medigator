# 🏥 BBB Medical Report API

[![CI/CD](https://github.com/nabinkim0318/BBB/actions/workflows/ci.yml/badge.svg)](https://github.com/nabinkim0318/BBB/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)](https://www.docker.com/)

AI-powered medical report generation and analysis system with RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and setup
git clone <repository-url>
cd BBB

# Start with Docker
make docker-build
make docker-up

# Access the application
# API: http://localhost:8082
# Frontend: http://localhost:5173
# API Docs: http://localhost:8082/docs
```

### Option 2: Local Development
```bash
# Setup (one-time)
make setup

# Run development servers
make dev

# Access the application
# API: http://localhost:8082
# Frontend: http://localhost:5173
```

## 📋 Prerequisites

### For Docker (Recommended)
- Docker & Docker Compose
- Git

### For Local Development
- Python 3.12+
- Node.js 18+
- Git

## 🛠️ Development

### Available Commands

```bash
# Setup
make setup          # One-time setup
make dev            # Run API + UI together
make api            # Run API only
make ui             # Run UI only

# Docker
make docker-build   # Build Docker images
make docker-up      # Start with Docker
make docker-down    # Stop Docker services
make docker-logs    # View logs
make docker-shell   # Open container shell

# Quality
make test           # Run tests (excludes trio)
make lint           # Lint code
make fmt            # Format code
# make type         # Type checking (disabled)
make precommit      # Run all checks

# Utilities
make pdf            # Generate sample PDF
make clean          # Clean caches
make distclean      # Remove all dependencies
```

## 🏗️ Architecture

```
BBB/
├── api/                    # FastAPI Backend
│   ├── core/              # Core functionality
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── middleware/        # Request/response processing
│   └── tests/             # Backend tests
├── src/                    # Next.js Frontend
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── lib/               # Utilities
├── data/                   # Sample data
├── docs/                   # Documentation
└── scripts/               # Utility scripts
```

## 🔧 Features

### Core Functionality
- **Medical Report Generation**: AI-powered report creation
- **Symptom Analysis**: Intelligent symptom interpretation
- **Code Generation**: Automatic ICD-10/CPT coding
- **Evidence Retrieval**: RAG-based evidence search
- **PDF Export**: Professional report formatting

### Technical Features
- **FastAPI Backend**: High-performance Python API
- **Next.js Frontend**: Modern TypeScript UI with App Router
- **RAG Integration**: FAISS + Sentence Transformers with query expansion
- **HIPAA Compliance**: PHI masking and security
- **Comprehensive Logging**: Structured logging with PHI protection
- **Error Handling**: Global exception management
- **Health Checks**: Application monitoring
- **Docker Support**: Multi-stage builds for production
- **CI/CD Pipeline**: GitHub Actions with automated testing

## 🔒 Security

- **PHI Masking**: Automatic PII/PHI redaction
- **Write Guards**: Demo mode protection
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Comprehensive data validation
- **Security Logging**: Audit trail for sensitive operations

## 📊 API Endpoints

### Core Endpoints
- `POST /api/v1/summary` - Generate medical summary
- `POST /api/v1/evidence` - Retrieve evidence
- `POST /api/v1/codes` - Generate medical codes
- `POST /api/v1/reports` - Create medical reports
- `GET /api/v1/rag/status` - RAG system status

### Health & Monitoring
- `GET /health` - Health check
- `GET /api/v1/llm/health` - LLM service status
- `GET /api/v1/rag/health` - RAG service status

## 🧪 Testing

```bash
# Run all tests (excludes trio tests)
make test

# Run specific test categories
pytest api/tests/test_summary.py
pytest api/tests/test_rag.py
pytest api/tests/test_llm_cache.py

# Run hardening tests
make test-hardening

# Run LLM tests with mock data
make test-llm
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build production image
docker build -t bbb-medical:latest .

# Run production container
docker run -p 8082:8082 \
  -e OPENAI_API_KEY=your_key \
  -e DEMO_ACCESS_CODE=your_code \
  bbb-medical:latest
```

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
DEMO_ACCESS_CODE=your_demo_code
DEMO_MODE=true
HIPAA_MODE=false
enable_rag=true
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.9
LLM_SEED=42
```

## 📈 Performance

- **Response Time**: < 2s for most operations
- **Concurrent Users**: Supports multiple simultaneous requests
- **Memory Usage**: Optimized for production workloads
- **Database**: SQLite for development, PostgreSQL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔧 Recent Updates

### Latest Improvements
- **LLM Hardening**: JSON schema validation, rule engine, normalization
- **RAG Quality**: Query expansion, MMR diversity, metadata extraction
- **Docker Support**: Multi-stage builds, production optimization
- **CI/CD Pipeline**: GitHub Actions with automated testing
- **Test Coverage**: Comprehensive test suite with mock data
- **Security**: Enhanced PHI masking, CORS configuration

### Fixed Issues
- ✅ Trio test failures in CI/CD
- ✅ Docker frontend build path issues
- ✅ Python version consistency (3.12)
- ✅ Type checking and linting errors
- ✅ RAG performance optimization

## 📊 Project Stats

- **Language**: Python 3.12, TypeScript
- **Framework**: FastAPI, Next.js 15.5.4
- **Database**: SQLite (dev), PostgreSQL (prod)
- **AI/ML**: OpenAI GPT-4, Sentence Transformers, FAISS
- **Deployment**: Docker, Vercel, GitHub Actions
- **Security**: HIPAA compliant, PHI masking

## 🎯 Roadmap

- [ ] Enhanced RAG capabilities
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Mobile application
- [ ] Integration with EHR systems
