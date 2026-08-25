# Local container workflow

`docker/docker-compose.yml` is the canonical reproducible demo environment.
It is a local research-prototype workflow, not a production or staging
deployment.

Run from the repository root:

```bash
make docker-up
# or: docker compose -f docker/docker-compose.yml up --build -d
```

| Service | Container port | Host port | Runtime |
| --- | ---: | ---: | --- |
| `api` | 8082 | 8082 | Uvicorn/FastAPI |
| `frontend` | 3000 | 3000 | Next.js development/demo server |

The image build context is the repository root (`..` relative to the Compose
file). Standalone image builds therefore use:

```bash
docker build -f docker/Dockerfile .
docker build -f docker/Dockerfile.frontend .
```

Do not use `cd docker && docker build .`; required `api/`, `src/`, `data/`,
and package files are outside that context.

## Volumes and environment

- `data/` → `/app/data` (writable): canonical SQLite
  `/app/data/medigator.db`, visible on the host as `data/medigator.db`.
- `rag_index/` → `/app/rag_index` (read-only): committed demo fixtures.
- `logs/` → `/app/logs` (writable, generated and gitignored).
- `reports/` → `/app/reports` (writable, generated and gitignored).
- `src/` and `public/` are source bind mounts for the development/demo
  frontend.

Compose sets `DB_URL=sqlite:///data/medigator.db`, `DEMO_MODE=true`,
`SYNTHETIC_DATA_ONLY=true`, and `ENABLE_RAG=false`. `OPENAI_API_KEY` is
optional and is not used by startup or health checks. RAG is disabled so
runtime startup does not download an embedding model.

## Verification

```bash
make docker-smoke
```

The smoke command uses bounded HTTP polling rather than a fixed sleep. It
checks `/health` for HTTP 200 and `status=healthy`, checks the frontend root,
writes synthetic data to SQLite, restarts the API container, verifies the
record remains available, and shuts Compose down with a trap.

The optional `docker/docker-compose-separate.yml` runs patient and doctor
frontends on host ports 3000 and 3001. It is development/demo-only and is not
part of the reproducibility CI gate.
