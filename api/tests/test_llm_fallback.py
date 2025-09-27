# api/tests/test_llm_fallback.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from api.core.schemas import SummaryIn
from api.services.llm.tasks import summarize as task


@pytest.mark.anyio
async def test_no_api_key_falls_back(monkeypatch):
    # Simulate no client
    monkeypatch.setattr("api.services.llm.client.async_client", None)
    body = SummaryIn(
        encounterId="e4",
        patient={"age": 55},
        answers={"cc": "chest pain", "exertion": True, "relievedByRest": True},
    )
    out = await task.run(body)
    assert "reports" in out.hpi.lower()  # templated form
    assert isinstance(out.flags["ischemic_features"], bool)


@pytest.mark.anyio
async def test_json_parse_error_falls_back(monkeypatch):
    async def fake_chat_json(**kwargs):
        raise ValueError("parse error")

    monkeypatch.setattr("api.services.llm.client.chat_json", fake_chat_json)
    body = SummaryIn(encounterId="e5", patient={"age": 40}, answers={"cc": "headache"})
    out = await task.run(body)
    assert isinstance(out.hpi, str)
