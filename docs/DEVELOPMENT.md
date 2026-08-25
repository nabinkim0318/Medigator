# 🛠️ Development Guide

This guide covers development setup and workflows for the BBB Medical System.

## 🚀 Quick Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (optional)
- Git

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd BBB

# One-time setup
make setup

# Start development servers
make dev
```

## 🏗️ Architecture Overview

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Patient UI    │    │   Doctor UI     │    │   Backend API   │
│   Port: 3000    │    │   Port: 3001    │    │   Port: 8082    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────────┐
                    │ SQLite               │
                    │ data/medigator.db    │
                    └──────────────────────┘
```

### Persistence

Local research-prototype persistence is **SQLite only**. There is one runtime
database:

- **Path**: `data/medigator.db` (repository-relative; gitignored)
- **Config**: `DB_URL` / `settings.db_url` (default `sqlite:///data/medigator.db`)
- **Helper**: `api.core.database.connect_db()` / `get_database_path()`
- **Data**: synthetic/demo fixtures only. Not a clinical record store.

Tests override `settings.db_url` to a `tmp_path` SQLite file. Do not point
tests at the repository database.

PostgreSQL is **not** implemented or tested. SQLAlchemy is **not** used;
runtime code uses the stdlib `sqlite3` helper above.

Some prototype routes are `async def` but run synchronous SQLite calls.
Async database scaling is not implemented.

#### Reset / recreate policy

This prototype's local DB is disposable demo state. Old files such as
`copilot.db` and `data/app.db` are **not** migrated. After upgrading, delete
any leftover local DB and recreate:

```bash
# Reset database (historical copilot.db / data/app.db are not read)
rm -f data/medigator.db data/medigator.db-wal data/medigator.db-shm
make seed
```

Importing API modules does not create the SQLite file. The file and parent
directory are created on the first real connection (or `make seed`).
`api.main` still runs startup checks at import; those checks do not create
the database when the file is missing. They may still create `logs/` and
`reports/` directories.

### Development Modes

#### 1. Unified Development (Single Frontend)
```bash
make dev
# Access: http://localhost:5173
```

#### 2. Separate Frontend Development
```bash
# Terminal 1: Backend API
make api

# Terminal 2: Patient Frontend
make ui-patient

# Terminal 3: Doctor Frontend
make ui-doctor
```

#### 3. Docker Development
```bash
# Unified services
make docker-up

# Separate services (recommended)
make docker-up-separate
```

## 🔧 Development Workflow

### Backend Development

#### API Endpoints
- **Health**: `GET /health`
- **RAG**: `POST /rag/query`
- **Summary**: `POST /summary`
- **Evidence**: `GET /evidence`
- **Report**: `POST /report/generate`

#### Key Directories
```
api/
├── core/           # Core functionality
├── routers/        # API endpoints
├── services/       # Business logic
├── middleware/     # Request processing
└── tests/          # Test suite
```

#### Testing
```bash
# Run all tests
make test

# Run specific test categories
make test-hardening
make test-llm
make test-api
```

### Frontend Development

#### Patient Interface (Port 3000)
- Symptom input forms
- Report viewing
- Patient dashboard

#### Doctor Interface (Port 3001)
- Report analysis
- Code generation
- Doctor dashboard

#### Key Directories
```
src/
├── app/
│   ├── page.tsx        # Unified interface
│   ├── patient/        # Patient pages
│   └── doctor/         # Doctor pages
├── components/         # React components
└── lib/               # Utilities
```

### Code Quality

#### Linting and Formatting
```bash
# Run linting
make lint

# Format code
make fmt

# Run pre-commit hooks
make precommit
```

#### Pre-commit Hooks
- **Ruff**: Python linting and formatting
- **Prettier**: Frontend formatting
- **TypeScript**: Type checking

## 🐳 Docker Development

### Service Configuration

#### Unified Services
```yaml
# docker-compose.yml
services:
  api:        # Backend API (8082)
  frontend:   # Single frontend (5173)
```

#### Separate Services
```yaml
# docker-compose-separate.yml
services:
  api:              # Backend API (8082)
  patient-frontend: # Patient UI (3000)
  doctor-frontend:  # Doctor UI (3001)
```

### Docker Commands
```bash
# Build images
make docker-build

# Start services
make docker-up-separate

# View logs
make docker-logs-separate

# Stop services
make docker-down-separate
```

## 🧪 Testing

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **LLM Tests**: Mock and real API testing
- **Hardening Tests**: Security and validation testing

### Test Commands
```bash
# All tests
make test

# Specific test suites
make test-hardening  # Security tests
make test-llm        # LLM functionality
make test-api        # API endpoints
```

### Test Data
- Mock patient data: `data/intake/mock_patient.json`
- Test questions: `data/intake/mock_questions_cp.json`
- RAG test data: `data/rag/`

## 🔍 Debugging

### Common Issues

#### Port Conflicts
```bash
# Check port usage
lsof -i :3000
lsof -i :3001
lsof -i :8082

# Kill processes if needed
kill -9 <PID>
```

#### Docker Issues
```bash
# Clean Docker cache
docker system prune -f

# Rebuild images
make docker-build
```

#### Database Issues
```bash
# Reset database (do not migrate leftover copilot.db / data/app.db)
rm -f data/medigator.db data/medigator.db-wal data/medigator.db-shm
make seed
```

### Logging
- **API Logs**: Check console output
- **Frontend Logs**: Browser developer tools
- **Docker Logs**: `make docker-logs-separate`

## 📊 Performance

### Optimization Tips
- Use `--turbopack` for faster Next.js builds
- Enable Docker layer caching
- Use production builds for testing

### Monitoring
- Health checks: `GET /health`
- API metrics: Available in logs
- Frontend performance: Browser dev tools

## 🚀 Deployment

### Production Setup
```bash
# Build production images
make docker-build

# Start production services
make docker-up-separate
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_key_here
DEMO_ACCESS_CODE=demo123

# Optional
DEMO_MODE=true
HIPAA_MODE=false
```

## 🤝 Contributing

### Development Process
1. Create feature branch
2. Make changes
3. Run tests: `make test`
4. Run linting: `make lint`
5. Commit with pre-commit hooks
6. Submit pull request

### Code Standards
- Follow existing code style
- Add tests for new features
- Update documentation
- Use meaningful commit messages
