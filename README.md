# 🏥 BBB Medical Report API

[![CI/CD](https://github.com/nabinkim0318/BBB/actions/workflows/ci.yml/badge.svg)](https://github.com/nabinkim0318/BBB/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)](https://www.docker.com/)

**Research prototype.** Synthetic/demo data only. Not for diagnosis,
treatment, clinical use, or production. Does **not** claim HIPAA compliance.

Demo medical-intake UI with optional RAG helpers. Suggested summaries and
codes are research artifacts, not clinical decisions or automatic coding.

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and setup
git clone <repository-url>
cd BBB

# Start with unified Docker (single frontend)
make docker-build
make docker-up
# Access: API: http://localhost:8082, Frontend: http://localhost:5173

# OR start with separate frontends (local two-app demo)
make docker-build
make docker-up-separate
# Access: API: http://localhost:8082, Patient: http://localhost:3000, Doctor: http://localhost:3001
```

### Option 2: Local Development
```bash
# Setup (one-time)
make setup

# Run unified development server
make dev
# Access: API: http://localhost:8082, Frontend: http://localhost:5173

# OR run separate frontend services
make api &          # Backend API (port 8082)
make ui-patient &   # Patient Frontend (port 3000)
make ui-doctor &    # Doctor Frontend (port 3001)
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
make ui-patient     # Patient Frontend (port 3000)
make ui-doctor      # Doctor Frontend (port 3001)

# Docker
make docker-build   # Build Docker images
make docker-up      # Start unified Docker services
make docker-up-separate # Start separate Docker services
make docker-down    # Stop unified Docker services
make docker-down-separate # Stop separate Docker services
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
├── api/                    # FastAPI Backend (Port 8082)
│   ├── core/              # Core functionality
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── middleware/        # Request/response processing
│   └── tests/             # Backend tests
├── src/                    # Next.js Frontend
│   ├── app/               # App router pages
│   │   ├── page.tsx       # Unified interface (Port 5173)
│   │   ├── patient/       # Patient interface (Port 3000)
│   │   └── doctor/        # Doctor interface (Port 3001)
│   ├── components/        # React components
│   └── lib/               # Utilities
├── docker/                 # Docker configurations
│   ├── Dockerfile         # Backend API
│   ├── Dockerfile.patient # Patient frontend
│   ├── Dockerfile.doctor  # Doctor frontend
│   └── docker-compose*.yml # Service orchestration
├── data/                   # Sample data
├── docs/                   # Documentation
└── scripts/               # Utility scripts
```

## 🔧 Features

### Core Functionality
- **Demo report sketches**: research-prototype text generation, not clinical reports
- **Symptom notes**: demo interpretation helpers, not diagnosis
- **Code suggestions**: optional ICD-10/CPT lookup for the prototype, not automatic coding
- **Evidence retrieval**: RAG search over bundled guideline snippets
- **PDF export**: demo formatting with a research-prototype watermark

### Technical Features
- **FastAPI Backend**: High-performance Python API
- **Next.js Frontend**: Modern TypeScript UI with App Router
- **RAG Integration**: FAISS + Sentence Transformers with query expansion
- **Sanitized logging**: event names/status/paths only (not a HIPAA control)
- **Error Handling**: Global exception management
- **Health Checks**: Application monitoring
- **Docker Support**: Local/demo container builds
- **CI/CD Pipeline**: GitHub Actions with automated testing

## 🔒 Security

This is a **research prototype**, not production security and **not** for
diagnosis, treatment, or clinical use. It does **not** claim HIPAA
compliance. Synthetic/demo data only: `DEMO_MODE` does **not** make real
identifiers safe. See `docs/SECURITY.md`.

- **Synthetic-data guard**: obvious real identifiers are rejected on intake writes
- **Deny-by-default API boundary**: UI routing is not authorization
- **Operator session**: doctor/admin-style reads require `DEMO_ACCESS_CODE`
- **Sanitized logging**: no request bodies, tokens, raw queries, or model output

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

### Docker (local demo)
```bash
# Build image
docker build -t bbb-medical:latest .

# Run container
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
HIPAA_MODE=false   # config flag only; does not mean HIPAA compliance
enable_rag=true
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.9
LLM_SEED=42
```

## 📈 Performance

- **Response Time**: informal local-demo target, not an SLA
- **Concurrent Users**: not sized or promised
- **Database**: SQLite for this prototype (optional Postgres is not a production deployment)

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
- **Separate Frontend Ports**: Patient (3000) and Doctor (3001) interfaces
- **Vercel Deployment**: Separate Vercel projects for Patient and Doctor frontends
- **LLM Hardening**: JSON schema validation, rule engine, normalization
- **RAG Quality**: Query expansion, MMR diversity, metadata extraction
- **Docker Support**: Local/demo container builds
- **CI/CD Pipeline**: GitHub Actions with automated testing
- **Test Coverage**: Comprehensive test suite with mock data
- **Security**: Enhanced PHI masking, CORS configuration

### Fixed Issues
- ✅ Trio test failures in CI/CD
- ✅ Docker frontend build path issues
- ✅ Python version consistency (3.12)
- ✅ Type checking and linting errors
- ✅ RAG performance optimization
- ✅ Docker Compose command compatibility
- ✅ PostCSS configuration for Tailwind CSS
- ✅ Hardcoded file paths in code generation
- ✅ Test type checking issues

## 📊 Project Stats

- **Language**: Python 3.12, TypeScript
- **Framework**: FastAPI, Next.js 15.5.4
- **Database**: SQLite (dev), PostgreSQL (prod)
- **AI/ML**: OpenAI GPT-4, Sentence Transformers, FAISS
- **Deployment**: Docker, Vercel, GitHub Actions
- **Security**: Prototype synthetic-data boundary (not production IAM)

## 🎯 Roadmap

- [ ] Enhanced RAG capabilities
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Mobile application
- [ ] Integration with EHR systems
