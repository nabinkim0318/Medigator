# api/services/rag/retrieve.py
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

from sentence_transformers import SentenceTransformer

from .query_expand import (
    bm25_or_clause,
    boost_key_terms,
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

# Load synonyms for query expansion
SYN_PATH = Path(__file__).parent.parent.parent.parent / "rag_index" / "synonyms.json"
SYN = load_synonyms(str(SYN_PATH))

# Lazy singletons
_model: SentenceTransformer | None = None
_store: RAGStore | None = None
_bm25: BM25Okapi | None = None
_tokenized: list[list[str]] | None = None


def _get_model() -> SentenceTransformer:
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


def make_query(summary: dict[str, Any]) -> dict[str, str]:
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
    bm25_query = bm25_or_clause(base_query, SYN, max_per_term=6)

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


def retrieve(summary: dict[str, Any], k: int = RAG_TOPK) -> list[Retrieval]:
    """
    hybrid search: embedding(required) + BM25(optional) → weighted rerank → top-k
    return: List[Retrieval] with {'chunk': meta_dict, 'score': float}
    """
    logger.info(f"RAG retrieval started with k={k}")
    if not USE_RAG:
        logger.info("RAG disabled, returning empty results")
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
        # 1) Generate expanded queries
        query_dict = make_query(summary)
        embed_query = query_dict["embed"]
        bm25_query = query_dict["bm25"]

        logger.debug(f"Base query: {query_dict['base']}")
        logger.debug(f"Embed query: {embed_query}")
        logger.debug(f"BM25 query: {bm25_query}")

        # 2) embedding ANN with expanded query
        q_emb = _get_model().encode([embed_query], normalize_embeddings=True)
        emb_hits: list[tuple[int, float]] = _store.search(
            q_emb,
            top_k=max(8, k * 2),
        )  # [(idx, score)]
        logger.info(f"Embedding search returned {len(emb_hits)} hits")

        # 3) BM25 with expanded query (optional)
        bm_hits: list[tuple[int, float]] = []
        if _bm25 is not None and _tokenized is not None:
            # Use expanded BM25 query for better keyword matching
            q_tokens = _tokenize(bm25_query)  # use expanded query
            # BM25 scores are generated for all documents → take top n
            scores = _bm25.get_scores(q_tokens)  # type: ignore[union-attr]
            bm_hits = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[
                : max(8, k * 2)
            ]

        # 3) rerank with empty result guards
        if emb_hits and bm_hits:
            # both available - merge scores
            merged = _merge_scores(emb_hits, bm_hits, w_emb=0.6, w_bm25=0.4)
        elif emb_hits:
            # only embedding results available
            idxs = [i for i, _ in emb_hits]
            norm = _minmax_norm([s for _, s in emb_hits])
            merged = list(zip(idxs, norm, strict=False))
        elif bm_hits:
            # only BM25 results available - fallback
            merged = bm_hits
        else:
            # no results from either method
            return []

        # 4) Top-k meta combination
        top = merged[:k]
        results: list[Retrieval] = []
        for idx, score in top:
            meta = _store.get_meta(
                idx,
            )  # {'id','title','source','text','file','start','end','url',...}
            # Retrieval type: {"chunk": meta, "score": float}
            results.append({"chunk": meta, "score": float(round(score, 4))})  # type: ignore
        return results

    except Exception:
        # fallback to empty results on any error
        return []
