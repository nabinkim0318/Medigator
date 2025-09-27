# ====== Variables ======
PY := .venv/bin/python
PIP := .venv/bin/pip
UVICORN := .venv/bin/uvicorn
PRECOMMIT := .venv/bin/pre-commit
ROOT := $(PWD)

API_DIR := api
APP_DIR := app
DB_URL := sqlite:///$(API_DIR)/copilot.db

# ====== Phony ======
.PHONY: help setup venv deps ui-deps seed dev api ui test lint fmt type precommit ci \
        build-frontend build-backend build pdf demo-clean clean distclean

help:
	@echo "Targets:"
	@echo "  setup          Create venv, install deps, seed DB, install UI deps"
	@echo "  dev            Run API (8080) + UI (5173) together"
	@echo "  api            Run FastAPI locally (reload)"
	@echo "  ui             Run Vite dev server"
	@echo "  seed           Load CSV/JSON seeds into SQLite"
	@echo "  test           Run backend tests"
	@echo "  lint           Ruff lint (auto-fix), Prettier for frontend"
	@echo "  fmt            Black + isort (backend), Prettier (frontend)"
	@echo "  type           mypy strict type-check"
	@echo "  precommit      Run all pre-commit hooks on all files"
	@echo "  ci             Lint + type + tests (CI quick gate)"
	@echo "  build          Build prod UI + check API import"
	@echo "  pdf            Generate a sample PDF report (api/reports/)"
	@echo "  clean          Remove __pycache__, caches, build artifacts"
	@echo "  distclean      Also remove venv and node_modules"

# ====== Bootstrap ======
setup: venv deps ui-deps seed
	@echo "✅ Setup done."

venv:
	@test -d .venv || python3 -m venv .venv
	@$(PIP) -q install --upgrade pip

deps:
	@$(PIP) -q install -r $(API_DIR)/requirements.txt
	@if [ -f "$(API_DIR)/requirements-dev.txt" ]; then $(PIP) -q install -r $(API_DIR)/requirements-dev.txt; fi
	@echo "DB_URL=$(DB_URL)" > $(API_DIR)/.env  || true
	@echo "✅ Python deps installed."

ui-deps:
	@cd $(APP_DIR) && npm install
	@echo "✅ Frontend deps installed."

seed:
	@$(PY) $(API_DIR)/db/seed.py
	@echo "✅ Seeded SQLite from /data."

# ====== Run ======
dev:
	@echo "ℹ️  Starting API : http://localhost:8080"
	@echo "ℹ️  Starting UI  : http://localhost:5173"
	@( cd $(API_DIR) && $(UVICORN) main:app --reload --port 8080 ) & \
	( cd $(APP_DIR) && npm run dev )
	@echo "⛔ Stopped dev."

api:
	@cd $(API_DIR) && $(UVICORN) main:app --reload --port 8080

ui:
	@cd $(APP_DIR) && npm run dev

# ====== Quality ======
test:
	@cd $(API_DIR) && pytest -q

lint:
	@cd $(API_DIR) && ruff --fix .
	@cd $(APP_DIR) && npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

fmt:
	@cd $(API_DIR) && isort . && black .
	@cd $(APP_DIR) && npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

type:
	@cd $(API_DIR) && mypy --strict .

precommit:
	@$(PRECOMMIT) run --all-files

ci: lint type test
	@echo "✅ CI gate passed."

# ====== Build / Artifacts ======
build-frontend:
	@cd $(APP_DIR) && npm run build

build-backend:
	@cd $(API_DIR) && python -c "import importlib; importlib.import_module('main')"
	@echo "✅ API import check OK."

build: build-frontend build-backend
	@echo "✅ Build complete."

# Sample PDF (assumes /report endpoint and demo session exist/seeded)
pdf:
	@mkdir -p $(API_DIR)/reports
	@echo "Generating demo PDF via API…"
	@curl -sSf http://localhost:8080/report/demo/pdf -o $(API_DIR)/reports/demo.pdf || \
	 (echo "API must be running: make api & then re-run make pdf"; exit 1)
	@echo "📄 Saved: $(API_DIR)/reports/demo.pdf"

# ====== Housekeeping ======
demo-clean:
	@find $(API_DIR) -name "*.db" -delete || true
	@rm -rf $(API_DIR)/reports/* || true
	@echo "🧹 Cleaned DB and reports."

clean:
	@find . -name "__pycache__" -type d -exec rm -rf {} + || true
	@rm -rf $(API_DIR)/.pytest_cache $(API_DIR)/.mypy_cache $(API_DIR)/.ruff_cache || true
	@rm -rf $(APP_DIR)/dist $(APP_DIR)/.vite $(APP_DIR)/.cache || true
	@echo "🧹 Cleaned caches and build artifacts."

distclean: clean
	@rm -rf .venv || true
	@rm -rf $(APP_DIR)/node_modules || true
	@echo "🗑️  Removed venv and node_modules."
