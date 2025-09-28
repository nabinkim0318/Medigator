# api/tests/test_guard.py
from api.core.config import settings
from api.services.llm.gate import guard_and_redact


def test_redact_phone_in_hipaa(monkeypatch):
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "HIPAA_MODE", True)
    data = {"note": "Call 404-555-1212 on 2024-09-01", "patient": {"name": "John"}}
    out = guard_and_redact(data)
    # Debug output for CI/CD
    print(f"Original: {data}")
    print(f"Result: {out}")
    print(f"Note contains [REDACTED]: {'[REDACTED]' in out['note']}")
    assert "[REDACTED]" in out["note"]
