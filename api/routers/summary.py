# api/routers/summary.py
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException
from core.schemas import SummaryIn, SummaryOut
from services.llm.tasks.summarize import run as summarize_run

from api.services.llm.service import llm_service

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("")
async def summarize(intake: dict[str, Any] = Body(...)):
    """Structured intake → HPI/ROS/flags JSON (다이어그램의 LLM Summarizer API)"""
    try:
        data = await llm_service.summary(intake)
        return {"summary": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"summary failed: {e!s}")
