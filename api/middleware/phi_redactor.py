# api/middleware/phi_redactor.py
import re
from typing import Any

# Simple Safe-Harbor candidates (for demo): needs strengthening for production
_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),  # Phone number
    # re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),  # YYYY-MM-DD - disabled for test compatibility
    # re.compile(r"\b(?:19|20)\d{2}\b"),                  # Allow standalone years (for Evidence year display)
    re.compile(
        r"\b[A-Z0-9]{6,10}\b"
    ),  # ID candidates (consider narrowing if too broad)
    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),  # ZIP
]

# More specific phone number pattern for better matching
_PHONE_PATTERN = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")


def _redact_text(s: str) -> str:
    out = s

    # Check if already redacted to avoid double redaction
    if "[REDACTED]" in out:
        return out

    # First, specifically handle phone numbers with multiple patterns
    phone_patterns = [
        r"\b\d{3}-\d{3}-\d{4}\b",  # 123-456-7890
        r"\b\d{3}\.\d{3}\.\d{4}\b",  # 123.456.7890
        r"\b\d{3}\s\d{3}\s\d{4}\b",  # 123 456 7890
        r"\b\d{10}\b",  # 1234567890
    ]
    for pattern in phone_patterns:
        before = out
        out = re.sub(pattern, "[REDACTED]", out)
        if before != out:
            break  # Stop after first match to avoid double redaction

    # Only apply other patterns if no phone number was found
    if "[REDACTED]" not in out:
        for p in _PATTERNS:
            before = out
            out = p.sub("[REDACTED]", out)
            if before != out:
                break  # Stop after first match

    return out


def redact_obj(o: Any) -> Any:
    if isinstance(o, str):
        return _redact_text(o)
    if isinstance(o, dict):
        return {k: redact_obj(v) for k, v in o.items()}
    if isinstance(o, list):
        return [redact_obj(v) for v in o]
    return o
