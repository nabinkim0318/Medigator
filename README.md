# Medigator research prototype

[![CI/CD](https://github.com/nabinkim0318/Medigator/actions/workflows/ci.yml/badge.svg)](https://github.com/nabinkim0318/Medigator/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.4-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-supported-blue.svg)](https://www.docker.com/)

**Research prototype.** Synthetic/demo data only. Not for diagnosis,
treatment, clinical use, or production. Does **not** claim HIPAA compliance.

Demo medical-intake UI with optional RAG helpers. Suggested summaries and
codes are research artifacts, not clinical decisions or automatic coding.

## Reproducible local demo

This is the one canonical local containerized research-prototype workflow.
It is not a production or staging deployment.

Prerequisites:

- Git
- Docker Desktop or Docker Engine with Compose v2
- `make` and `curl` for the reusable smoke command

From a clean checkout:

```bash
git clone https://github.com/nabinkim0318/Medigator.git
cd Medigator
make docker-up
```

Expected services:

| Service | Container port | Host port | Mode |
| --- | ---: | ---: | --- |
| FastAPI | 8082 | 8082 | local/demo API |
| Next.js | 3000 | 3000 | development/demo server |

Verify and stop:

```bash
curl -sS http://localhost:8082/health
curl -I http://localhost:3000/
make docker-down
```

The equivalent direct command is:

```bash
docker compose -f docker/docker-compose.yml up --build -d
```

Both images use the repository root as their build context. Do not run
`cd docker && docker build .`; the Dockerfiles copy paths from the repository
root.

The API writes the canonical SQLite database to `/app/data/medigator.db`,
bind-mounted at `data/medigator.db` on the host. The `data/` mount is writable.
The committed `rag_index/` fixtures are read-only. `logs/` and `reports/` are
writable generated output.

RAG is disabled in this workflow, so runtime startup does not download an
embedding model. `OPENAI_API_KEY` is optional and empty by default; `/health`
and the Docker smoke do not call OpenAI. All inputs must be synthetic/demo
data. `DEMO_ACCESS_CODE` defaults to `replace-me-locally`; override it in your
shell for local use. These defaults are not production security.

Run the full reusable check:

```bash
make docker-smoke
```

It builds and starts Compose, polls `GET /health` for HTTP 200 and
`status=healthy`, checks the frontend root, performs a synthetic SQLite write,
restarts the API container, verifies the record remains visible, and always
shuts containers down. Existing demo rows in `data/medigator.db` are preserved.

## Optional host development

This path is not the clean-clone Docker reproducibility gate. It requires
Python 3.12 and Node.js 18+:

```bash
make setup
make dev
```

The API is at `http://localhost:8082` and the Next.js development server is at
`http://localhost:3000`.

## 🛠️ Development

### Available Commands

```bash
# Setup
make setup          # One-time setup
make dev            # Run API + UI together
make api            # Run API only
make ui-patient     # Patient Frontend (port 3000)
make ui-doctor      # Doctor Frontend (port 3001)

# Docker (canonical local/demo path)
make docker-build   # Build API and development/demo frontend images
make docker-up      # Start API 8082 + frontend 3000
make docker-smoke   # Full HTTP and persistence smoke
make docker-down

# Optional two-app demo; not part of the reproducibility gate
make docker-up-separate
make docker-down-separate
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
│   │   ├── page.tsx       # Unified demo interface
│   │   ├── patient/       # Patient interface
│   │   └── doctor/        # Doctor interface
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
- **RAG Integration**: FAISS + BM25 over bundled demo snippets (see `docs/RAG.md`)
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

## Environment variables

- `DB_URL`: fixed to `sqlite:///data/medigator.db` by canonical Compose.
- `DEMO_MODE=true` and `SYNTHETIC_DATA_ONLY=true`: synthetic demo boundary.
- `DEMO_ACCESS_CODE`: optional local override; shared demo password only.
- `OPENAI_API_KEY`: optional; not needed for startup or smoke.
- `ENABLE_RAG=false`: avoids model/network dependency in canonical Compose.
- `NEXT_PUBLIC_API_URL=http://localhost:8082`: browser-visible API URL.

## 📈 Performance

- **Response Time**: informal local-demo target, not an SLA
- **Concurrent Users**: not sized or promised
- **Database**: SQLite at `data/medigator.db`. PostgreSQL is not implemented or tested.

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
- **Cloud deployment**: no production or staging target is configured or verified
- **LLM Hardening**: JSON schema validation, rule engine, normalization
- **RAG**: chunk-id IR eval (Recall@k / MRR / nDCG@5) on 20 golden queries; MMR is not implemented
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
- **Database**: SQLite at `data/medigator.db` (local research prototype). PostgreSQL is not implemented or tested.
- **AI/ML**: OpenAI GPT-4, Sentence Transformers, FAISS
- **Reproducibility**: local Docker Compose plus GitHub Actions
- **Security**: Prototype synthetic-data boundary (not production IAM)

## 🎯 Roadmap

- [ ] Enhanced RAG capabilities
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Mobile application
- [ ] Integration with EHR systems
