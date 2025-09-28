# ====== Variables ======
PY := $(PWD)/venv/bin/python
PIP := $(PWD)/venv/bin/pip
UVICORN := $(PWD)/venv/bin/uvicorn
PRECOMMIT := $(PWD)/venv/bin/pre-commit
ROOT := $(PWD)

API_DIR := api
APP_DIR := .  # Next.js is at root level
DB_URL := sqlite:///$(API_DIR)/copilot.db

# ====== Phony ======
.PHONY: help setup venv deps ui-deps seed dev api ui test lint fmt type precommit ci \
        build-frontend build-backend build pdf demo-clean clean distclean \
        docker-build docker-up docker-down docker-logs docker-shell test-hardening \
        test-llm test-api

help:
	@echo "Targets:"
	@echo "  setup          Create venv, install deps, seed DB, install UI deps"
	@echo "  dev            Run API (8082) + UI (5173) together"
	@echo "  api            Run FastAPI locally (reload)"
	@echo "  ui             Run Next.js dev server"
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
	@echo "  docker-build   Build Docker images"
	@echo "  docker-up      Start services with Docker Compose"
	@echo "  docker-down    Stop Docker services"
	@echo "  docker-logs    Show Docker logs"
	@echo "  docker-shell   Open shell in running container"
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
	@echo "ℹ️  Starting UI  : http://localhost:5173"
	@( cd $(API_DIR) && $(PY) -m uvicorn main:app --reload --port 8082 ) & \
	( npm run dev )
	@echo "⛔ Stopped dev."

api:
	@cd $(API_DIR) && $(PY) -m uvicorn main:app --reload --port 8082

ui:
	@npm run dev

# ====== Quality ======
test:
	@cd $(ROOT) && PYTHONPATH=$(ROOT) $(PY) -m pytest api/tests -k "not trio" -v

lint:
	@cd $(API_DIR) && ruff check --fix .
	@npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

fmt:
	@cd $(API_DIR) && isort . && black .
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

# ====== Docker ======
docker-build:
	@echo "🐳 Building Docker images..."
	@docker build -t bbb-medical-api .
	@docker build -f Dockerfile.frontend -t bbb-medical-frontend .
	@echo "✅ Docker images built."

docker-up:
	@echo "🐳 Starting services with Docker Compose..."
	@docker-compose up -d
	@echo "✅ Services started. API: http://localhost:8082, UI: http://localhost:5173"

docker-down:
	@echo "🐳 Stopping Docker services..."
	@docker-compose down
	@echo "✅ Services stopped."

docker-logs:
	@docker-compose logs -f

docker-shell:
	@docker-compose exec api bash

# ====== Housekeeping ======
demo-clean:
	@find $(API_DIR) -name "*.db" -delete || true
	@rm -rf $(API_DIR)/reports/* || true
	@echo "🧹 Cleaned DB and reports."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + || true
	@rm -rf $(API_DIR)/.pytest_cache $(API_DIR)/.mypy_cache $(API_DIR)/.ruff_cache || true
	@rm -rf dist .next .vite .cache || true
	@echo "🧹 Cleaned caches and build artifacts."

distclean: clean
	@rm -rf venv || true
	@rm -rf node_modules || true
	@echo "🗑️  Removed venv and node_modules."
