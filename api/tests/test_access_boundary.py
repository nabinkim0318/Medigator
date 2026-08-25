from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from api.core.access import reset_operator_sessions
from api.core.config import settings
from api.main import app


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
    token = res.json()["operator_session"]
    assert token
    return {"Authorization": f"Bearer {token}"}


def test_health_public(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["synthetic_data_only"] is True


def test_username_login_disabled(client: TestClient):
    res = client.post("/api/v1/auth/login", json={"username": "anyone"})
    assert res.status_code == 403
    assert "username-derived" in res.text.lower() or "disabled" in res.text.lower()


def test_invalid_operator_code(client: TestClient):
    res = client.post("/api/v1/auth/demo-operator", json={"access_code": "wrong"})
    assert res.status_code == 401


def test_patient_profile_list_requires_operator(client: TestClient):
    res = client.get("/api/v1/patient/profile")
    assert res.status_code == 401
    assert res.json()["error"] == "operator_required"


def test_patient_profile_list_with_operator(client: TestClient):
    headers = operator_headers(client)
    res = client.get("/api/v1/patient/profile", headers=headers)
    assert res.status_code == 200
    assert "profiles" in res.json()


def test_direct_api_bypasses_frontend_doctor_route(client: TestClient):
    """UI /DoctorPatientView is not authorization — unauthenticated API still denied."""
    for path in (
        "/api/v1/patient/profile",
        "/api/v1/patient/stats",
        "/api/v1/analytics/dashboard",
    ):
        res = client.get(path)
        assert res.status_code == 401, path


def test_disabled_sensitive_routes(client: TestClient):
    cases = [
        ("GET", "/api/v1/patient/search?query=jane"),
        ("GET", "/api/v1/patient/appointment/not-a-secret"),
        ("GET", "/api/v1/patient/appointment/not-a-secret/summary"),
        ("PUT", "/api/v1/patient/profile/abc"),
        ("GET", "/api/v1/analytics/export/patients"),
        ("GET", "/api/v1/analytics/symptoms/analysis"),
        ("GET", "/api/v1/files/stats"),
        ("GET", "/api/v1/files/download/abc"),
        ("GET", "/api/v1/notifications/stats"),
        ("POST", "/api/v1/rag/build-index"),
    ]
    for method, path in cases:
        res = client.request(method, path, json={})
        assert res.status_code == 403, f"{method} {path} -> {res.status_code}"
        assert res.json()["error"] == "endpoint_disabled"


def test_placeholder_clinical_routes_are_not_implemented(client: TestClient):
    cases = [
        ("POST", "/api/v1/llm/chat"),
        ("POST", "/api/v1/llm/analyze"),
        ("POST", "/api/v1/llm/treatment-plan"),
        ("POST", "/api/v1/reports/pdf"),
        ("GET", "/api/v1/reports/demo/pdf"),
        ("POST", "/api/v1/reports/analyze"),
    ]
    for method, path in cases:
        res = client.request(method, path, json={})
        assert res.status_code == 501, f"{method} {path} -> {res.status_code}"
        body = res.json()
        assert body["error"] == "not_implemented"
        assert "placeholder" in body["message"].lower()


def test_demo_open_summary(client: TestClient):
    res = client.post(
        "/api/v1/summary",
        json={
            "encounterId": "demo-1",
            "patient": {"age": 55, "sex": "M"},
            "answers": {"cc": "chest pain"},
        },
    )
    assert res.status_code not in {401, 403}


def test_synthetic_appointment_allowed(client: TestClient):
    res = client.post(
        "/api/v1/patient/appointment",
        json={
            "session_id": "demo-session-1",
            "patientData": {
                "name": "Demo Patient",
                "age": 40,
                "gender": "Female",
                "bloodGroup": "O+",
                "phone": "5550101234",
                "email": "demo.patient@example.com",
            },
            "appointmentData": {"q1": "chest pain", "q2": "middle of chest"},
        },
    )
    assert res.status_code == 200
    assert "key" in res.json()


def test_real_identifier_appointment_rejected(client: TestClient):
    res = client.post(
        "/api/v1/patient/appointment",
        json={
            "session_id": "demo-session-2",
            "patientData": {
                "name": "Jane Doe",
                "age": 40,
                "gender": "Female",
                "bloodGroup": "O+",
                "phone": "4155551234",
                "email": "jane@gmail.com",
            },
            "appointmentData": {"q1": "chest pain"},
        },
    )
    assert res.status_code == 400
    detail = res.json()["message"]
    assert (
        "synthetic_data_required" in str(detail) or "synthetic" in str(detail).lower()
    )


def test_operator_delete_allowed(client: TestClient):
    created = client.post(
        "/api/v1/patient/profile",
        json={
            "session_id": "demo-session-del",
            "profile": {
                "name": "Demo Patient",
                "age": 41,
                "gender": "Male",
                "bloodGroup": "A+",
                "phone": "5550109999",
                "email": "delete.me@example.com",
            },
        },
    )
    assert created.status_code == 200
    listed = client.get("/api/v1/patient/profile", headers=operator_headers(client))
    assert listed.status_code == 200
    profiles = listed.json()["profiles"]
    assert profiles
    target = profiles[0]["token"]
    denied = client.delete(f"/api/v1/patient/profile/{target}")
    assert denied.status_code == 401
    allowed = client.delete(
        f"/api/v1/patient/profile/{target}", headers=operator_headers(client)
    )
    assert allowed.status_code in {200, 404}
