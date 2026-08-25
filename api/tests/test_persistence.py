from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from api.core.access import reset_operator_sessions
from api.core.config import settings
from api.core.database import CANONICAL_RELATIVE_PATH, REPO_ROOT, connect_db
from api.main import app
from api.routers.notifications import (
    _ensure_notifications_table_exists,
    _get_db_connection as notifications_connect,
)
from api.routers.patient import (
    _ensure_table_exists,
    _get_db_connection as patient_connect,
)
from api.services.rules import rules_service


SYNTHETIC_APPOINTMENT = {
    "session_id": "demo-persist-1",
    "patientData": {
        "name": "Demo Patient",
        "age": 40,
        "gender": "Female",
        "bloodGroup": "O+",
        "phone": "5550101234",
        "email": "demo.patient@example.com",
    },
    "appointmentData": {"q1": "chest pain", "q2": "middle of chest"},
}


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "DEMO_ACCESS_CODE", "test-operator-code")
    monkeypatch.setattr(settings, "SYNTHETIC_DATA_ONLY", True)
    monkeypatch.setattr(settings, "DEMO_MODE", True)
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{tmp_path / 'test.db'}")
    reset_operator_sessions()
    with TestClient(app) as c:
        yield c
    reset_operator_sessions()


def operator_headers(client: TestClient) -> dict[str, str]:
    res = client.post(
        "/api/v1/auth/demo-operator", json={"access_code": "test-operator-code"}
    )
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['operator_session']}"}


def test_patient_write_is_visible_to_analytics(client: TestClient, tmp_path):
    created = client.post("/api/v1/patient/appointment", json=SYNTHETIC_APPOINTMENT)
    assert created.status_code == 200

    headers = operator_headers(client)
    listed = client.get("/api/v1/patient/profile", headers=headers)
    assert listed.status_code == 200
    profiles = listed.json()["profiles"]
    assert profiles
    assert profiles[0]["profile"]["email"] == "demo.patient@example.com"

    dash = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash.status_code == 200
    assert dash.json()["total_patients"] >= 1
    assert (tmp_path / "test.db").exists()
    assert (tmp_path / "test.db").resolve() != (
        REPO_ROOT / CANONICAL_RELATIVE_PATH
    ).resolve()


def test_patient_and_notifications_helpers_share_tmp_db(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{tmp_path / 'shared.db'}")

    conn = patient_connect()
    _ensure_table_exists(conn)
    conn.execute(
        """
        INSERT INTO intake_session (id, token, status, expires_at)
        VALUES ('sess-1', 'demo-shared-token', 'PENDING', '2099-01-01')
        """
    )
    conn.commit()
    conn.close()

    other = notifications_connect()
    _ensure_notifications_table_exists(other)
    row = other.execute(
        "SELECT token FROM intake_session WHERE id = ?", ("sess-1",)
    ).fetchone()
    tables = {
        r["name"]
        for r in other.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    other.close()

    assert row["token"] == "demo-shared-token"
    assert "intake_session" in tables
    assert "notifications" in tables
    assert (tmp_path / "shared.db").exists()


def test_rules_service_reads_the_configured_db(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{tmp_path / 'rules.db'}")
    conn = connect_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS symptom_icd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptom TEXT,
            icd_code TEXT,
            icd_description TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO symptom_icd (symptom, icd_code, icd_description) VALUES (?, ?, ?)",
        ("demo headache", "R51", "synthetic demo mapping"),
    )
    conn.commit()
    conn.close()

    import asyncio

    rows = asyncio.run(rules_service.get_symptom_icd_mapping("headache"))
    assert rows
    assert rows[0]["icd_code"] == "R51"
