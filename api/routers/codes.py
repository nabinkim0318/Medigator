# api/routers/codes.py
from fastapi import APIRouter, Body
import logging
from typing import Dict, Any
from api.services.codes import generate_codes

# Get logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/codes", tags=["codes"])

@router.post("")
def codes(summary: Dict[str,Any] = Body(...), intake: Dict[str,Any] = Body(None), emr: Dict[str,Any] = Body(None)):
    logger.info("Code generation request received")
    try:
        result = generate_codes(summary, intake or {}, emr or {})
        logger.info(f"Generated codes: {len(result.get('icd', []))} ICD, {len(result.get('cpt', []))} CPT, {len(result.get('em', []))} EM")
        return result
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}")
        raise
