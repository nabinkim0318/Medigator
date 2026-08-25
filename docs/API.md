# Medigator API boundary

**Research prototype.** Synthetic/demo data only. Not for diagnosis,
treatment, clinical use, or production. Does **not** claim HIPAA compliance.
This is a local demo map, not a production API contract.

- Base URL: `http://localhost:8082`
- OpenAPI: `http://localhost:8082/docs`
- Health: `GET /health`
- No production API host is configured.

The middleware classifies `/api/*` deny-by-default. A route appearing in
OpenAPI does not mean that the security boundary permits it.

## Implemented demo surfaces

| Access | Method and path | Behavior |
| --- | --- | --- |
| Public | `GET /health` | process/config health response |
| Demo-open | `POST /api/v1/patient/profile` | persist synthetic profile intake |
| Demo-open | `POST /api/v1/patient/appointment` | persist synthetic appointment intake |
| Demo-open | `POST /api/v1/summary` | structured summary with `openai` or `fallback` provenance |
| Demo-open | `POST /api/v1/codes` | CSV-based ICD suggestions with `rules` provenance; CPT matcher currently returns no rule matches |
| Demo-open | `POST /api/v1/evidence` | RAG or static evidence cards with provenance |
| Demo-open | `GET /api/v1/rag/status` | optional retriever status |
| Demo-open | `POST /api/v1/rag/search` | search committed demo snippets when RAG is enabled |
| Demo-open | `GET /api/v1/llm/health` | LLM integration status |
| Demo-open | `GET /api/v1/reports/health` | report-router health |
| Demo-open | `GET /api/v1/reports/rules` | local rule metadata |
| Demo-open | `GET /api/v1/reports/symptoms/{symptom}/icd` | local ICD lookup response |
| Demo-open | `GET /api/v1/reports/conditions/{condition}/cpt` | local CPT lookup response |

Response provenance uses the sources `openai`, `fallback`, `rules`, `rag`, and
`static`. These labels identify the implementation path; they do not establish
medical correctness.

## Demo operator boundary

Selected profile reads/deletes, statistics, and analytics dashboard/trend
routes require an in-memory operator session:

```http
POST /api/v1/auth/demo-operator
Content-Type: application/json

{"access_code": "<DEMO_ACCESS_CODE>"}
```

Send the returned token as:

```http
Authorization: Bearer <operator_session>
```

Sessions are random, process-local, expire after eight hours, and disappear on
restart. The shared access code and operator session are a demo boundary, not
production IAM.

## Disabled and unimplemented surfaces

- Username-derived login is disabled.
- File, notification, patient-token path reads/updates, search/export, and RAG
  index mutation are disabled with `403`.
- Unclassified `/api/*` routes are denied with `403`.
- Placeholder clinical LLM and report/PDF generation routes return `501`.
- UI navigation does not grant API access.

See `api/core/access.py` for the authoritative route classification and
[`SECURITY.md`](SECURITY.md) for the data/logging boundary.

## Local configuration

- `DB_URL=sqlite:///data/medigator.db`
- `DEMO_MODE=true` and `SYNTHETIC_DATA_ONLY=true`
- `DEMO_ACCESS_CODE=<local shared code>`
- optional `OPENAI_API_KEY`
- optional `ENABLE_RAG=true`; canonical Docker sets it to `false`
- optional `BM25_QUERY_EXPANSION=true`; defaults to `false` based on the frozen
  retrieval fixture

Start the canonical demo with `make docker-up`. The unified Next.js frontend is
served at `http://localhost:3000`; the optional two-frontend workflow also uses
port 3001 but is not part of the reproducibility gate.
