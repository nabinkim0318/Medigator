# Medigator synthetic LLM fixtures

`data/intake/mock_patient.json` is synthetic input for exercising the summary
path. It is not a patient record and its output is not a clinical assessment.

The maintained backend regression suite is:

```bash
PYTHONPATH=. pytest api/tests/ -k "not trio"
```

That suite covers schema validation, deterministic fallback behavior,
provenance, access boundaries, persistence, and retrieval evaluation. OpenAI
credentials are not required for the deterministic test paths.

Two older executable demo scripts remain under `tests/`:

```bash
PYTHONPATH=. python tests/test_simple_mock.py

# Requires the local API to be running at http://localhost:8082
PYTHONPATH=. python tests/test_api_mock.py
```

These scripts are supplementary demonstrations, not separate CI gates. Do not
print, log, or commit API keys. If `OPENAI_API_KEY` is configured, live calls
may use the provider and incur cost; otherwise summary generation uses the
documented template fallback where applicable.

See `docs/API.md` for the current route boundary and `docs/SECURITY.md` for the
synthetic-data and logging rules.
