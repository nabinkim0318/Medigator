# api/middleware/phi_redactor.py
import re
from typing import Any, Dict

# Simple Safe-Harbor candidates (for demo): needs strengthening for production
_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),                  # SSN
    re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),      # Phone number
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),                  # YYYY-MM-DD
    # re.compile(r"\b(?:19|20)\d{2}\b"),                  # Allow standalone years (for Evidence year display)
    re.compile(r"\b[A-Z0-9]{6,10}\b"),                     # ID candidates (consider narrowing if too broad)
    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),             # ZIP
]

def _redact_text(s: str) -> str:
    out = s
    for p in _PATTERNS:
        out = p.sub("[REDACTED]", out)
    return out

def redact_obj(o: Any) -> Any:
    if isinstance(o, str):
        return _redact_text(o)
    if isinstance(o, dict):
        return {k: redact_obj(v) for k, v in o.items()}
    if isinstance(o, list):
        return [redact_obj(v) for v in o]
    return o
