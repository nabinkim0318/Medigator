# Development guide

This guide covers development setup and workflows for Medigator.

## 🚀 Quick Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker (optional)
- Git

### Initial Setup
```bash
# Clone repository
git clone https://github.com/nabinkim0318/Medigator.git
cd Medigator

# One-time setup
make setup

# Start development servers
make dev
# API: http://localhost:8082
# UI:  http://localhost:3000
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
# Access: http://localhost:3000
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

#### 3. Canonical Docker demo
```bash
make docker-up
# API: http://localhost:8082
# UI:  http://localhost:3000
```

This is the reproducibility-gated path. `make docker-up-separate` is an
optional two-frontend demo and is not part of that gate.

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

## Docker development

`docker/docker-compose.yml` is the canonical local containerized
research-prototype workflow. The API publishes 8082:8082 and the Next.js
development/demo frontend publishes 3000:3000. The build context is the
repository root. It is not a production image or deployment.

```bash
make docker-build
make docker-up
make docker-smoke
make docker-down
```

Compose mounts `data/` writable at `/app/data`, so
`data/medigator.db` persists across container restarts. `rag_index/` is
read-only. `logs/` and `reports/` are writable generated output. RAG is
disabled and OpenAI is not required for startup or smoke verification.

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
- **Docker Logs**: `make docker-logs`

## 📊 Performance

### Optimization Tips
- Use `--turbopack` for faster Next.js development
- Docker layer caching may reduce repeat build time

### Monitoring
- Health checks: `GET /health`
- API metrics: Available in logs
- Frontend performance: Browser dev tools

## Deployment status

No production or staging deployment target is configured or verified. The
Docker files support only the documented local/demo workflow.

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
