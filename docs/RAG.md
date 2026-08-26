# RAG retrieval (research prototype)

Bundled guideline snippets in `docs/rag/` are indexed into `rag_index/`.
This is **not** a clinical evidence service.

## What the retriever actually does

Runtime retrieval supports three explicit modes via `RAG_RETRIEVAL_MODE`:

- `bm25` — `BM25Okapi` only; MiniLM query encoding is not required
- `vector` — MiniLM (`sentence-transformers/all-MiniLM-L6-v2`) + committed
  FAISS inner-product index; no BM25 contribution
- `hybrid` — MiniLM/FAISS and BM25 merged at the existing weights **0.6
  vector / 0.4 BM25**

The current demo default is `bm25`. Vector and hybrid remain available
experimental/evaluation modes. They are not removed and are not treated as
broken; the frozen fixture currently ranks BM25 higher.

The committed synthetic/demo fixture currently favors BM25, so the
application uses BM25 as the default retrieval mode. This is an
evidence-based default for this repository fixture, not a general claim about
lexical versus semantic retrieval.

On the frozen fixture:

```text
BM25 Recall@5 = 0.903    MiniLM Recall@5 = 0.759    Hybrid Recall@5 = 0.774
BM25 nDCG@5  = 0.901    MiniLM nDCG@5  = 0.765    Hybrid nDCG@5  = 0.826
```

The embedding channel uses synonym query expansion. BM25 expansion emits a
bounded lexical term list and is disabled by default
(`BM25_QUERY_EXPANSION=false`) because the frozen fixture still favors the raw
BM25 query.
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
`all-MiniLM-L6-v2`.

Current BM25 results on the committed fixture:

| Variant | Hit@5 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No expansion | 20/20 | 0.402 | 0.758 | 0.903 | 1.000 | 0.901 |
| Legacy Boolean-style expansion | 20/20 | 0.250 | 0.620 | 0.755 | 0.821 | 0.709 |
| Fixed lexical expansion | 20/20 | 0.250 | 0.620 | 0.755 | 0.821 | 0.709 |

Document-level results were Hit@5 20/20, Recall@5 0.950, and MRR 1.000
without expansion. Both legacy and fixed expansion produced Hit@5 20/20,
Recall@5 0.950, and MRR 0.854.

The legacy implementation serialized expansion as Boolean-looking text, for
example `(chest) AND (pain)`, even though BM25 uses a bag-of-words tokenizer.
That tokenizer treated generated `and` / `or` syntax as lexical terms. The
fixed implementation passes original-first, deduplicated lexical terms with a
40-term cap. This removed the token contamination but did not change aggregate
BM25 metrics on the unchanged fixture. The hypothesized contamination was real,
but it does not explain the measured expansion regression on this fixture;
runtime BM25 expansion therefore changed from unconditional to opt-in.

Deterministic hybrid results also remained unchanged from the legacy expanded
run: fixed expansion produced Recall@1 0.377, Recall@3 0.678, Recall@5 0.834,
MRR 0.975, and nDCG@5 0.821, versus 0.402, 0.770, 0.868, 1.000, and 0.881
without expansion. This hybrid is TF-IDF 0.6 + BM25 0.4; it is not evidence
about runtime MiniLM/FAISS quality.

The CI evaluation's vector channel uses TF-IDF cosine for deterministic,
dependency-cheap comparison. It is not a MiniLM/FAISS measurement.

## Runtime MiniLM/FAISS benchmark

`api/services/rag/eval_runtime.py` measures the **actual** runtime retriever
against the same frozen fixture:

- BM25 with the current default (`BM25_QUERY_EXPANSION=false`)
- MiniLM/FAISS using `sentence-transformers/all-MiniLM-L6-v2` and the
  committed `IndexFlatIP` (384-d inner product) index
- the production hybrid merge at weights **0.6 vector / 0.4 BM25**

Query handling uses `make_query({"cc": query})`, so synonym expansion for the
embedding channel and the BM25 expansion default match production. Candidate
pooling is `max(8, k * 2)` per channel, then the production merge. Metric
helpers are shared with `eval.py`.

This command is **not** a blocking CI job. It requires SentenceTransformers
and FAISS. The first run may download MiniLM into the local Hugging Face
cache; after the model is available locally, retrieval evaluation does not
require OpenAI, a clinical service, or a live external medical API. CPU is
sufficient. If the model cannot be loaded, the process exits with
`RUNTIME_BENCHMARK_NOT_RUN` instead of substituting TF-IDF.

Observed local snapshot (Python 3.12.3, sentence-transformers 5.1.1,
transformers 4.56.2, faiss 1.12.0, scikit-learn 1.7.2). Repeat run in the same
environment: identical aggregate metrics and ranked chunk IDs.

| Retriever | Hit@5 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BM25 | 20/20 | 0.402 | 0.758 | 0.903 | 1.000 | 0.901 |
| TF-IDF surrogate | 20/20 | 0.402 | 0.703 | 0.851 | 1.000 | 0.861 |
| TF-IDF/BM25 hybrid | 20/20 | 0.402 | 0.770 | 0.868 | 1.000 | 0.881 |
| MiniLM/FAISS | 20/20 | 0.348 | 0.662 | 0.759 | 0.902 | 0.765 |
| Runtime MiniLM/FAISS+BM25 hybrid | 20/20 | 0.402 | 0.724 | 0.774 | 1.000 | 0.826 |

On this fixture, BM25 is stronger than MiniLM/FAISS. The current runtime
hybrid does not outperform BM25, so the 0.6/0.4 weighting is not justified by
these 20 queries. Weights were not swept. The demo runtime therefore defaults
to BM25 while leaving vector and hybrid selectable. Hit@5 remained 20/20 for
every channel; MiniLM's weaker recall is ranking, not total miss. Notable MiniLM
weaknesses include `acc-aha-2021` (MRR 0.200) and `heart-mace` (MRR 0.333).
`heart-score` hybrid Recall@5 (0.400) was below both BM25 (0.800) and MiniLM
(0.600).

This is **Runtime MiniLM/FAISS: evaluated on the frozen synthetic/demo
fixture**. It is not clinical IR validation, not a large-corpus study, and not
production retrieval validation. Results can vary with model/library versions.
The default-mode change does not remove those limits: 20 queries, 49 chunks,
synthetic/demo relevance judgments, model/library version dependence, no
production retrieval validation. The former 15-vs-14 file count is explained:
empty `docs/prompts.md` was discovered at the original index build and
produced zero chunks. Third-party corpus rights remain unverified.

Tests verify ranked-hit `chunk_id`, file, offsets, and text hash; evidence-card
provenance; instruction-only and keyword-stuffed poison handling; that query
injection cannot create corpus chunk IDs; shared metric helpers; FAISS-to-chunk
mapping; hybrid weight reuse; index integrity failures; and that a missing
MiniLM model exits with `RUNTIME_BENCHMARK_NOT_RUN` instead of TF-IDF.

Bundled source descriptions and rights limitations are documented in
[`RAG_CORPUS.md`](RAG_CORPUS.md). The source and artifact hashes that define
this fixture are committed in `data/rag/eval_manifest.json`.

```bash
PYTHONPATH=. python -m api.services.rag.eval
PYTHONPATH=. python -m api.services.rag.eval_runtime
pytest api/tests/test_rag_eval.py api/tests/test_rag_runtime_eval.py -q
```
