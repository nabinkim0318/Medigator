# api/services/llm/gate.py
from api.core.config import settings
from api.middleware.phi_redactor import redact_obj

def guard_and_redact(payload: dict) -> dict:
    # DEMO_MODE: PHI input should be empty (UI should not collect PHI like name/phone etc.)
    # HIPAA_MODE: send to external LLM, at least masking
    if settings.DEMO_MODE:
        return payload  # demo input should be anonymous
    if settings.HIPAA_MODE:
        return redact_obj(payload)
    return payload  # other (internal test)
