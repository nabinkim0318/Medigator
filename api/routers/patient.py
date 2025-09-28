import sqlite3
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/patient", tags=["patient"])


class PatientDataIn(BaseModel):
    token: str
    medicalHistory: dict


class ProfileIn(BaseModel):
    token: str
    profile: dict


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


@router.get("/profile")
def get_profiles(token: Optional[str] = None):
    """Return profiles stored in the patients table.

    If `token` is provided, returns a single profile under profiles: [ ... ].
    Otherwise returns all profiles.
    """
    try:
        with sqlite3.connect("data/app.db") as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS patients (token TEXT PRIMARY KEY, profile_json TEXT, medical_history_json TEXT, created_at TEXT, updated_at TEXT)"
            )
            if token:
                row = c.execute(
                    "SELECT token, profile_json, medical_history_json FROM patients WHERE token=?",
                    (token,),
                ).fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="not found")
                token_v, profile_json, med_json = row
                return {
                    "ok": True,
                    "profiles": [
                        {
                            "token": token_v,
                            "profile": __import__("json").loads(profile_json) if profile_json else None,
                            "medicalHistory": __import__("json").loads(med_json) if med_json else None,
                        }
                    ],
                }

            rows = c.execute(
                "SELECT token, profile_json, medical_history_json FROM patients"
            ).fetchall()
            profiles = []
            for r in rows:
                token_v, profile_json, med_json = r
                profiles.append(
                    {
                        "token": token_v,
                        "profile": __import__("json").loads(profile_json) if profile_json else None,
                        "medicalHistory": __import__("json").loads(med_json) if med_json else None,
                    }
                )

        return {"ok": True, "profiles": profiles}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e!s}")


@router.post("/profile")
def submit_profile(body: ProfileIn = Body(...)):
    """Accept a user's profile and persist it tied to the user token.

    Request shape:
      { token: str, profile: { name, age, gender, bloodGroup, phone, email } }

    Stores/updates into table `patients` with columns (token, profile_json, medical_history_json, created_at, updated_at)
    """
    if not body.token:
        raise HTTPException(status_code=400, detail="token required")

    try:
        with sqlite3.connect("data/app.db") as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS patients (token TEXT PRIMARY KEY, profile_json TEXT, medical_history_json TEXT, created_at TEXT, updated_at TEXT)"
            )
            # check existing
            row = c.execute("SELECT token FROM patients WHERE token=?", (body.token,)).fetchone()
            now = datetime.utcnow().isoformat()
            profile_json = __import__("json").dumps(body.profile)
            if row:
                c.execute(
                    "UPDATE patients SET profile_json=json(?), updated_at=? WHERE token=?",
                    (profile_json, now, body.token),
                )
            else:
                c.execute(
                    "INSERT INTO patients(token, profile_json, medical_history_json, created_at, updated_at) VALUES(?, json(?), NULL, ?, ?)",
                    (body.token, profile_json, now, now),
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
