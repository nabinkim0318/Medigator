# Security boundary (research prototype)

**Research prototype.** Synthetic/demo data only.
**Not for diagnosis, treatment, clinical use, or production.** It is **not**
production security and makes **no** HIPAA or production-compliance claims.

`DEMO_MODE=true` does **not** make arbitrary identifiers safe. Obvious
real-looking identifiers are rejected where practical; this is not
de-identification.

## Access model

- Deny-by-default for `/api/*`.
- Patient intake writes (`POST /api/v1/patient/profile`, `POST /api/v1/patient/appointment`)
  and clinical helpers (`/summary`, `/evidence`, `/codes`, RAG search/status)
  are open for the demo, with synthetic-data checks on persisted intake.
- Doctor/admin-style reads (profile list/get/delete, stats, analytics dashboard/trends)
  require a random **operator session** from `POST /api/v1/auth/demo-operator`
  using `DEMO_ACCESS_CODE`. Send `Authorization: Bearer <operator_session>`.
- Username-derived UUIDs are **not** authentication. `POST /api/v1/auth/login` is disabled.
- File, notification, export, search, token-in-path reads, RAG index builds,
  and unauthenticated patient dumps are **disabled** (403).
- Placeholder clinical LLM/report generation returns **501** (not implemented),
  not a fake 200 diagnosis or treatment plan.
- Live demo helpers (`/summary`, `/codes`, `/evidence`) include a `provenance`
  object (`openai` / `fallback` / `rules` / `rag` / `static`). They are not
  clinical decisions.
- UI routing is not authorization.

## Token transport

Patient correlation ids live in `sessionStorage` and request JSON bodies.
They are not placed in query strings or shown in the UI.

## Logging

Logs use event names/status/paths only. Request bodies, tokens, raw queries,
raw model output, and third-party exception payloads must not be logged.

## Runtime artifacts

Ignore local SQLite files (`data/medigator.db` and `*.db` / WAL/SHM sidecars),
uploads, generated PDFs/reports, logs, and FAISS rebuild outputs. Tracked
`data/` JSON/CSV fixtures and `docs/` sources are synthetic demo content, not
runtime dumps. The committed `rag_index/` files are treated as a demo fixture
so search can run without an index-build API. PostgreSQL is not a runtime
backend.

## Historical secret / history audit

The security-remediation audit was performed at
`6bcdf146416c62d31bdfc8d95e0ee788909e2113`. This is an audit record, not a
continuing guarantee about every future commit. Matched values are not written
here.

| Check | Verdict |
| --- | --- |
| Audited-tree regex scan (PEM headers, `AKIA…` keys, assigned `api_key`/`secret_key` literals) | Clean for tracked source. Placeholders in `*.env.example` were allowlisted. |
| History through the audited commit: added `*.pem` / `*.key` / `.env` / `id_rsa` / `credentials.json` | None found. |
| GitHub secret-scanning alerts | **NOT VERIFIED** — local `gh` authentication to github.com was invalid. |
| Rotation | Not performed. No live third-party credential was confirmed. |

`DEMO_ACCESS_CODE` is a shared demo operator password for this prototype, not a cloud credential. Do not treat it as production IAM.

## CI gates

Backend pre-commit/lint/tests, frontend typecheck and build, and Docker HTTP
smoke are **blocking**.
The GitHub Actions `dependency-report` job runs `safety check` and uploads an
artifact; it is **nonblocking** (current `safety check` reports many findings
in the torch/transformers stack). A green report job does not mean zero
vulnerabilities. Frontend ESLint is **absent**.
