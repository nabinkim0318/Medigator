# tests/test_rag.py
import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _summary(flags):
    return {
        "hpi": "Chest pain with exertion",
        "ros": {
            "cardiovascular": {"positive": ["chest pain"], "negative": []},
            "respiratory": {"positive": ["shortness of breath"], "negative": []},
            "constitutional": {"positive": [], "negative": []},
        },
        "pmh": [],
        "meds": [],
        "flags": flags,
    }


def test_chest_pain_cards(client):
    body = _summary({"ischemic_features": True, "dm_followup": False, "labs_a1c_needed": False})
    resp = client.post("/api/v1/evidence", json=body).json()
    assert resp["evidence"], "should return at least one evidence card"
