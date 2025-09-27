# api/services/rag/__init__.py
"""
RAG (Retrieval-Augmented Generation) module for medical document search.

This module provides:
- Document indexing with FAISS
- Hybrid search (embedding + BM25)
- Evidence retrieval for medical summaries
"""

from .retrieve import retrieve, init_retriever, make_query
from .index import build_index
from .store import RAGStore
from .summarize import to_cards
from .types import DocChunk, Retrieval, EvidenceCard

__all__ = [
    "retrieve",
    "init_retriever", 
    "make_query",
    "build_index",
    "RAGStore",
    "to_cards",
    "DocChunk",
    "Retrieval", 
    "EvidenceCard"
]
