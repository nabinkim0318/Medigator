# api/services/llm/gate.py
from api.middleware.phi_redactor import redact_obj


def guard_and_redact(payload: dict) -> dict:
    """
    Redact obvious identifier patterns before external transmission.

    DEMO_MODE does not make identifiers safe. This is heuristic redaction,
    not de-identification and not a production control.
    """
    return redact_obj(payload)
