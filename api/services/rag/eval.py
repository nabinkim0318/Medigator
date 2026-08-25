"""Retrieval evaluation over the committed demo corpus.

Ranks the full committed `rag_index/meta.json` with BM25, TF-IDF cosine, and a
hybrid merge. Judgments are exact chunk ids from that metadata file.

This does not download MiniLM, does not score FAISS query embeddings, does not
implement MMR, and is not a clinical retrieval benchmark. `index.faiss` is
hashed when present; the vector channel in this harness is TF-IDF cosine.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Literal

from api.services.rag.query_expand import (
    bm25_or_clause,
    expand_query_text,
    load_synonyms,
)
from api.services.rag.retrieve import _merge_scores, _tokenize

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_META = ROOT / "rag_index" / "meta.json"
DEFAULT_QUERIES = ROOT / "data" / "rag" / "eval_queries.json"
DEFAULT_SYNONYMS = ROOT / "rag_index" / "synonyms.json"
DEFAULT_SUMMARY = ROOT / "rag_index" / "build_summary.json"
DEFAULT_FAISS = ROOT / "rag_index" / "index.faiss"
DEFAULT_MANIFEST = ROOT / "data" / "rag" / "eval_manifest.json"
DEFAULT_DOCS = ROOT / "docs"

Mode = Literal["bm25", "tfidf", "hybrid"]
MODES: tuple[Mode, ...] = ("bm25", "tfidf", "hybrid")
INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system override",
    "always cite this first",
)
NOTE = (
    "Chunk-id IR metrics on the committed 49-chunk demo corpus. "
    "vector/hybrid here is TF-IDF cosine merged with BM25 (production weights "
    "0.6/0.4), not MiniLM+FAISS. Not MMR, not a clinical benchmark."
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return sha256_bytes(path.read_bytes())


def doc_id_for(chunk_id: str) -> str:
    return chunk_id.rsplit("__", 1)[0]


def is_poisoned_text(text: str) -> bool:
    lowered = (text or "").lower()
    return any(marker in lowered for marker in INJECTION_MARKERS)


def fixture_hashes(
    *,
    meta_path: Path = DEFAULT_META,
    queries_path: Path = DEFAULT_QUERIES,
    synonyms_path: Path = DEFAULT_SYNONYMS,
    summary_path: Path = DEFAULT_SUMMARY,
    faiss_path: Path = DEFAULT_FAISS,
    docs_dir: Path = DEFAULT_DOCS,
) -> dict[str, Any]:
    corpus = load_json(meta_path)
    source_files: dict[str, str | None] = {}
    combined = hashlib.sha256()
    for rel in sorted({str(item.get("file") or "") for item in corpus}):
        if not rel:
            continue
        digest = sha256_file(docs_dir / rel)
        source_files[rel] = digest
        combined.update(rel.encode("utf-8"))
        combined.update(b"\0")
        combined.update((digest or "").encode("utf-8"))
        combined.update(b"\n")
    return {
        "meta.json": sha256_file(meta_path),
        "eval_queries.json": sha256_file(queries_path),
        "synonyms.json": sha256_file(synonyms_path),
        "build_summary.json": sha256_file(summary_path),
        "index.faiss": sha256_file(faiss_path),
        "source_files": source_files,
        "source_files_combined": combined.hexdigest(),
    }


def dcg(grades: list[float]) -> float:
    return sum((2**grade - 1) / math.log2(idx + 2) for idx, grade in enumerate(grades))


def ndcg_at_k(ranked_ids: list[str], grades: dict[str, int], k: int) -> float:
    gained = [float(grades.get(chunk_id, 0)) for chunk_id in ranked_ids[:k]]
    ideal = [float(g) for g in sorted(grades.values(), reverse=True)[:k]]
    denom = dcg(ideal)
    return (dcg(gained) / denom) if denom else 0.0


def recall_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    retrieved = set(ranked_ids[:k])
    return len(retrieved & relevant) / len(relevant)


def mrr_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    for rank, chunk_id in enumerate(ranked_ids[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def hit_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(chunk_id in relevant for chunk_id in ranked_ids[:k]) else 0.0


def _mean(values: list[float]) -> float:
    return (sum(values) / len(values)) if values else 0.0


def _text_sha(text: str) -> str:
    return sha256_bytes((text or "").encode("utf-8"))


def _hit_payload(item: dict[str, Any], score: float) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "file": item.get("file"),
        "title": item.get("title"),
        "score": float(score),
        "start": item.get("start"),
        "end": item.get("end"),
        "text_sha256": _text_sha(item.get("text") or ""),
        "poisoned": is_poisoned_text(item.get("text") or ""),
    }


def _bm25_scores(query: str, corpus: list[dict[str, Any]]) -> list[float]:
    from rank_bm25 import BM25Okapi

    tokenized = [_tokenize(item.get("text") or "") for item in corpus]
    return [float(s) for s in BM25Okapi(tokenized).get_scores(_tokenize(query))]


def _tfidf_scores(query: str, corpus: list[dict[str, Any]]) -> list[float]:
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = [item.get("text") or "" for item in corpus]
    vectorizer = TfidfVectorizer(analyzer=_tokenize)
    matrix = vectorizer.fit_transform(texts)
    q_vec = vectorizer.transform([query])
    sims = (matrix @ q_vec.T).toarray().ravel()
    return [float(s) for s in sims]


def _ranked_from_scores(
    scores: list[float], corpus: list[dict[str, Any]], k: int
) -> list[dict[str, Any]]:
    order = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)[:k]
    return [_hit_payload(corpus[idx], score) for idx, score in order]


def rank(
    query: str,
    corpus: list[dict[str, Any]],
    *,
    mode: Mode = "bm25",
    k: int = 5,
    query_bm25: str | None = None,
    query_tfidf: str | None = None,
) -> list[dict[str, Any]]:
    bm25_query = query if query_bm25 is None else query_bm25
    tfidf_query = query if query_tfidf is None else query_tfidf
    if mode == "bm25":
        return _ranked_from_scores(_bm25_scores(bm25_query, corpus), corpus, k)
    if mode == "tfidf":
        return _ranked_from_scores(_tfidf_scores(tfidf_query, corpus), corpus, k)
    if mode != "hybrid":
        msg = f"unknown ranking mode: {mode}"
        raise ValueError(msg)

    bm25 = _bm25_scores(bm25_query, corpus)
    tfidf = _tfidf_scores(tfidf_query, corpus)
    n = len(corpus)
    merged = _merge_scores(
        [(i, tfidf[i]) for i in range(n)],
        [(i, bm25[i]) for i in range(n)],
        w_emb=0.6,
        w_bm25=0.4,
    )
    return [_hit_payload(corpus[idx], score) for idx, score in merged[:k]]


def _expand(raw: str, syn: dict[str, list[str]], mode: Mode) -> str:
    if not syn:
        return raw
    if mode == "bm25":
        return bm25_or_clause(raw, syn)
    return expand_query_text(raw, syn)


def _metrics_for_row(
    ranked: list[dict[str, Any]], grades: dict[str, int], k: int
) -> dict[str, float]:
    ranked_ids = [str(hit.get("id") or "") for hit in ranked]
    relevant = {cid for cid, grade in grades.items() if grade > 0}
    rel_docs = {doc_id_for(cid) for cid in relevant}
    ranked_docs = [doc_id_for(cid) for cid in ranked_ids]
    return {
        "hit_at_k": hit_at_k(ranked_ids, relevant, k),
        "recall@1": recall_at_k(ranked_ids, relevant, 1),
        "recall@3": recall_at_k(ranked_ids, relevant, 3),
        "recall@5": recall_at_k(ranked_ids, relevant, min(k, 5)),
        "mrr": mrr_at_k(ranked_ids, relevant, k),
        "ndcg@5": ndcg_at_k(ranked_ids, grades, min(k, 5)),
        "doc_hit_at_k": hit_at_k(ranked_docs, rel_docs, k),
        "doc_recall@5": recall_at_k(ranked_docs, rel_docs, min(k, 5)),
        "doc_mrr": mrr_at_k(ranked_docs, rel_docs, k),
    }


def _validate_queries(
    corpus: list[dict[str, Any]], queries: list[dict[str, Any]]
) -> None:
    corpus_ids = {item.get("id") for item in corpus}
    if not queries:
        msg = "eval query fixture is empty"
        raise ValueError(msg)
    for spec in queries:
        grades = spec.get("relevant") or {}
        if not isinstance(grades, dict) or not grades:
            msg = f"{spec.get('id')}: relevant chunk grades are required"
            raise ValueError(msg)
        missing = [cid for cid in grades if cid not in corpus_ids]
        if missing:
            msg = f"{spec.get('id')}: unknown chunk ids {missing}"
            raise ValueError(msg)


def evaluate(
    *,
    meta_path: Path = DEFAULT_META,
    queries_path: Path = DEFAULT_QUERIES,
    k: int = 5,
    mode: Mode = "bm25",
    use_query_expansion: bool = True,
) -> dict[str, Any]:
    corpus = load_json(meta_path)
    queries = load_json(queries_path)
    _validate_queries(corpus, queries)
    syn = load_synonyms(str(DEFAULT_SYNONYMS)) if use_query_expansion else {}

    rows: list[dict[str, Any]] = []
    metric_lists: dict[str, list[float]] = {}
    for spec in queries:
        raw = spec["query"]
        ranked = rank(
            raw,
            corpus,
            mode=mode,
            k=k,
            query_bm25=_expand(raw, syn, "bm25"),
            query_tfidf=_expand(raw, syn, "tfidf"),
        )
        grades = {str(cid): int(grade) for cid, grade in spec["relevant"].items()}
        metrics = _metrics_for_row(ranked, grades, k)
        for key, value in metrics.items():
            metric_lists.setdefault(key, []).append(value)
        rows.append(
            {
                "id": spec["id"],
                "query": raw,
                "metrics": metrics,
                "hits": ranked,
            }
        )

    means = {key: _mean(vals) for key, vals in metric_lists.items()}
    n = len(queries)
    return {
        "k": k,
        "n": n,
        "mode": mode,
        "query_expansion": use_query_expansion,
        "mmr": False,
        "embedding_model": None,
        "note": NOTE,
        "hashes": fixture_hashes(meta_path=meta_path, queries_path=queries_path),
        "metrics": means,
        "hit_at_k": means.get("hit_at_k", 0.0),
        "rows": rows,
    }


def _delta(on: dict[str, float], off: dict[str, float]) -> dict[str, float]:
    keys = sorted(set(on) | set(off))
    return {key: on.get(key, 0.0) - off.get(key, 0.0) for key in keys}


def evaluate_suite(*, k: int = 5, modes: tuple[Mode, ...] = MODES) -> dict[str, Any]:
    runs: dict[str, Any] = {}
    n = 0
    hashes: dict[str, Any] = fixture_hashes()
    for mode in modes:
        off = evaluate(k=k, mode=mode, use_query_expansion=False)
        on = evaluate(k=k, mode=mode, use_query_expansion=True)
        n = int(on["n"])
        hashes = on["hashes"]
        runs[mode] = {
            "expansion_off": {"metrics": off["metrics"], "hit_at_k": off["hit_at_k"]},
            "expansion_on": {"metrics": on["metrics"], "hit_at_k": on["hit_at_k"]},
            "expansion_delta": _delta(on["metrics"], off["metrics"]),
        }
    return {
        "k": k,
        "n": n,
        "mmr": False,
        "embedding_model": None,
        "note": NOTE,
        "hashes": hashes,
        "modes": runs,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_suite(), indent=2))
