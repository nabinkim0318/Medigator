from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from api.core.access import reset_operator_sessions
from api.core.config import settings
from api.core.safe_logging import sanitize_text
from api.main import app

CANARY_SSN = "123-45-6789"
CANARY_EMAIL = "patient.leak@gmail.com"
CANARY_TOKEN = "super-secret-patient-token"
CANARY_QUERY = "left-arm crushing pain with diaphoresis"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "DEMO_ACCESS_CODE", "test-operator-code")
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{tmp_path / 'log.db'}")
    reset_operator_sessions()
    with TestClient(app) as c:
        yield c
    reset_operator_sessions()


def test_sanitize_text_redacts_sensitive_patterns():
    blob = f"token={CANARY_TOKEN} ssn={CANARY_SSN} mail={CANARY_EMAIL} Bearer abcdefghijklmnop"
    out = sanitize_text(blob)
    assert CANARY_SSN not in out
    assert CANARY_EMAIL not in out
    assert "Bearer [REDACTED]" in out


def test_validation_error_does_not_log_body(client: TestClient, caplog):
    caplog.set_level(logging.WARNING)
    payload = {
        "session_id": CANARY_TOKEN,
        "patientData": {"email": CANARY_EMAIL, "ssn": CANARY_SSN},
        "appointmentData": "not-an-object",
    }
    res = client.post("/api/v1/patient/appointment", json=payload)
    assert res.status_code == 422
    text = caplog.text
    assert CANARY_SSN not in text
    assert CANARY_EMAIL not in text
    assert CANARY_TOKEN not in text
    assert "appointmentData" not in text or "validation_failed" in text
    assert '"body"' not in text
    assert "not-an-object" not in text


def test_disabled_route_does_not_log_query(client: TestClient, caplog):
    caplog.set_level(logging.INFO)
    res = client.get(f"/api/v1/patient/search?query={CANARY_QUERY}")
    assert res.status_code == 403
    assert CANARY_QUERY not in caplog.text


def test_synthetic_rejection_does_not_log_identifiers(client: TestClient, caplog):
    caplog.set_level(logging.INFO)
    res = client.post(
        "/api/v1/patient/appointment",
        json={
            "session_id": CANARY_TOKEN,
            "patientData": {
                "name": "Real Person",
                "age": 44,
                "gender": "Female",
                "phone": "4155550199",
                "email": CANARY_EMAIL,
            },
            "appointmentData": {"q1": CANARY_QUERY},
        },
    )
    assert res.status_code == 400
    assert CANARY_EMAIL not in caplog.text
    assert CANARY_QUERY not in caplog.text
    assert CANARY_TOKEN not in caplog.text
