# 🏥 BBB Medical Report API

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
- Python 3.11+
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
make test           # Run tests
make lint           # Lint code
make fmt            # Format code
make type           # Type checking
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
├── app/                    # React Frontend
│   ├── src/               # Source code
│   └── public/            # Static assets
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
- **React Frontend**: Modern TypeScript UI
- **RAG Integration**: FAISS + Sentence Transformers
- **HIPAA Compliance**: PHI masking and security
- **Comprehensive Logging**: Structured logging with PHI protection
- **Error Handling**: Global exception management
- **Health Checks**: Application monitoring

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
# Run all tests
make test

# Run specific test categories
pytest api/tests/test_summary.py
pytest api/tests/test_rag.py
pytest api/tests/test_llm_cache.py
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

## 🎯 Roadmap

- [ ] Enhanced RAG capabilities
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Mobile application
- [ ] Integration with EHR systems
