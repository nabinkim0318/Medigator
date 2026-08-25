# RAG retrieval (research prototype)

Bundled guideline snippets in `docs/rag/` are indexed into `rag_index/`.
This is **not** a clinical evidence service.

## What the retriever actually does

When `enable_rag=true`, search is hybrid **embedding + BM25** with synonym
query expansion. **MMR diversity is not implemented.**

`enable_rag` defaults to `false`. Evidence cards then fall back to static demo
cards and declare `provenance.source` as `static` or `rag`. Evidence cards
include `chunk_id` / `file` / `start` / `end` when the hit came from RAG.

## Evaluation

`api/services/rag/eval.py` is a small IR harness over the committed 49-chunk
demo corpus (`rag_index/meta.json`) and `data/rag/eval_queries.json`.

It reports:

- exact **chunk-id** graded judgments (not filename substring match)
- **Recall@1 / Recall@3 / Recall@5**, **MRR**, **nDCG@5**
- **document-level** hit/recall/MRR derived from chunk-id prefixes
- **BM25** vs **TF-IDF cosine** vs **hybrid** (TF-IDF 0.6 + BM25 0.4, the
  same merge weights as `retrieve.py`)
- query expansion **off vs on**
- SHA-256 of corpus / index / eval fixtures (`data/rag/eval_manifest.json`)

It does **not** download MiniLM, does **not** score FAISS embeddings in CI,
does **not** implement MMR, and is **not** a clinical retrieval benchmark.
Vector/hybrid in this harness is lexical TF-IDF cosine, not production
`all-MiniLM-L6-v2`. On this fixture, BM25 query expansion currently **lowers**
metrics versus the raw query because `bm25_or_clause` injects `AND`/`OR`
tokens; that delta is recorded rather than assumed to be an improvement.

```bash
PYTHONPATH=. python -m api.services.rag.eval
pytest api/tests/test_rag_eval.py -q
```
