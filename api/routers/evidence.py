# api/routers/evidence.py
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
import time
from typing import Any

from fastapi import APIRouter, Body

from services.evidence import select_evidence as static_cards
from services.rag.retrieve import USE_RAG, init_retriever, retrieve
from services.rag.summarize import to_cards

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evidence", tags=["evidence"])

_initialized = False
_CACHE: dict[str, tuple[float, dict]] = {}  # key -> (ts, response)
_CACHE_TTL = 120.0  # seconds


def _ensure_init():
    global _initialized
    if not _initialized and USE_RAG:
        try:
            init_retriever()
            _initialized = True
        except Exception as e:
            logger.warning(f"RAG init failed → static only: {e!s}")


def _hash_payload(p: dict) -> str:
    """요약/코드/플래그 변화에만 반응하도록 정규화"""
    keys = ["hpi", "ros", "cc", "flags", "codes"]
    base = {k: p.get(k) for k in keys}
    blob = json.dumps(base, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def _dedupe(cards: list[dict]) -> list[dict]:
    """중복 제거 (title, year, section 기준)"""
    seen = set()
    out = []
    for c in cards:
        key = (
            c.get("title", "").strip().lower(),
            str(c.get("year", "")),
            c.get("section", "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


async def _rag_cards(
    summary: dict[str, Any], timeout_ms: int = 600, k: int = 6, max_cards: int = 2
) -> list[dict]:
    """RAG 카드 추출 with timeout and jitter"""
    if not USE_RAG:
        return []

    try:
        # retrieve()는 sync → executor로
        # Add jitter to prevent thundering herd
        jitter = random.randint(-100, 150)  # nosec S311
        t = (timeout_ms + jitter) / 1000.0
        rets = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, lambda: retrieve(summary, k=k)),
            timeout=t,
        )

        # 키워드 하이라이트용 추출(옵션)
        flags = list((summary.get("flags") or {}).keys())
        codes = summary.get("codes") or {}
        kw = (
            flags
            + (codes.get("icd") or [])[:3]
            + (codes.get("cpt") or [])[:3]
            + (codes.get("labels") or [])[:5]
        )

        return to_cards(rets, max_cards=max_cards, keywords=kw)  # type: ignore
    except Exception as e:
        logger.info(f"RAG timeout/fail → []: {e!s}")
        return []


@router.post("")
async def evidence(summary: dict[str, Any] = Body(...)):
    """상위 2개 에비던스 추출 with 캐시/중복제거/랭킹"""
    _ensure_init()

    # 캐시 체크
    ck = _hash_payload(summary)
    now = time.time()
    hit = _CACHE.get(ck)
    if hit and now - hit[0] < _CACHE_TTL:
        logger.info("Cache hit for evidence request")
        return hit[1]

    # 1) RAG 우선 (최대 2장)
    rag = await _rag_cards(summary, timeout_ms=600, k=8, max_cards=2)
    logger.info(f"Retrieved {len(rag)} RAG evidence cards")

    # 2) 정적 카드 보충
    static = static_cards(summary)
    logger.info(f"Retrieved {len(static)} static evidence cards")

    # 3) 결합: RAG 먼저, 중복 제거, 상한 2
    merged = _dedupe(rag + static)[:2]

    # 4) rank 재부여(1..n), score 없으면 0.0
    for i, c in enumerate(merged, 1):
        c["rank"] = i
        c.setdefault("score", 0.0)

    resp = {"items": merged}  # ← UI가 받는 최종 스키마
    _CACHE[ck] = (now, resp)

    logger.info(f"Returning {len(merged)} evidence cards with ranking")
    return resp
