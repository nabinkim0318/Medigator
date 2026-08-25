# RAG retrieval (research prototype)

Bundled guideline snippets in `docs/rag/` are indexed into `rag_index/`.
This is **not** a clinical evidence service.

## What the retriever actually does

When `enable_rag=true`, search is hybrid **embedding + BM25** with synonym
query expansion. The embedding channel uses
`sentence-transformers/all-MiniLM-L6-v2` with a committed FAISS inner-product
index; normalized embedding and BM25 scores are merged with weights 0.6/0.4.
**MMR diversity is not implemented.**

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

Current BM25 results on the committed fixture:

| Expansion | Hit@5 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Off | 20/20 | 0.402 | 0.758 | 0.903 | 1.000 | 0.901 |
| On | 20/20 | 0.250 | 0.620 | 0.755 | 0.821 | 0.709 |

The CI evaluation's vector channel uses TF-IDF cosine for deterministic,
dependency-cheap comparison. It is not a benchmark of the runtime
MiniLM/FAISS embedding channel and is not a clinical IR study.

Tests additionally verify ranked-hit `chunk_id`, file, offsets, and text hash;
evidence-card provenance; instruction-only and keyword-stuffed poison handling;
and that query injection cannot create corpus chunk IDs.

Bundled source descriptions and rights limitations are documented in
[`RAG_CORPUS.md`](RAG_CORPUS.md). The source and artifact hashes that define
this fixture are committed in `data/rag/eval_manifest.json`.

```bash
PYTHONPATH=. python -m api.services.rag.eval
pytest api/tests/test_rag_eval.py -q
```
