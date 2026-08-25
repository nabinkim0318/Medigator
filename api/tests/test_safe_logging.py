from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from api.core.access import reset_operator_sessions
from api.core.config import settings
from api.core.logging_config import setup_logging
from api.core.safe_logging import SensitiveLogFilter, sanitize_text
from api.main import app
from api.services.llm import service as llm_service_module
from api.services.llm.service import LLMService

CANARY_SSN = "123-45-6789"
CANARY_EMAIL = "patient.leak@gmail.com"
CANARY_PHONE = "415-555-0199"
CANARY_UUID = "123e4567-e89b-12d3-a456-426614174000"
CANARY_TOKEN = "super-secret-patient-token"
CANARY_QUERY = "left-arm crushing pain with diaphoresis"
PATIENT_LIKE_STRINGS = (
    "Alice Wonderland",
    "123 Maple Street",
    "March 14 1990",
    "metformin",
    "sharp pain after walking upstairs",
)


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "DEMO_ACCESS_CODE", "test-operator-code")
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{tmp_path / 'log.db'}")
    reset_operator_sessions()
    with TestClient(app) as c:
        yield c
    reset_operator_sessions()


def test_sanitize_text_redacts_sensitive_patterns():
    blob = (
        f"https://example.test/?access_token={CANARY_TOKEN}&next=value"
        f" ssn={CANARY_SSN} mail={CANARY_EMAIL} phone={CANARY_PHONE}"
        f" id={CANARY_UUID} Bearer abcdefghijklmnop"
    )
    out = sanitize_text(blob)
    assert CANARY_TOKEN not in out
    assert CANARY_SSN not in out
    assert CANARY_EMAIL not in out
    assert CANARY_PHONE not in out
    assert CANARY_UUID not in out
    assert "Bearer [REDACTED]" in out


def test_sensitive_filter_is_attached_to_every_output_handler(tmp_path):
    setup_logging(tmp_path / "logs")

    for handler_name in ("console", "file", "error_file", "security_file"):
        handler = logging.getHandlerByName(handler_name)
        assert handler is not None
        assert any(
            isinstance(handler_filter, SensitiveLogFilter)
            for handler_filter in handler.filters
        )


@pytest.mark.anyio
async def test_summary_excludes_arbitrary_patient_content_from_logs(
    monkeypatch, tmp_path, capsys
):
    logs_dir = tmp_path / "logs"
    setup_logging(logs_dir)

    async def fake_chat_json(**_kwargs):
        return {
            "hpi": "Synthetic patient reports discomfort.",
            "ros": {
                "cardiovascular": {"positive": [], "negative": []},
                "respiratory": {"positive": [], "negative": []},
                "constitutional": {"positive": [], "negative": []},
            },
            "pmh": [],
            "meds": [],
            "flags": {
                "ischemic_features": False,
                "dm_followup": False,
                "labs_a1c_needed": False,
            },
        }

    monkeypatch.setattr(llm_service_module, "chat_json", fake_chat_json)

    await LLMService().summary(
        {
            "name": PATIENT_LIKE_STRINGS[0],
            "address": PATIENT_LIKE_STRINGS[1],
            "date_of_birth": PATIENT_LIKE_STRINGS[2],
            "medications": [PATIENT_LIKE_STRINGS[3]],
            "complaint": PATIENT_LIKE_STRINGS[4],
        }
    )

    for handler in logging.getLogger().handlers:
        handler.flush()
    for logger_name in ("api", "api.services", "security"):
        for handler in logging.getLogger(logger_name).handlers:
            handler.flush()

    console_text = capsys.readouterr().out.casefold()
    file_text = "\n".join(
        (logs_dir / filename).read_text(encoding="utf-8")
        for filename in ("api.log", "error.log", "security.log")
    ).casefold()

    for patient_value in PATIENT_LIKE_STRINGS:
        assert patient_value.casefold() not in console_text
        assert patient_value.casefold() not in file_text

    assert "event=negation_processing_completed field_count=5" in console_text
    assert "event=negation_processing_completed field_count=5" in file_text

    console_handler = logging.getHandlerByName("console")
    assert console_handler is not None
    console_handler.setStream(sys.__stdout__)


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
