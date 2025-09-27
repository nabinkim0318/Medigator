# api/tests/test_summary.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json, re
import pytest
from api.core.schemas import SummaryIn, SummaryOut
from api.services.llm.tasks import summarize as task
from api.services.llm import validators

FORBIDDEN = validators.FORBIDDEN

@pytest.mark.anyio
async def test_summary_normal(monkeypatch):
    # mock chat_json to avoid network
    async def fake_chat_json(**kwargs):
        return {
            "hpi": "55-year-old male reports 2 hours history of chest pain with radiation to left arm.",
            "ros": {
                "cardiovascular": {"positive": ["chest pain"], "negative": []},
                "respiratory":    {"positive": [], "negative": []},
                "constitutional": {"positive": [], "negative": []}
            },
            "pmh": ["hypertension"],
            "meds": ["lisinopril"],
            "flags": {"ischemic_features": True, "dm_followup": False, "labs_a1c_needed": False}
        }
    monkeypatch.setattr("api.services.llm.client.chat_json", fake_chat_json)

    body = SummaryIn(
        encounterId='e1',
        patient={'age':55, 'sex':'M'},
        answers={'cc':'chest pain','onset':'2 hours','radiation':'left arm','pmh':['hypertension'],'meds':['lisinopril'],'exertion':True,'relievedByRest':True}
    )
    out = await task.run(body)
    assert isinstance(out, SummaryOut)
    assert out.flags["ischemic_features"] is True
    assert "chest pain" in out.hpi.lower()
    assert not FORBIDDEN.search(out.hpi)

@pytest.mark.anyio
async def test_summary_minimal_input(monkeypatch):
    async def fake_chat_json(**kwargs):
        return {
            "hpi": "30-year-old patient reports headache.",
            "ros": {
                "cardiovascular": {"positive": [], "negative": []},
                "respiratory":    {"positive": [], "negative": []},
                "constitutional": {"positive": [], "negative": []}
            },
            "pmh": [], "meds": [], "flags": {"ischemic_features": False, "dm_followup": False, "labs_a1c_needed": False}
        }
    monkeypatch.setattr("api.services.llm.client.chat_json", fake_chat_json)

    body = SummaryIn(encounterId='e2', patient={'age':30}, answers={'cc':'headache','pmh':[],'meds':[]})
    out = await task.run(body)
    SummaryOut.model_validate(out.model_dump())  # schema re-validate
    assert out.ros["cardiovascular"].positive == []

@pytest.mark.anyio
async def test_summary_forbidden_phrase_filtered(monkeypatch):
    # Force model to output forbidden terms; validators should sanitize
    async def fake_chat_json(**kwargs):
        return {
            "hpi": "Diagnosis: MI. Treatment: aspirin. risk 20%. Patient reports chest pain.",
            "ros": { "cardiovascular":{"positive":["chest pain"],"negative":[]},
                     "respiratory":{"positive":[],"negative":[]},
                     "constitutional":{"positive":[],"negative":[]} },
            "pmh": [], "meds": [], "flags": {"ischemic_features": True, "dm_followup": False, "labs_a1c_needed": False}
        }
    monkeypatch.setattr("api.services.llm.client.chat_json", fake_chat_json)

    body = SummaryIn(encounterId='e3', patient={'age':65,'sex':'F'}, answers={'cc':'chest pain'})
    out = await task.run(body)
    assert not FORBIDDEN.search(out.hpi)
