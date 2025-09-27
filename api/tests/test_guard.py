# api/tests/test_guard.py
import pytest
from api.core.config import settings
from api.services.llm.gate import guard_and_redact

def test_redact_phone_in_hipaa(monkeypatch):
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "HIPAA_MODE", True)
    data = {"note": "Call 404-555-1212 on 2024-09-01", "patient": {"name": "John"}}
    out = guard_and_redact(data)
    assert "[REDACTED]" in out["note"]
