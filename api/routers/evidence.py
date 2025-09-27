# api/routers/evidence.py
from __future__ import annotations
import asyncio
import logging
from fastapi import APIRouter, Body
from typing import Dict, Any
from api.services.evidence import select_evidence as static_cards
from api.services.rag.retrieve import retrieve, init_retriever, USE_RAG
from api.services.rag.summarize import to_cards
from api.core.exceptions import RAGServiceException

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evidence", tags=["evidence"])
_initialized = False

def _ensure_init():
    global _initialized
    if not _initialized and USE_RAG:
        try:
            init_retriever()
            _initialized = True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"RAG initialization failed, falling back to static evidence only: {str(e)}")
            # fallback to static evidence only

async def _rag_with_timeout(summary: Dict[str, Any], timeout_ms: int = None) -> list:
    """RAG retrieval with timeout fallback and jitter"""
    if not USE_RAG:
        return []
        
    try:
        # Use asyncio.wait_for for timeout
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, lambda: retrieve(summary, k=4)
            ),
            timeout=timeout_ms / 1000.0
        )
        return to_cards(result, max_cards=2)
    except (asyncio.TimeoutError, Exception):
        return []

@router.post("")
async def evidence(summary: Dict[str, Any] = Body(...)):
    logger.info("Evidence request received")
    _ensure_init()
    
    # Always get static evidence cards
    static = static_cards(summary)
    logger.info(f"Retrieved {len(static)} static evidence cards")
    
    # RAG cards with timeout (400-600ms)
    rag_cards = await _rag_with_timeout(summary, timeout_ms=500)
    logger.info(f"Retrieved {len(rag_cards)} RAG evidence cards")
    
    # combine (max 3 total)
    cards = (static + rag_cards)[:3]
    logger.info(f"Returning {len(cards)} total evidence cards")
    return {"evidence": cards}
