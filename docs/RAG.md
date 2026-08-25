# RAG retrieval (research prototype)

Bundled guideline snippets in `docs/rag/` are indexed into `rag_index/`.
This is **not** a clinical evidence service.

## What the retriever actually does

When `enable_rag=true`, search is hybrid **embedding + BM25** with synonym
query expansion. **MMR diversity is not implemented.**

`enable_rag` defaults to `false`. Evidence cards then fall back to static demo
cards and declare `provenance.source` as `static` or `rag`.

## Evaluation

`api/services/rag/eval.py` scores **BM25 hit@k** on
`data/rag/eval_queries.json` against the committed `rag_index/meta.json`.
It does not download embedding models and is not a published IR benchmark.

```bash
PYTHONPATH=. python -c "from api.services.rag.eval import evaluate; import json; print(json.dumps(evaluate(), indent=2))"
pytest api/tests/test_rag_eval.py -q
```
