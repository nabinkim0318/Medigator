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


def test_summary_declares_fallback_or_openai_provenance(client: TestClient):
    res = client.post(
        "/api/v1/summary",
        json={
            "encounterId": "demo-prov-1",
            "patient": {"age": 55, "sex": "M"},
            "answers": {"cc": "chest pain"},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert "summary" in body
    prov = body["provenance"]
    assert prov["source"] in {"openai", "fallback"}
    if prov["source"] == "fallback":
        assert "not a model diagnosis" in prov["note"].lower()


def test_codes_declare_rules_provenance(client: TestClient):
    res = client.post(
        "/api/v1/codes",
        json={"summary": {"flags": {}}, "intake": {}, "emr": {}},
    )
    assert res.status_code == 200
    prov = res.json()["provenance"]
    assert prov["source"] == "rules"
    assert "not automatic clinical coding" in prov["note"].lower()


def test_evidence_declares_rag_or_static_provenance(client: TestClient):
    res = client.post("/api/v1/evidence", json={"hpi": "chest pain", "flags": {}})
    assert res.status_code == 200
    body = res.json()
    assert "items" in body
    assert body["provenance"]["source"] in {"rag", "static"}


def test_llm_health_does_not_claim_healthy_without_client(
    client: TestClient, monkeypatch
):
    monkeypatch.setattr(
        "api.routers.llm.get_client_status",
        lambda: {
            "available": False,
            "provenance": {
                "source": "none",
                "provider": None,
                "model": "gpt-4o-mini",
                "has_api_key": False,
            },
        },
    )
    res = client.get("/api/v1/llm/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] != "healthy"
    assert body["available"] is False
    assert body["provenance"]["source"] == "none"
