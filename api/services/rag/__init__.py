# api/services/rag/__init__.py
"""
RAG (Retrieval-Augmented Generation) module for medical document search.

This module provides:
- Document indexing with FAISS and per-file build provenance
- Runtime search modes: BM25, MiniLM/FAISS, and 0.6/0.4 hybrid
- Evidence retrieval for medical summaries
"""

from .index import build_index
from .retrieve import init_retriever, make_query, retrieve
from .store import RAGStore
from .summarize import to_cards
from .types import DocChunk, EvidenceCard, Retrieval

__all__ = [
    "DocChunk",
    "EvidenceCard",
    "RAGStore",
    "Retrieval",
    "build_index",
    "init_retriever",
    "make_query",
    "retrieve",
    "to_cards",
]
