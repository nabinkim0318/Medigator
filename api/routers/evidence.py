# api/routers/evidence.py
from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Body

from services.evidence import select_evidence as static_cards
from services.rag.retrieve import USE_RAG, init_retriever, retrieve
from services.rag.summarize import to_cards

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
            logger.warning(
                f"RAG initialization failed, falling back to static evidence only: {e!s}",
            )
            # fallback to static evidence only


async def _rag_with_timeout(summary: dict[str, Any], timeout_ms: int | None = None) -> list:
    """RAG retrieval with timeout fallback and jitter"""
    if not USE_RAG:
        return []

    try:
        # Use asyncio.wait_for for timeout
        timeout_seconds = (timeout_ms or 500) / 1000.0
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, lambda: retrieve(summary, k=4)),
            timeout=timeout_seconds,
        )
        return to_cards(result, max_cards=2)  # type: ignore
    except (TimeoutError, Exception):
        return []


@router.post("")
async def evidence(summary: dict[str, Any] = Body(...)):
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
