# api/routers/compliance.py
from fastapi import APIRouter

from core.config import settings
from services.llm.client import get_client_status

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("")
def compliance_status():
    return {
        "demo_mode": settings.DEMO_MODE,
        "hipaa_mode": settings.HIPAA_MODE,
        "llm": get_client_status(),
        "logging": {"store_bodies": False},
        "disclaimer": (
            "Demo only. No real PHI." if settings.DEMO_MODE else "Not for diagnosis."
        ),
    }
