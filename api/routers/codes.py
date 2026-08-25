# api/routers/codes.py
import logging
from typing import Any

from fastapi import APIRouter, Body

from api.core.provenance import provenance
from api.services.codes import generate_codes

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/codes", tags=["codes"])


@router.post("")
def codes(
    summary: dict[str, Any] = Body(...),
    intake: dict[str, Any] = Body(None),
    emr: dict[str, Any] = Body(None),
):
    """Research-prototype ICD suggestions; CPT rule matching is not active."""
    logger.info("Code generation request received")
    try:
        result = generate_codes(summary, intake or {}, emr or {})
        result["provenance"] = provenance(
            source="rules",
            provider="local-csv",
            note=(
                "CSV-based ICD suggestions; loaded CPT rules "
                "currently have no active predicates. "
                "Not automatic clinical coding."
            ),
        )
        logger.info(
            "Generated codes: %s ICD, %s CPT, %s EM",
            len(result.get("icd", [])),
            len(result.get("cpt", [])),
            len(result.get("em", [])),
        )
        return result
    except Exception:
        logger.error("Code generation failed")
        raise
