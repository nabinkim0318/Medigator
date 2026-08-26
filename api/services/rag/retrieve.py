# api/services/rag/retrieve.py
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Literal, TypedDict

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional when RAG deps are absent
    SentenceTransformer = None  # type: ignore

from .query_expand import (
    boost_key_terms,
    expand_bm25_terms,
    expand_query_text,
    load_synonyms,
)
from .types import Retrieval

# Get logger
logger = logging.getLogger(__name__)

try:
    from rank_bm25 import BM25Okapi  # optional
except Exception:  # pragma: no cover
    BM25Okapi = None  # type: ignore

# Import settings to use consistent RAG flag
from api.core.config import settings  # noqa: E402
from .store import RAGStore  # noqa: E402

USE_RAG = bool(getattr(settings, "enable_rag", False))
RAG_INDEX_DIR = os.getenv("RAG_INDEX_DIR", "rag_index")
RAG_TOPK = int(os.getenv("RAG_TOPK", "4"))

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
HYBRID_W_EMB = 0.6
HYBRID_W_BM25 = 0.4
CANDIDATE_POOL_MIN = 8
CANDIDATE_POOL_MULT = 2
RetrievalMode = Literal["bm25", "vector", "hybrid"]
RETRIEVAL_MODES: tuple[RetrievalMode, ...] = ("bm25", "vector", "hybrid")

# Load synonyms for query expansion
SYN_PATH = Path(__file__).parent.parent.parent.parent / "rag_index" / "synonyms.json"
SYN = load_synonyms(str(SYN_PATH))

# Lazy singletons
_model: SentenceTransformer | None = None
_store: RAGStore | None = None
_bm25: BM25Okapi | None = None
_tokenized: list[list[str]] | None = None


class QueryParts(TypedDict):
    base: str
    embed: str
    bm25: list[str]


def retrieval_mode_flags(mode: str) -> tuple[bool, bool]:
    """Return ``(use_vector, use_bm25)`` for a supported retrieval mode."""
    if mode == "bm25":
        return False, True
    if mode == "vector":
        return True, False
    if mode == "hybrid":
        return True, True
    raise ValueError(
        f"unsupported RAG_RETRIEVAL_MODE={mode!r}; expected bm25 | vector | hybrid"
    )


def _get_model() -> SentenceTransformer:
    if SentenceTransformer is None:
        raise RuntimeError("RAG embedding dependencies are not installed")
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _tokenize(text: str) -> list[str]:
    """
    Improved tokenization for BM25: handles hyphens, slashes, and other special characters
    """
    return re.findall(r"[a-z0-9]+", text.lower())


def _maybe_init_bm25(corpus_texts: list[str]) -> None:
    """
    Build BM25 over plain tokenized chunks (very lightweight).
    Safe to call multiple times — builds once.
    """
    global _bm25, _tokenized, BM25Okapi
    if BM25Okapi is None or _bm25 is not None:
        return
    # improved tokenizer with regex for better handling of special characters
    _tokenized = [_tokenize(t) for t in corpus_texts]
    _bm25 = BM25Okapi(_tokenized)


def init_retriever() -> bool:
    """call once at app startup to prepare store/BM25"""
    global _store
    _store = RAGStore()  # assume faiss/meta is loaded internally

    # BM25 corpus text: assume store exposes meta
    try:
        corpus = _store.get_corpus_texts()  # type: ignore[attr-defined]
        if isinstance(corpus, list) and corpus:
            _maybe_init_bm25(corpus)
    except Exception:
        # store may not have corpus method → skip BM25
        pass
    return True


def make_query(summary: dict[str, Any]) -> QueryParts:
    """create expanded query from flags + codes/labels + HPI/ROS (domain-tagged)"""
    parts: list[str] = []
    flags = summary.get("flags", {}) or {}

    # Existing flag-based queries
    if flags.get("ischemic_features"):
        parts += [
            "chest pain",
            "ischemia",
            "ECG",
            "troponin",
            "risk stratification",
            "outpatient evaluation",
        ]
    if flags.get("dm_followup"):
        parts += [
            "type 2 diabetes",
            "HbA1c frequency",
            "lipid management",
            "ADA standards",
        ]

    # Code/label enhancement
    codes = summary.get("codes", {}) or {}
    icds = codes.get("icd", []) if isinstance(codes.get("icd"), list) else []
    cpts = codes.get("cpt", []) if isinstance(codes.get("cpt"), list) else []
    labels = codes.get("labels", []) if isinstance(codes.get("labels"), list) else []

    parts += icds[:3] + cpts[:3] + labels[:5]

    # Chief complaint enhancement
    cc = summary.get("cc", "")
    if cc and isinstance(cc, str):
        parts.append(cc)

    if not parts:
        # minimum fallback: include part of HPI keywords in query (truncate if too long)
        hpi = (summary.get("hpi") or "")[:140]
        parts = [hpi] if hpi else ["primary care evaluation"]

    base_query = " ".join(parts)

    # Query expansion for better retrieval
    embed_query = expand_query_text(base_query, SYN, max_total=40)
    bm25_query = (
        expand_bm25_terms(
            base_query,
            SYN,
            max_per_term=6,
            max_total=40,
        )
        if settings.bm25_query_expansion
        else _tokenize(base_query)
    )

    # Boost key terms for ischemic features
    key_terms = (
        ["troponin", "ecg", "chest pain", "ischemia"]
        if flags.get("ischemic_features")
        else []
    )
    boosted_query = boost_key_terms(embed_query, SYN, key_terms)

    return {"base": base_query, "embed": boosted_query, "bm25": bm25_query}


def _minmax_norm(scores: list[float]) -> list[float]:
    if not scores:
        return scores
    lo = min(scores)
    hi = max(scores)
    if hi <= lo + 1e-12:
        return [0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


def _merge_scores(
    emb_results: list[tuple[int, float]],
    bm25_results: list[tuple[int, float]],
    w_emb: float = 0.6,
    w_bm25: float = 0.4,
) -> list[tuple[int, float]]:
    """
    emb_results/bm25_results: [(idx, score)], different order/length possible.
    normalize and merge scores for same idx.
    """
    # index set
    idxs = sorted({i for i, _ in emb_results} | {i for i, _ in bm25_results})

    emb_map = {i: s for i, s in emb_results}
    bm_map = {i: s for i, s in bm25_results}

    # extract and normalize score vectors in same order
    emb_vec = [emb_map.get(i, 0.0) for i in idxs]
    bm_vec = [bm_map.get(i, 0.0) for i in idxs]

    emb_norm = _minmax_norm(emb_vec)
    bm_norm = _minmax_norm(bm_vec)

    merged = []
    for i, e, b in zip(idxs, emb_norm, bm_norm, strict=False):
        merged.append((i, w_emb * e + w_bm25 * b))
    # sort by score descending
    merged.sort(key=lambda x: x[1], reverse=True)
    return merged


def candidate_pool_size(k: int) -> int:
    return max(CANDIDATE_POOL_MIN, k * CANDIDATE_POOL_MULT)


def merge_retrieval_channels(
    emb_hits: list[tuple[int, float]],
    bm_hits: list[tuple[int, float]],
    *,
    w_emb: float = HYBRID_W_EMB,
    w_bm25: float = HYBRID_W_BM25,
) -> list[tuple[int, float]]:
    """Merge FAISS and BM25 candidate lists with the production empty-channel guards."""
    if emb_hits and bm_hits:
        return _merge_scores(emb_hits, bm_hits, w_emb=w_emb, w_bm25=w_bm25)
    if emb_hits:
        idxs = [i for i, _ in emb_hits]
        norm = _minmax_norm([s for _, s in emb_hits])
        return list(zip(idxs, norm, strict=False))
    return list(bm_hits)


def rank_channels(
    query_dict: QueryParts,
    *,
    store: RAGStore,
    model: Any | None,
    bm25: Any | None,
    k: int,
    use_vector: bool = True,
    use_bm25: bool = True,
) -> list[tuple[int, float]]:
    """Rank corpus indices using the production candidate pool and merge."""
    pool = candidate_pool_size(k)
    emb_hits: list[tuple[int, float]] = []
    if use_vector:
        if model is None:
            raise RuntimeError("vector ranking requires an embedding model")
        q_emb = model.encode([query_dict["embed"]], normalize_embeddings=True)
        emb_hits = store.search(q_emb, top_k=pool)
    bm_hits: list[tuple[int, float]] = []
    if use_bm25 and bm25 is not None:
        scores = bm25.get_scores(query_dict["bm25"])
        bm_hits = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[
            :pool
        ]
    return merge_retrieval_channels(emb_hits, bm_hits)[:k]


def retrieve(
    summary: dict[str, Any],
    k: int = RAG_TOPK,
    *,
    mode: RetrievalMode | None = None,
) -> list[Retrieval]:
    """Rank chunks using the configured retrieval mode.

    ``bm25`` uses BM25Okapi only. ``vector`` uses MiniLM/FAISS only.
    ``hybrid`` keeps the existing 0.6/0.4 MiniLM+BM25 merge. MiniLM is loaded
    only when the selected mode needs vector encoding.
    """
    resolved = settings.rag_retrieval_mode if mode is None else mode
    use_vector, use_bm25 = retrieval_mode_flags(resolved)
    logger.info("retrieval mode=%s", resolved)
    if not USE_RAG:
        logger.info("retrieval skipped rag_enabled=false")
        return []

    if _store is None:
        # defensive code for user who doesn't call init_retriever
        try:
            init_retriever()
        except Exception:
            return []

    if _store is None:
        return []

    try:
        query_dict = make_query(summary)
        model = _get_model() if use_vector else None
        merged = rank_channels(
            query_dict,
            store=_store,
            model=model,
            bm25=_bm25 if use_bm25 else None,
            k=k,
            use_vector=use_vector,
            use_bm25=use_bm25,
        )
        logger.info("retrieval returned %s hits", len(merged))
        if not merged:
            return []

        results: list[Retrieval] = []
        for idx, score in merged:
            meta = _store.get_meta(
                idx,
            )  # {'id','title','source','text','file','start','end','url',...}
            results.append({"chunk": meta, "score": float(round(score, 4))})  # type: ignore
        return results

    except Exception:
        # fallback to empty results on any error
        return []
