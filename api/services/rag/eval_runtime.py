"""Offline MiniLM/FAISS runtime retrieval benchmark.

Measures the production vector path (all-MiniLM-L6-v2 + committed FAISS) and
the production MiniLM/FAISS + BM25 hybrid against the same frozen fixture used
by the deterministic CI evaluator.

This module is not a CI job. It may load a local Hugging Face model cache or
download MiniLM once. It never substitutes TF-IDF for the runtime vector
channel. It is not a clinical IR benchmark.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Literal

from api.core.config import settings
from api.services.rag.eval import (
    DEFAULT_FAISS,
    DEFAULT_MANIFEST,
    DEFAULT_META,
    DEFAULT_QUERIES,
    DEFAULT_SUMMARY,
    _hit_payload,
    _mean,
    _validate_queries,
    evaluate,
    fixture_hashes,
    load_json,
    metrics_for_row,
    sha256_file,
)
from api.services.rag.retrieve import (
    HYBRID_W_BM25,
    HYBRID_W_EMB,
    MODEL_NAME,
    _tokenize,
    make_query,
    rank_channels,
)
from api.services.rag.store import RAGStore

try:
    import faiss
except ImportError:  # pragma: no cover - optional when RAG deps are absent
    faiss = None  # type: ignore

try:
    from rank_bm25 import BM25Okapi
except Exception:  # pragma: no cover
    BM25Okapi = None  # type: ignore

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "reports" / "runtime_eval_results.json"
RuntimeMode = Literal["bm25", "vector", "hybrid"]
RUNTIME_MODES: tuple[RuntimeMode, ...] = ("bm25", "vector", "hybrid")
STATUS_NOT_RUN = "RUNTIME_BENCHMARK_NOT_RUN"
NOTE = (
    "Offline MiniLM/FAISS runtime benchmark on the frozen 20-query / 49-chunk "
    "demo fixture. CI evaluation remains BM25 + TF-IDF cosine. Not MMR, not a "
    "clinical retrieval benchmark, not production IR validation."
)


class RuntimeBenchmarkNotRun(RuntimeError):
    """Raised when the actual runtime vector path cannot be measured."""


class IndexIntegrityError(RuntimeError):
    """Raised when the committed FAISS index does not match its metadata."""


def environment_versions() -> dict[str, str]:
    import importlib

    versions: dict[str, str] = {"python": sys.version.split()[0]}
    modules = {
        "sentence-transformers": "sentence_transformers",
        "transformers": "transformers",
        "faiss": "faiss",
        "scikit-learn": "sklearn",
    }
    for label, module_name in modules.items():
        try:
            module = importlib.import_module(module_name)
            versions[label] = str(getattr(module, "__version__", "unknown"))
        except Exception:
            versions[label] = "unavailable"
    return versions


def load_embedding_model(
    model_name: str = MODEL_NAME,
    *,
    local_files_only: bool | None = None,
) -> Any:
    """Load MiniLM. Prefer the local cache; never fall back to TF-IDF."""
    if SentenceTransformer is None:
        raise RuntimeBenchmarkNotRun(
            f"{STATUS_NOT_RUN}: sentence-transformers is not installed. "
            "No TF-IDF fallback is used."
        )
    if local_files_only is None:
        flag = os.getenv("RUNTIME_BENCHMARK_LOCAL_FILES_ONLY", "").strip().lower()
        local_files_only = flag in {"1", "true", "yes"}

    try:
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception as local_exc:
        if local_files_only:
            raise RuntimeBenchmarkNotRun(
                f"{STATUS_NOT_RUN}: MiniLM model {model_name} is not available "
                "in the local Hugging Face cache. No TF-IDF fallback is used."
            ) from local_exc
        try:
            return SentenceTransformer(model_name, local_files_only=False)
        except Exception as download_exc:
            raise RuntimeBenchmarkNotRun(
                f"{STATUS_NOT_RUN}: failed to load embedding model {model_name} "
                "from the local cache or by download. No TF-IDF fallback is used."
            ) from download_exc


def verify_runtime_index(
    *,
    meta_path: Path = DEFAULT_META,
    faiss_path: Path = DEFAULT_FAISS,
    summary_path: Path = DEFAULT_SUMMARY,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> dict[str, Any]:
    """Fail if the committed FAISS index does not match metadata/manifest."""
    if faiss is None:
        raise RuntimeBenchmarkNotRun(
            f"{STATUS_NOT_RUN}: faiss is not installed. No TF-IDF fallback is used."
        )
    if not faiss_path.is_file() or not meta_path.is_file():
        raise IndexIntegrityError(
            f"committed FAISS artifacts missing: {faiss_path} / {meta_path}"
        )

    corpus = load_json(meta_path)
    if not isinstance(corpus, list) or not corpus:
        raise IndexIntegrityError("meta.json is empty or invalid")
    index = faiss.read_index(str(faiss_path))
    summary = load_json(summary_path) if summary_path.is_file() else {}
    manifest = load_json(manifest_path) if manifest_path.is_file() else {}

    expected_dim = int(summary.get("dim") or 0)
    expected_chunks = int(summary.get("chunks") or 0)
    expected_model = str(summary.get("model") or "")
    empty_ids = [
        item.get("id") for item in corpus if not (item.get("text") or "").strip()
    ]
    errors: list[str] = []
    if not isinstance(index, faiss.IndexFlatIP):
        errors.append(f"expected IndexFlatIP, got {type(index).__name__}")
    if index.ntotal != len(corpus):
        errors.append(f"vector count {index.ntotal} != meta chunks {len(corpus)}")
    if expected_chunks and index.ntotal != expected_chunks:
        errors.append(
            f"vector count {index.ntotal} != build_summary.chunks {expected_chunks}"
        )
    if expected_dim and index.d != expected_dim:
        errors.append(f"index dim {index.d} != build_summary.dim {expected_dim}")
    if expected_model and expected_model != MODEL_NAME:
        errors.append(
            f"build_summary.model {expected_model!r} != runtime {MODEL_NAME!r}"
        )
    if empty_ids:
        errors.append(
            "empty chunk texts would desynchronize BM25 row ids from FAISS ids: "
            f"{empty_ids}"
        )
    live_faiss = sha256_file(faiss_path)
    live_meta = sha256_file(meta_path)
    if manifest.get("index.faiss") and live_faiss != manifest["index.faiss"]:
        errors.append("index.faiss hash does not match eval_manifest.json")
    if manifest.get("meta.json") and live_meta != manifest["meta.json"]:
        errors.append("meta.json hash does not match eval_manifest.json")
    if errors:
        raise IndexIntegrityError("FAISS integrity check failed: " + "; ".join(errors))

    return {
        "type": type(index).__name__,
        "ntotal": int(index.ntotal),
        "dim": int(index.d),
        "metric": "inner_product",
        "model": expected_model or MODEL_NAME,
        "index.faiss": live_faiss,
        "meta.json": live_meta,
    }


def _mode_flags(mode: RuntimeMode) -> tuple[bool, bool]:
    if mode == "bm25":
        return False, True
    if mode == "vector":
        return True, False
    if mode == "hybrid":
        return True, True
    msg = f"unknown runtime ranking mode: {mode}"
    raise ValueError(msg)


def _build_bm25(store: RAGStore) -> Any:
    if BM25Okapi is None:
        raise RuntimeBenchmarkNotRun(
            f"{STATUS_NOT_RUN}: rank-bm25 is not installed. No TF-IDF fallback is used."
        )
    corpus_texts = store.get_corpus_texts()
    if len(corpus_texts) != store.size:
        raise IndexIntegrityError(
            f"BM25 corpus length {len(corpus_texts)} != FAISS rows {store.size}"
        )
    return BM25Okapi([_tokenize(text) for text in corpus_texts])


def rank_runtime(
    query: str,
    *,
    store: RAGStore,
    model: Any | None,
    bm25: Any | None,
    mode: RuntimeMode,
    k: int,
) -> list[dict[str, Any]]:
    use_vector, use_lexical = _mode_flags(mode)
    query_dict = make_query({"cc": query})
    ranked = rank_channels(
        query_dict,
        store=store,
        model=model,
        bm25=bm25,
        k=k,
        use_vector=use_vector,
        use_bm25=use_lexical,
    )
    return [_hit_payload(store.get_meta(idx), score) for idx, score in ranked]


def _evaluate_mode(
    *,
    mode: RuntimeMode,
    corpus: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    store: RAGStore,
    model: Any | None,
    bm25: Any | None,
    k: int,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    metric_lists: dict[str, list[float]] = {}
    started = time.perf_counter()
    for spec in queries:
        raw = spec["query"]
        ranked = rank_runtime(
            raw,
            store=store,
            model=model,
            bm25=bm25,
            mode=mode,
            k=k,
        )
        grades = {str(cid): int(grade) for cid, grade in spec["relevant"].items()}
        metrics = metrics_for_row(ranked, grades, k)
        for key, value in metrics.items():
            metric_lists.setdefault(key, []).append(value)
        rows.append(
            {
                "id": spec["id"],
                "query": raw,
                "channel": mode,
                "expected": grades,
                "ranked_ids": [hit.get("id") for hit in ranked],
                "metrics": metrics,
                "hits": ranked,
            }
        )
    elapsed = time.perf_counter() - started
    means = {key: _mean(vals) for key, vals in metric_lists.items()}
    return {
        "k": k,
        "n": len(queries),
        "mode": mode,
        "query_expansion_bm25": bool(settings.bm25_query_expansion),
        "query_expansion_vector": True,
        "embedding_model": MODEL_NAME if mode != "bm25" else None,
        "hybrid_weights": (
            {"vector": HYBRID_W_EMB, "bm25": HYBRID_W_BM25}
            if mode == "hybrid"
            else None
        ),
        "timing": {
            "total_s": elapsed,
            "avg_query_s": (elapsed / len(queries)) if queries else 0.0,
        },
        "metrics": means,
        "hit_at_k": means.get("hit_at_k", 0.0),
        "rows": rows,
        "chunks": len(corpus),
    }


def _ci_baseline(k: int) -> dict[str, Any]:
    runs: dict[str, Any] = {}
    for mode in ("bm25", "tfidf", "hybrid"):
        result = evaluate(k=k, mode=mode, use_query_expansion=False)
        runs[mode] = {
            "metrics": result["metrics"],
            "hit_at_k": result["hit_at_k"],
            "query_expansion": False,
            "embedding_model": None,
        }
    return {
        "note": (
            "Deterministic CI-safe baseline. Vector/hybrid here is TF-IDF cosine, "
            "not MiniLM/FAISS."
        ),
        "query_expansion": False,
        "modes": runs,
    }


def evaluate_runtime(
    *,
    k: int = 5,
    include_ci_baseline: bool = True,
    local_files_only: bool | None = None,
    model: Any | None = None,
    meta_path: Path = DEFAULT_META,
    queries_path: Path = DEFAULT_QUERIES,
    faiss_path: Path = DEFAULT_FAISS,
    index_dir: Path | None = None,
) -> dict[str, Any]:
    corpus = load_json(meta_path)
    queries = load_json(queries_path)
    _validate_queries(corpus, queries)
    index_info = verify_runtime_index(
        meta_path=meta_path,
        faiss_path=faiss_path,
    )
    store = RAGStore(str(index_dir or faiss_path.parent))
    runtime_model = (
        model
        if model is not None
        else load_embedding_model(local_files_only=local_files_only)
    )
    bm25 = _build_bm25(store)

    runtime_runs: dict[str, Any] = {}
    started = time.perf_counter()
    for mode in RUNTIME_MODES:
        runtime_runs[mode] = _evaluate_mode(
            mode=mode,
            corpus=corpus,
            queries=queries,
            store=store,
            model=runtime_model,
            bm25=bm25,
            k=k,
        )
    elapsed = time.perf_counter() - started
    hashes = fixture_hashes(meta_path=meta_path, queries_path=queries_path)
    payload: dict[str, Any] = {
        "status": "ok",
        "k": k,
        "n": len(queries),
        "chunks": len(corpus),
        "mmr": False,
        "embedding_model": MODEL_NAME,
        "hybrid_weights": {"vector": HYBRID_W_EMB, "bm25": HYBRID_W_BM25},
        "bm25_query_expansion": bool(settings.bm25_query_expansion),
        "vector_query_expansion": True,
        "note": NOTE,
        "environment": environment_versions(),
        "index": index_info,
        "hashes": hashes,
        "timing": {
            "total_s": elapsed,
            "avg_query_s": (elapsed / (len(queries) * len(RUNTIME_MODES)))
            if queries
            else 0.0,
        },
        "runtime": runtime_runs,
    }
    if include_ci_baseline:
        payload["ci_safe"] = _ci_baseline(k)
    return payload


def _fmt(metrics: dict[str, float]) -> str:
    return (
        f"Hit@5={metrics.get('hit_at_k', 0.0):.3f}  "
        f"R@1={metrics.get('recall@1', 0.0):.3f}  "
        f"R@3={metrics.get('recall@3', 0.0):.3f}  "
        f"R@5={metrics.get('recall@5', 0.0):.3f}  "
        f"MRR={metrics.get('mrr', 0.0):.3f}  "
        f"nDCG@5={metrics.get('ndcg@5', 0.0):.3f}"
    )


def print_summary(result: dict[str, Any]) -> None:
    print(NOTE)
    env = result.get("environment") or {}
    print("environment: " + ", ".join(f"{key}={value}" for key, value in env.items()))
    print(
        "hybrid weights: "
        f"vector={HYBRID_W_EMB} bm25={HYBRID_W_BM25}; "
        f"BM25 expansion={result.get('bm25_query_expansion')}"
    )
    ci_safe = result.get("ci_safe") or {}
    if ci_safe:
        print("\nCI-safe deterministic baseline (expansion off; TF-IDF ≠ MiniLM):")
        for mode in ("bm25", "tfidf", "hybrid"):
            metrics = ci_safe["modes"][mode]["metrics"]
            print(f"  {mode:<8} {_fmt(metrics)}")
    print("\nRuntime MiniLM/FAISS benchmark:")
    labels = {"bm25": "bm25", "vector": "minilm", "hybrid": "hybrid"}
    for mode in RUNTIME_MODES:
        metrics = result["runtime"][mode]["metrics"]
        print(f"  {labels[mode]:<8} {_fmt(metrics)}")
    misses = [
        row["id"]
        for row in result["runtime"]["hybrid"]["rows"]
        if row["metrics"].get("hit_at_k", 0.0) < 1.0
    ]
    if misses:
        print("hybrid Hit@5 misses:", ", ".join(misses))


def _write_output(result: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nwrote {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Offline MiniLM/FAISS runtime retrieval benchmark. "
            "Not a CI job and not a TF-IDF surrogate."
        )
    )
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON artifact path (gitignored reports/ by default)",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Do not download MiniLM; fail with RUNTIME_BENCHMARK_NOT_RUN if absent",
    )
    parser.add_argument(
        "--no-ci-baseline",
        action="store_true",
        help="Skip the deterministic TF-IDF/BM25 comparison block",
    )
    args = parser.parse_args(argv)
    try:
        result = evaluate_runtime(
            k=args.k,
            include_ci_baseline=not args.no_ci_baseline,
            local_files_only=True if args.local_files_only else None,
        )
    except RuntimeBenchmarkNotRun as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except IndexIntegrityError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    print_summary(result)
    _write_output(result, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
