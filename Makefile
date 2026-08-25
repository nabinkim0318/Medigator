# ====== Variables ======
PY := $(PWD)/venv/bin/python
PIP := $(PWD)/venv/bin/pip
UVICORN := $(PWD)/venv/bin/uvicorn
PRECOMMIT := $(PWD)/venv/bin/pre-commit
ROOT := $(PWD)

API_DIR := api
APP_DIR := .  # Next.js is at root level
DB_URL := sqlite:///data/medigator.db

COMPOSE := docker compose -f docker/docker-compose.yml
COMPOSE_SEPARATE := docker compose -f docker/docker-compose-separate.yml

# ====== Phony ======
.PHONY: help setup venv deps ui-deps seed dev api ui test lint fmt type precommit ci \
        build-frontend build-backend build pdf demo-clean clean distclean \
        docker-build docker-up docker-down docker-logs docker-shell docker-smoke \
        docker-up-separate docker-down-separate test-hardening test-llm test-api

help:
	@echo "Targets:"
	@echo "  setup          Create venv, install deps, seed DB, install UI deps"
	@echo "  dev            Run API (8082) + UI (3000) together (host venv/npm, not Docker)"
	@echo "  api            Run FastAPI locally (reload)"
	@echo "  ui             Run Next.js dev server (unified)"
	@echo "  ui-patient     Run Patient Frontend on port 3000"
	@echo "  ui-doctor      Run Doctor Frontend on port 3001"
	@echo "  seed           Load CSV/JSON seeds into SQLite"
	@echo "  test           Run backend tests"
	@echo "  test-hardening Run hardening component tests"
	@echo "  test-llm       Run LLM mock data tests"
	@echo "  test-api       Run API endpoint tests"
	@echo "  lint           Ruff lint (auto-fix), Prettier for frontend"
	@echo "  fmt            Black + isort (backend), Prettier (frontend)"
	@echo "  # type           mypy strict type-check (disabled)"
	@echo "  precommit      Run all pre-commit hooks on all files"
	@echo "  ci             Lint + tests (CI quick gate)"
	@echo "  build          Build prod UI + check API import"
	@echo "  pdf            Generate a sample PDF report (api/reports/)"
	@echo "  docker-build   Build canonical local/demo Compose images"
	@echo "  docker-up      Start canonical local/demo Compose (API 8082, UI 3000)"
	@echo "  docker-smoke   Build/start, poll /health, shut down (CI gate)"
	@echo "  docker-up-separate Optional two-app Compose (not the reproducibility gate)"
	@echo "  docker-down    Stop canonical Docker services"
	@echo "  docker-logs    Show Docker logs"
	@echo "  docker-shell   Open shell in the API container"
	@echo "  clean          Remove __pycache__, caches, build artifacts"
	@echo "  distclean      Also remove venv and node_modules"

# ====== Bootstrap ======
setup: venv deps ui-deps seed
	@echo "✅ Setup done."

venv:
	@test -d venv || python3.12 -m venv venv
	@$(PIP) -q install --upgrade pip

deps:
	@$(PIP) -q install -r $(API_DIR)/requirements.txt
	@if [ -f "$(API_DIR)/requirements-dev.txt" ]; then $(PIP) -q install -r $(API_DIR)/requirements-dev.txt; fi
	@echo "DB_URL=$(DB_URL)" > $(API_DIR)/.env  || true
	@echo "✅ Python deps installed."

ui-deps:
	@npm install
	@echo "✅ Frontend deps installed."

seed:
	@$(PY) $(API_DIR)/db/seed.py
	@echo "✅ Seeded SQLite from /data."

# ====== Run ======
dev:
	@echo "ℹ️  Starting API : http://localhost:8082"
	@echo "ℹ️  Starting UI  : http://localhost:3000"
	@( cd $(API_DIR) && $(PY) -m uvicorn main:app --reload --port 8082 ) & \
	( npm run dev )
	@echo "⛔ Stopped dev."

api:
	@cd $(API_DIR) && $(PY) -m uvicorn main:app --reload --port 8082

ui:
	@npm run dev

ui-patient:
	@echo "🏥 Starting Patient Frontend on port 3000..."
	@npm run dev:patient

ui-doctor:
	@echo "👨‍⚕️ Starting Doctor Frontend on port 3001..."
	@npm run dev:doctor

# ====== Quality ======
test:
	@cd $(ROOT) && PYTHONPATH=$(ROOT) $(PY) -m pytest api/tests -k "not trio" -v

lint:
	@cd $(API_DIR) && ruff check --fix .
	@npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

fmt:
	@cd $(API_DIR) && ruff check --fix . && ruff format .
	@npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

# type:
# 	@cd $(API_DIR) && mypy --strict .

precommit:
	@$(PRECOMMIT) run --all-files

precommit-changed:
	@$(PRECOMMIT) run

precommit-fix:
	@$(PRECOMMIT) run --all-files
	@echo "✅ Pre-commit checks completed"

check: precommit
	@echo "✅ All checks passed - ready to commit!"

ci: lint test
	@echo "✅ CI gate passed."

# ====== Testing ======
test-hardening:
	@echo "🔧 Running hardening tests..."
	@cd $(ROOT) && PYTHONPATH=$(ROOT) $(PY) tests/test_hardening.py
	@echo "✅ Hardening tests completed."

test-llm:
	@echo "🤖 Running LLM tests..."
	@cd $(ROOT) && PYTHONPATH=$(ROOT) $(PY) tests/test_api_mock.py
	@echo "✅ LLM tests completed."

test-api:
	@echo "🌐 Running API tests..."
	@cd $(ROOT) && PYTHONPATH=$(ROOT) $(PY) tests/test_api_mock.py
	@echo "✅ API tests completed."

# ====== Build / Artifacts ======
build-frontend:
	@npm run build

build-backend:
	@cd $(API_DIR) && python -c "import importlib; importlib.import_module('main')"
	@echo "✅ API import check OK."

build: build-frontend build-backend
	@echo "✅ Build complete."

# Sample PDF (assumes /report endpoint and demo session exist/seeded)
pdf:
	@mkdir -p $(API_DIR)/reports
	@echo "Generating demo PDF via API…"
	@curl -sSf http://localhost:8082/report/demo/pdf -o $(API_DIR)/reports/demo.pdf || \
	 (echo "API must be running: make api & then re-run make pdf"; exit 1)
	@echo "📄 Saved: $(API_DIR)/reports/demo.pdf"

# ====== Docker (local/demo; repository-root build context) ======
docker-build:
	@echo "Building canonical local/demo images (context = repository root)..."
	@$(COMPOSE) build
	@echo "Images built."

docker-up:
	@echo "Starting local containerized research-prototype workflow..."
	@$(COMPOSE) up --build -d
	@echo "API: http://localhost:8082  Frontend (dev/demo): http://localhost:3000"
	@echo "Verify: curl -sS http://localhost:8082/health"

docker-smoke:
	@chmod +x scripts/docker_smoke.sh
	@./scripts/docker_smoke.sh

docker-up-separate:
	@echo "Optional two-app Compose — not the reproducibility gate."
	@$(COMPOSE_SEPARATE) up --build -d
	@echo "API: http://localhost:8082  Patient: http://localhost:3000  Doctor: http://localhost:3001"

docker-down:
	@echo "Stopping canonical Docker services..."
	@$(COMPOSE) down --remove-orphans
	@echo "Services stopped."

docker-down-separate:
	@echo "Stopping optional separate services..."
	@$(COMPOSE_SEPARATE) down --remove-orphans
	@echo "Services stopped."

docker-logs:
	@$(COMPOSE) logs -f

docker-logs-separate:
	@$(COMPOSE_SEPARATE) logs -f

docker-shell:
	@$(COMPOSE) exec api sh

# ====== Housekeeping ======
demo-clean:
	@rm -f data/medigator.db data/medigator.db-wal data/medigator.db-shm
	@rm -rf reports/* api/reports/* || true
	@echo "Cleaned local SQLite DB and generated reports."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + || true
	@rm -rf $(API_DIR)/.pytest_cache $(API_DIR)/.mypy_cache $(API_DIR)/.ruff_cache || true
	@rm -rf dist .next .vite .cache || true
	@echo "🧹 Cleaned caches and build artifacts."

distclean: clean
	@rm -rf venv || true
	@rm -rf node_modules || true
	@echo "🗑️  Removed venv and node_modules."
