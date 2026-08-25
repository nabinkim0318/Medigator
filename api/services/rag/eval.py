"""Cheap retrieval evaluation over the committed demo corpus.

This scores BM25 hit@k against golden queries. It does not download embedding
models, does not implement MMR, and is not a clinical retrieval benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from api.services.rag.query_expand import expand_query_text, load_synonyms
from api.services.rag.retrieve import _tokenize

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_META = ROOT / "rag_index" / "meta.json"
DEFAULT_QUERIES = ROOT / "data" / "rag" / "eval_queries.json"
DEFAULT_SYNONYMS = ROOT / "rag_index" / "synonyms.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _hit(ranked_files: list[str], expect: list[str]) -> bool:
    return any(any(exp in (name or "") for exp in expect) for name in ranked_files)


def bm25_rank(
    query: str, corpus: list[dict[str, Any]], k: int = 5
) -> list[dict[str, Any]]:
    from rank_bm25 import BM25Okapi

    tokenized = [_tokenize(item.get("text") or "") for item in corpus]
    scores = BM25Okapi(tokenized).get_scores(_tokenize(query))
    ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)[:k]
    out = []
    for idx, score in ranked:
        item = corpus[idx]
        out.append(
            {
                "file": item.get("file"),
                "title": item.get("title"),
                "score": float(score),
            }
        )
    return out


def evaluate(
    *,
    meta_path: Path = DEFAULT_META,
    queries_path: Path = DEFAULT_QUERIES,
    k: int = 5,
    use_query_expansion: bool = True,
) -> dict[str, Any]:
    corpus = load_json(meta_path)
    queries = load_json(queries_path)
    syn = load_synonyms(str(DEFAULT_SYNONYMS)) if use_query_expansion else {}

    rows: list[dict[str, Any]] = []
    hits = 0
    for spec in queries:
        raw = spec["query"]
        query = expand_query_text(raw, syn) if syn else raw
        ranked = bm25_rank(query, corpus, k=k)
        files = [str(item.get("file") or "") for item in ranked]
        ok = _hit(files, spec["expect_file_substr"])
        hits += int(ok)
        rows.append(
            {
                "id": spec["id"],
                "hit": ok,
                "query": raw,
                "files": files,
            }
        )

    n = len(queries)
    return {
        "k": k,
        "n": n,
        "hits": hits,
        "hit_at_k": (hits / n) if n else 0.0,
        "query_expansion": use_query_expansion,
        "mmr": False,
        "note": (
            "BM25 hit@k on the committed demo corpus. "
            "Not MMR, not an embedding eval, not a clinical benchmark."
        ),
        "rows": rows,
    }
