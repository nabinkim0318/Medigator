# api/routers/intake.py
import sqlite3
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.intake.tokens import mk_token, verify

router = APIRouter(prefix="/intake", tags=["intake"])


class StartIn(BaseModel):
    patient_hint: str | None = None
    ttl_hours: int = 8


@router.post("/start")
def start(body: StartIn):
    sid = str(uuid.uuid4())
    token, exp = mk_token(sid, ttl_sec=body.ttl_hours * 3600)
    expires_at = datetime.fromtimestamp(exp, tz=UTC).isoformat()
    with sqlite3.connect("data/app.db") as c:
        c.execute(
            """INSERT INTO intake_session(id, token, status, patient_hint, expires_at)
                     VALUES(?,?,?,?,?)""",
            (sid, token, "PENDING", body.patient_hint, expires_at),
        )
        c.commit()
    return {"session_id": sid, "link": f"https://app.local/intake/{token}"}


@router.get("/{token}")
def load(token: str):
    v = verify(token)
    if not v:
        raise HTTPException(401, "invalid token")
    with sqlite3.connect("data/app.db") as c:
        row = c.execute(
            "SELECT id,status,expires_at FROM intake_session WHERE token=?",
            (token,),
        ).fetchone()
    if not row:
        raise HTTPException(404, "not found")
    sid, status, exp = row
    if status != "PENDING":
        raise HTTPException(410, "already used")
    if datetime.fromisoformat(exp) < datetime.utcnow().replace(tzinfo=None):
        raise HTTPException(410, "expired")
    # Fixed 6-question example
    questions = [
        {"id": "cc", "label": "What is your main symptom?"},
        {"id": "onset", "label": "When did it start?"},
        {"id": "exertion", "type": "bool", "label": "Worse with exertion?"},
        {"id": "relievedByRest", "type": "bool", "label": "Relieved by rest?"},
        {
            "id": "associated",
            "type": "multi",
            "options": ["shortness of breath", "diaphoresis", "nausea"],
        },
        {"id": "radiation", "label": "Does the pain radiate?"},
    ]
    return {"valid": True, "session_id": sid, "questions": questions}


class SubmitIn(BaseModel):
    answers: dict


@router.post("/{token}/submit")
def submit(token: str, body: SubmitIn):
    v = verify(token)
    if not v:
        raise HTTPException(401, "invalid token")
    with sqlite3.connect("data/app.db") as c:
        row = c.execute(
            "SELECT id,status,expires_at FROM intake_session WHERE token=?",
            (token,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "not found")
        sid, status, exp = row
        if status != "PENDING":
            raise HTTPException(410, "already used")
        if datetime.fromisoformat(exp) < datetime.utcnow().replace(tzinfo=None):
            raise HTTPException(410, "expired")
        c.execute(
            "INSERT OR REPLACE INTO intake_payload(session_id, answers_json) VALUES(?, json(?))",
            (sid, __import__("json").dumps(body.answers)),
        )
        c.execute(
            "UPDATE intake_session SET status='SUBMITTED', submitted_at=datetime('now') WHERE id=?",
            (sid,),
        )
        c.commit()
    # Async pipeline trigger (summary/code/RAG)
    # enqueue_job("build_report", session_id=sid)
    return {"ok": True, "session_id": sid}
