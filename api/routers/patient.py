import sqlite3
from datetime import datetime

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/patient", tags=["patient"])


class PatientDataIn(BaseModel):
    token: str
    medicalHistory: dict


@router.post("/patientData")
def submit_patient_data(body: PatientDataIn = Body(...)):
    """Accept onboarding medical history and persist it tied to the user token.

    Request shape:
      { token: str, medicalHistory: { ... } }

    Stores into table `patient_medical_history` with columns (token, payload_json, created_at)
    """
    if not body.token:
        raise HTTPException(status_code=400, detail="token required")

    # Basic persistence using sqlite like other routers
    try:
        with sqlite3.connect("data/app.db") as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS patient_medical_history (token TEXT PRIMARY KEY, payload_json TEXT, created_at TEXT)"
            )
            # Upsert – store latest payload
            c.execute(
                "INSERT OR REPLACE INTO patient_medical_history(token, payload_json, created_at) VALUES(?, json(?), ?)",
                (body.token, __import__("json").dumps(body.medicalHistory), datetime.utcnow().isoformat()),
            )
            c.commit()

        return {"ok": True, "token": body.token}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e!s}")


# --- Appointment endpoints


class AppointmentIn(BaseModel):
    token: str
    appointmentData: dict


@router.post("/appointment")
def create_appointment(body: AppointmentIn = Body(...)):
    """Create a new appointment entry for the user token.

    The server will generate a key like `appointmentData-YYYYMMDDTHHMMSSZ` and store the
    JSON payload. Returns { ok: True, key } on success.
    """
    if not body.token:
        raise HTTPException(status_code=400, detail="token required")
    key = f"appointmentData-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    try:
        with sqlite3.connect("data/app.db") as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS patient_appointments (token TEXT, key TEXT PRIMARY KEY, payload_json TEXT, created_at TEXT)"
            )
            c.execute(
                "INSERT INTO patient_appointments(token, key, payload_json, created_at) VALUES(?, ?, json(?), ?)",
                (body.token, key, __import__("json").dumps(body.appointmentData), datetime.utcnow().isoformat()),
            )
            c.commit()

        return {"ok": True, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e!s}")


@router.put("/appointment/{key}")
def update_appointment(key: str, body: AppointmentIn = Body(...)):
    """Update an existing appointment by key for the provided token."""
    if not body.token:
        raise HTTPException(status_code=400, detail="token required")
    try:
        with sqlite3.connect("data/app.db") as c:
            row = c.execute("SELECT key FROM patient_appointments WHERE key=? AND token=?", (key, body.token)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="not found")
            c.execute(
                "UPDATE patient_appointments SET payload_json=json(?), created_at=? WHERE key=? AND token=?",
                (__import__("json").dumps(body.appointmentData), datetime.utcnow().isoformat(), key, body.token),
            )
            c.commit()
        return {"ok": True, "key": key}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e!s}")
