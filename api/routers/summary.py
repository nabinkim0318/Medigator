# api/routers/summary.py
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from api.core.provenance import provenance
from api.services.llm.service import llm_service

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("")
async def summarize(intake: dict[str, Any] = Body(...)):
    """Structured intake → HPI/ROS/flags JSON (LLM Summarizer API from diagram)"""
    try:
        data = await llm_service.summary(intake)
        meta = data.get("_metadata") if isinstance(data, dict) else None
        source = (meta or {}).get("provenance") or provenance(
            source="unknown",
            note="Summary returned without provenance metadata",
        )
        return {"summary": data, "provenance": source}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"summary failed: {e!s}")
