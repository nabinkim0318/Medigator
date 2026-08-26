# Medigator

[![CI](https://github.com/nabinkim0318/Medigator/actions/workflows/ci.yml/badge.svg)](https://github.com/nabinkim0318/Medigator/actions/workflows/ci.yml)

Medigator is a synthetic-data healthcare-AI engineering prototype combining a
structured intake workflow, schema-constrained LLM summarization with a
deterministic template fallback, rule-based ICD suggestions, local CPT
reference lookup, and evidence retrieval. The repository includes
explicit response provenance,
quantitative retrieval evaluation, deny-by-default API boundaries, SQLite
persistence, and a reproducible local Docker demo.

**Research prototype. Synthetic/demo data only. Not for diagnosis, treatment,
clinical use, or production. Does not claim HIPAA compliance.**

Runtime retrieval supports BM25, MiniLM/FAISS vector search, and a 0.6/0.4
hybrid. The demo defaults to BM25 because it performed best on the committed
frozen 20-query/49-chunk evaluation fixture; vector and hybrid modes remain
available for experimentation. This result is fixture-specific and does not
establish that BM25 is generally superior for healthcare or production
retrieval. BM25 lexical expansion is available but defaults off based on the
frozen evaluation. A deterministic CI harness uses TF-IDF as a
dependency-cheap vector surrogate; a separate offline command benchmarks the
actual MiniLM/FAISS runtime path on the same frozen fixture.
Results and limitations are summarized under [Evaluation](#evaluation) and
documented in [docs/RAG.md](docs/RAG.md).

Quick reproduction:

```bash
make docker-up       # API http://localhost:8082; UI http://localhost:3000
make docker-smoke    # HTTP health, frontend, SQLite write/restart/read
```

## What it demonstrates

- FastAPI with a deny-by-default API access boundary
- synthetic-data intake persistence in one configurable SQLite database
- schema-constrained OpenAI summarization with deterministic template fallback
- response provenance labels: `openai`, `fallback`, `rules`, `rag`, and `static`
- CSV rule-based ICD suggestions and local CPT reference lookup
- MiniLM/FAISS, BM25, and 0.6/0.4 hybrid retrieval over a committed demo corpus
- frozen chunk-level IR evaluation: CI TF-IDF/BM25 plus a separate offline MiniLM/FAISS benchmark
- blocking backend, frontend, and container smoke gates in GitHub Actions

## Architecture

```text
Next.js demo UI
       |
       v
FastAPI API ──> SQLite (data/medigator.db, configured by DB_URL)
       |
       +──> OpenAI JSON summary when configured
       |    └──> deterministic template fallback
       +──> local ICD rules + CPT reference lookup
       └──> runtime retrieval: selected mode
            - BM25 (default)
            - MiniLM/FAISS
            - hybrid 0.6/0.4
            + vector expansion + optional BM25 lexical expansion

CI retrieval evaluation (separate, blocking-CI safe):
BM25 + TF-IDF cosine + TF-IDF/BM25 hybrid

Offline runtime benchmark (separate, not CI):
BM25 + MiniLM/FAISS + MiniLM/FAISS+BM25 hybrid
```

TF-IDF is the deterministic CI vector surrogate. MiniLM/FAISS is the runtime
vector benchmark. They are not the same experiment. Runtime RAG is optional
and disabled in the canonical Docker workflow to avoid model downloads. See
[docs/RAG.md](docs/RAG.md).

## Capability status

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| Synthetic intake | Implemented | persisted demo/synthetic inputs only |
| LLM summary | Implemented | OpenAI when configured; deterministic template fallback otherwise |
| Rule-based ICD suggestions | Implemented | local CSV rules; not clinical coding |
| CPT reference lookup | Partial | lookup route exists; `/codes` CPT matching is inactive |
| Evidence retrieval | Implemented | optional local retriever; demo default BM25; vector/hybrid remain available; static cards when disabled/empty |
| Retrieval evaluation | Evaluated with limitations | frozen 20-query/49-chunk fixture; CI TF-IDF surrogate + offline MiniLM/FAISS; not clinical IR |
| Authentication | Demo boundary only | in-memory operator sessions; not production IAM |
| Persistence | Implemented | local SQLite only |
| Docker reproducibility | Verified | clean-worktree local demo workflow |
| PostgreSQL | Unsupported | not implemented or tested |
| Clinical use | Unsupported | research prototype only |
| HIPAA compliance | Not claimed | no compliance assertion or de-identification claim |
| Cloud deployment | Not configured | no staging or production target |

## Implemented capabilities

The frontend provides unified patient and operator demo views. The backend
persists synthetic intake records, produces structured summary objects, adds
deterministic flags and ICD suggestions, and returns evidence cards with
source provenance. Sensitive or unfinished surfaces are denied or return
`501` rather than simulating successful clinical functionality.

Suggested summaries, flags, codes, and evidence are research artifacts. They
are not diagnoses, treatment advice, validated coding, or clinical records.
MMR is not implemented.

## Evaluation

The committed RAG evaluation uses 20 frozen synthetic queries with exact,
graded chunk-ID relevance judgments over a committed 49-chunk corpus. It
reports Recall@1/3/5, MRR, nDCG@5, document-level metrics, and Hit@5. Tests also
verify chunk/file/offset/text-hash provenance and cover instruction-only,
keyword-stuffed, and query-injection retrieval cases.

There are two deliberately different evaluation modes over the same fixture:

- **CI-safe deterministic baseline:** BM25, TF-IDF cosine, and TF-IDF/BM25.
  Fast, no MiniLM download, used in blocking tests.
- **Offline runtime benchmark:** BM25, MiniLM/FAISS, and the actual 0.6/0.4
  MiniLM/FAISS+BM25 hybrid. Model-dependent; not part of blocking CI.

Current committed-fixture snapshot (BM25 expansion off unless noted):

| Retriever | Hit@5 | Recall@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: |
| BM25 | 20/20 | 0.903 | 1.000 | 0.901 |
| TF-IDF surrogate | 20/20 | 0.851 | 1.000 | 0.861 |
| TF-IDF/BM25 hybrid | 20/20 | 0.868 | 1.000 | 0.881 |
| MiniLM/FAISS | 20/20 | 0.759 | 0.902 | 0.765 |
| Runtime MiniLM/FAISS+BM25 hybrid | 20/20 | 0.774 | 1.000 | 0.826 |

TF-IDF = deterministic CI surrogate. MiniLM/FAISS = runtime vector benchmark.
On this small synthetic fixture, lexical BM25 outperforms MiniLM/FAISS, and
the current 0.6/0.4 runtime hybrid does not beat BM25. The application
therefore defaults to `RAG_RETRIEVAL_MODE=bm25`. Vector and hybrid remain
available experimental/evaluation modes. Weights were not tuned against the
fixture. This is an evidence-based default for this repository fixture, not a
general claim about lexical versus semantic retrieval, not clinical IR
validation, and not production retrieval validation.

BM25 expansion variants on the same fixture:

| BM25 variant | Hit@5 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No expansion | 20/20 | 0.402 | 0.758 | 0.903 | 1.000 | 0.901 |
| Legacy Boolean-style expansion | 20/20 | 0.250 | 0.620 | 0.755 | 0.821 | 0.709 |
| Fixed lexical expansion | 20/20 | 0.250 | 0.620 | 0.755 | 0.821 | 0.709 |

The legacy implementation passed generated `AND` / `OR` syntax to a
bag-of-words tokenizer, which treated those words as BM25 terms. The fix emits
bounded, deterministic lexical terms instead. Metrics did not improve on the
unchanged fixture, so the contamination hypothesis does not explain the
measured regression and runtime BM25 expansion now defaults off. Vector-query
expansion is unchanged.

Fixture identity is pinned by SHA-256:

- corpus/source set:
  `7df66ea776b879576f66363f8291390f883e6ccd3029d1b100fdee6c1e0b7d96`
- FAISS index:
  `8e8280e2a45640d1fdaa3bae671d8b666251658ed94f0e0e876d537891c86eeb`
- evaluation queries:
  `dc26206b31b78ef7da9b8fae1e9b84a6617de578c8704910ebbe2cc5aff06409`

All fixture hashes are committed in `data/rag/eval_manifest.json`. Corpus
sources and redistribution caveats are recorded in
[docs/RAG_CORPUS.md](docs/RAG_CORPUS.md).

## Reproducible local demo

Prerequisites are Git, Docker with Compose v2, `make`, and `curl`.

```bash
git clone https://github.com/nabinkim0318/Medigator.git
cd Medigator
make docker-up
```

- API: `http://localhost:8082`
- frontend: `http://localhost:3000` (Next.js development/demo server)
- health: `GET http://localhost:8082/health`
- SQLite: host `data/medigator.db` mounted at `/app/data/medigator.db`

`make docker-smoke` builds and starts Compose, polls health, checks the
frontend, writes a synthetic row, restarts the API, verifies persistence, and
shuts down. The workflow has been executed from a fresh worktree with no local
Python/Node dependencies or pre-existing database; Docker layer cache may
still be used.

RAG is off during this smoke, so no embedding model is downloaded. OpenAI is
optional and neither startup nor smoke calls it. The result is a reproducible
local containerized demo, not a production deployment. Details:
[docker/README.md](docker/README.md).

## Security and data boundary

- Inputs are synthetic/demo only; `DEMO_MODE` does not make real data safe.
- Intake writes reject obvious real-looking identifiers where practical. This
  is not complete de-identification.
- `/api/*` is classified deny-by-default.
- Selected doctor/admin-style reads require a demo operator session.
- Sensitive routes are disabled; unfinished clinical/report routes are denied
  or return `501`.
- Summary-path operational logs use content-free event/status/count fields and
  do not serialize intake payloads, prompts, or raw model output. Request
  logging excludes bodies, tokens, and raw retrieval queries. Handler-level
  identifier redaction remains defense in depth, not complete PHI detection.
- Authentication tokens are not transported in query strings.

The operator-session mechanism is a demo boundary, not production IAM. See
[docs/SECURITY.md](docs/SECURITY.md) for the route and logging model.

## Known limitations and unsupported functionality

- SQLite is the only runtime backend. PostgreSQL and SQLAlchemy are not used.
  Demo database state is disposable; no migration framework is provided.
- `/codes` does not currently activate its loaded CPT rules; CPT values shown
  in the UI are explicitly labeled static placeholders.
- Some async routes perform synchronous SQLite work.
- Runtime MiniLM/FAISS: evaluated on the frozen synthetic/demo fixture; not
  clinical IR validation and not production retrieval validation. On that
  fixture BM25 outperforms MiniLM and the current 0.6/0.4 hybrid, so the demo
  default is BM25. Changing the default does not remove those evaluation
  limits: 20 queries, 49 chunks, synthetic/demo judgments, model/library
  version dependence, and no production retrieval validation.
- The bundled corpus is small; source redistribution status is not
  independently verified. The original 15-vs-14 file count is empty
  `docs/prompts.md` (discovered, zero chunks), not a missing indexed
  guideline. Rebuilds use `data/rag/corpus_sources.json` (14 files) rather
  than scanning every Markdown file under `docs/`.
- Operator sessions are in-memory and intended only for the local demo.
- Frontend ESLint is absent.
- Dependency vulnerability reporting is nonblocking.
- No production/staging deployment target or clinical validation exists.

## Repository structure

```text
api/                 FastAPI backend, services, and tests
src/                 Next.js App Router demo frontend
api/services/rag/    runtime retrieval and evaluation logic
data/rag/            frozen evaluation queries, source allowlist, and hash manifest
docs/rag/            bundled retrieval source summaries
rag_index/           committed 49-chunk demo index
docker/              canonical local container workflow
docs/                API, security, RAG, and development notes
scripts/             smoke and setup utilities
```

## Tests and CI

Blocking GitHub Actions jobs run:

- backend pre-commit hooks, Ruff lint/format checks, and pytest
- frontend TypeScript checking and a Next.js build
- Docker HTTP smoke (API health in CI; the reusable local command also checks
  frontend and persistence)

`dependency-report` uploads the dependency scan and is nonblocking; a green job
does not mean zero vulnerabilities. There is no configured frontend ESLint
gate.

Local equivalents:

```bash
pytest api/tests/ -k "not trio"
ruff check api/
ruff format --check api/
PYTHONPATH=. python -m api.services.rag.eval
npx tsc --noEmit
npm run build
make docker-smoke
```

The MiniLM/FAISS runtime benchmark is optional and local:

```bash
PYTHONPATH=. python -m api.services.rag.eval_runtime
```

It is model-dependent. After `all-MiniLM-L6-v2` is available locally, retrieval
evaluation does not require OpenAI, a clinical service, or a live medical API.
CPU is sufficient. First-time execution may download the model; it is not a
blocking CI job.

## Technical stack

- **Backend:** Python 3.12, FastAPI, Pydantic, SQLite
- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS
- **AI/retrieval:** OpenAI API integration, SentenceTransformers MiniLM,
  FAISS, BM25, scikit-learn TF-IDF evaluation surrogate
- **Infrastructure:** Docker, Docker Compose, GitHub Actions

## Portfolio summary

- Built a healthcare-AI research prototype with FastAPI/Next.js,
  schema-constrained LLM summarization and deterministic fallbacks, BM25 /
  MiniLM/FAISS evidence retrieval with an evidence-driven demo default, frozen
  quantitative IR evaluation, SQLite persistence, Docker reproducibility, and
  CI-enforced checks.
- The deterministic CI baseline uses TF-IDF for dependency-cheap regression
  testing, while a separate offline benchmark evaluates the actual MiniLM/FAISS
  runtime retriever against the same frozen chunk-level relevance judgments.

## Project status

**Status: portfolio/research prototype.** Core remediation covers
access-boundary safety, clinical-claim truthfulness, API provenance, retrieval
evaluation, SQLite persistence, and Docker reproducibility. Remaining
limitations include demo-only operator sessions, synchronous SQLite in some
async routes, no frontend lint gate, nonblocking dependency vulnerability
reporting, inactive `/codes` CPT matching, unclear corpus redistribution
status, no production deployment, and no clinical validation.

This repository is MIT-licensed; see `LICENSE`. That project license does not
establish rights to third-party material summarized in the bundled RAG corpus.
