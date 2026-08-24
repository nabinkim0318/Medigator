# api/routers/compliance.py
from fastapi import APIRouter

from api.core.config import settings
from api.services.llm.client import get_client_status

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("")
def compliance_status():
    return {
        "demo_mode": settings.DEMO_MODE,
        "hipaa_mode": settings.HIPAA_MODE,
        "llm": get_client_status(),
        "logging": {"store_bodies": False},
        "disclaimer": (
            "Synthetic/demo data only. DEMO_MODE does not make real identifiers safe. "
            "Not a production security control."
        ),
    }
