# api/services/rag/__init__.py
"""
RAG (Retrieval-Augmented Generation) module for medical document search.

This module provides:
- Document indexing with FAISS
- Hybrid search (embedding + BM25)
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
