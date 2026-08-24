# api/routers/patient.py
"""
Patient API router
Handles patient intake data storage and retrieval
"""

import asyncio
import inspect
import json
import logging
import sqlite3
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from api.core.config import settings
from api.core.safe_logging import log_error, log_info, log_warning
from api.core.synthetic import enforce_synthetic_payload, enforce_synthetic_profile
from api.services.llm import llm_service

# Get logger
logger = logging.getLogger(__name__)

# Router creation
router = APIRouter(prefix="/patient", tags=["patient"])


def _get_db_connection():
    """Get database connection"""
    db_path = settings.db_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = (
        sqlite3.Row
    )  # This enables column access by name: row['column_name']
    return conn


def _ensure_table_exists(conn):
    """Ensure intake_payload table exists"""
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS intake_session (
            id TEXT PRIMARY KEY,                -- uuid
            token TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDING','SUBMITTED','EXPIRED')),
            patient_hint TEXT,                  -- patient hint (optional)
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,           -- ISO
            submitted_at TEXT
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS intake_payload (
            session_id TEXT PRIMARY KEY REFERENCES intake_session(id) ON DELETE CASCADE,
            patient_data TEXT,                  -- patient profile data (JSON)
            answers_json TEXT NOT NULL,         -- form response (non-PHI only)
            ai_summary_status TEXT DEFAULT 'pending' -- New column for AI summary status
        );
        """
    )
    conn.commit()


def _generate_llm_summary_background(
    session_id: str, token: str, appointment_data: dict
):
    """Generate LLM summary in background"""
    try:
        log_info(logger, "llm_summary_started")

        # Prepare data for LLM
        summary_data = {
            "encounterId": "demo-session",
            "patient": {},
            "answers": {
                "chief_complaint": appointment_data.get("q1", ""),
                "location": appointment_data.get("q2", ""),
                "character": appointment_data.get("q3", ""),
                "aggravating_factors": appointment_data.get("q4", ""),
                "alleviating_factors": appointment_data.get("q5", ""),
                "associated_symptoms": appointment_data.get("q6", ""),
                "severity": appointment_data.get("q7", ""),
                "duration": appointment_data.get("q8", ""),
                "notes": appointment_data.get("q9", ""),
            },
        }

        result = llm_service.summary(summary_data)
        if inspect.isawaitable(result):
            asyncio.run(result)
        log_info(logger, "llm_summary_result_received")

        # Update AI summary status to 'done'
        conn = _get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE intake_payload SET ai_summary_status = ? WHERE session_id = ?",
                ("done", session_id),
            )
            conn.commit()

        log_info(logger, "llm_summary_completed")

    except Exception:
        log_error(logger, "llm_summary_failed")
        # Update status to 'failed' if needed
        try:
            conn = _get_db_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE intake_payload SET ai_summary_status = ? WHERE session_id = ?",
                    ("failed", session_id),
                )
                conn.commit()
        except Exception:
            log_error(logger, "llm_summary_status_update_failed")


def _trigger_llm_summary_async(session_id: str, token: str, appointment_data: dict):
    """Trigger LLM summary generation asynchronously"""
    # Use ThreadPoolExecutor to run in background
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(
        _generate_llm_summary_background, session_id, token, appointment_data
    )
    # Don't wait for completion, let it run in background
    return future


class AppointmentData(BaseModel):
    """Patient appointment data model"""

    q1: str = ""
    q2: str = ""
    q3: str = ""
    q4: str = ""
    q5: str = ""
    q6: str = ""
    q7: str = ""
    q8: str = ""
    q9: str = ""


class PatientData(BaseModel):
    """Patient profile data model"""

    name: str = ""
    age: int = 0
    gender: str = ""
    bloodGroup: str = ""
    phone: str = ""
    email: str = ""


class AppointmentRequest(BaseModel):
    """Appointment request model. session_id is a correlation id, not authentication."""

    session_id: str = ""
    token: str = ""  # legacy alias for session_id; not an access token
    patientData: PatientData = PatientData()
    appointmentData: AppointmentData

    def correlation_id(self) -> str:
        return (self.session_id or self.token).strip()


class AppointmentResponse(BaseModel):
    """Appointment response model"""

    key: str
    message: str


def get_db_connection():
    """Get SQLite database connection"""
    db_path = settings.db_url.replace("sqlite:///", "")
    return sqlite3.connect(db_path)


def create_appointment_table():
    """Create appointment table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id VARCHAR(50) UNIQUE NOT NULL,
            token VARCHAR(100) NOT NULL,
            q1 TEXT,
            q2 TEXT,
            q3 TEXT,
            q4 TEXT,
            q5 TEXT,
            q6 TEXT,
            q7 TEXT,
            q8 TEXT,
            q9 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@router.post("/appointment", response_model=AppointmentResponse)
async def save_appointment(request: AppointmentRequest):
    """
    Save patient appointment data to SQLite database

    Args:
        request: Appointment data with token

    Returns:
        Saved appointment information
    """
    logger.info("Saving appointment data")

    try:
        correlation_id = request.correlation_id() or str(uuid.uuid4())
        enforce_synthetic_profile(request.patientData.model_dump())
        enforce_synthetic_payload(request.appointmentData.model_dump())

        # Generate unique appointment ID
        appointment_id = str(uuid.uuid4())

        # Connect to database
        conn = _get_db_connection()
        _ensure_table_exists(conn)
        cursor = conn.cursor()

        # Create intake session first
        session_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO intake_session (id, token, status, created_at, expires_at)
            VALUES (?, ?, 'SUBMITTED', datetime('now'), datetime('now', '+1 day'))
            """,
            (session_id, correlation_id),
        )

        # Prepare patient data
        patient_data = {
            "name": request.patientData.name,
            "age": request.patientData.age,
            "gender": request.patientData.gender,
            "bloodGroup": request.patientData.bloodGroup,
            "phone": request.patientData.phone,
            "email": request.patientData.email,
        }

        # Insert appointment data into intake_payload
        appointment_data = {
            "q1": request.appointmentData.q1,
            "q2": request.appointmentData.q2,
            "q3": request.appointmentData.q3,
            "q4": request.appointmentData.q4,
            "q5": request.appointmentData.q5,
            "q6": request.appointmentData.q6,
            "q7": request.appointmentData.q7,
            "q8": request.appointmentData.q8,
            "q9": request.appointmentData.q9,
        }

        cursor.execute(
            """
            INSERT INTO intake_payload (session_id, patient_data, answers_json, ai_summary_status)
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                json.dumps(patient_data),
                json.dumps(appointment_data),
                "pending",
            ),
        )

        conn.commit()
        conn.close()

        # Trigger LLM summary generation in background
        _trigger_llm_summary_async(session_id, correlation_id, appointment_data)

        log_info(logger, "appointment_saved")

        return AppointmentResponse(
            key=appointment_id, message="Appointment data saved successfully"
        )

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "appointment_save_failed")
        raise HTTPException(status_code=500, detail="Failed to save appointment")


@router.get("/appointment/{token}")
async def get_appointment(token: str):
    """
    Retrieve patient appointment data by token

    Args:
        token: Patient token

    Returns:
        Appointment data
    """
    log_info(logger, "appointment_get")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT appointment_id, q1, q2, q3, q4, q5, q6, q7, q8, q9, created_at
            FROM appointments
            WHERE token = ?
            ORDER BY created_at DESC
            LIMIT 1
        """,
            (token,),
        )

        result = cursor.fetchone()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Convert to dictionary
        appointment_data = {
            "appointment_id": result[0],
            "q1": result[1],
            "q2": result[2],
            "q3": result[3],
            "q4": result[4],
            "q5": result[5],
            "q6": result[6],
            "q7": result[7],
            "q8": result[8],
            "q9": result[9],
            "created_at": result[10],
        }

        return appointment_data

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "appointment_get_failed")
        raise HTTPException(status_code=500, detail="Failed to retrieve appointment")


@router.get("/appointment/{token}/summary")
async def get_appointment_summary(token: str):
    """
    Get appointment data formatted for LLM summary

    Args:
        token: Patient token

    Returns:
        Formatted data for LLM summary
    """
    log_info(logger, "appointment_summary_get")

    try:
        # Get appointment data
        appointment_data = await get_appointment(token)

        # Format for LLM summary
        summary_data = {
            "encounterId": appointment_data["appointment_id"],
            "patient": {
                "age": 0,  # Default age, should be collected in form
                "sex": "Unknown",  # Default sex, should be collected in form
            },
            "answers": {
                "cc": appointment_data.get("q1", ""),
                "onset": appointment_data.get("q2", ""),
                "radiation": appointment_data.get("q3", ""),
                "pmh": appointment_data.get("q4", ""),
                "meds": appointment_data.get("q5", ""),
                "exertion": appointment_data.get("q6", ""),
                "relievedByRest": appointment_data.get("q7", ""),
                "additional": appointment_data.get("q8", ""),
                "notes": appointment_data.get("q9", ""),
            },
        }

        return summary_data

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "appointment_summary_failed")
        raise HTTPException(status_code=500, detail="Failed to get appointment summary")


@router.get("/profile")
async def get_patient_profiles():
    """
    Retrieve all patient profiles with their intake data.
    """
    log_info(logger, "patient_profiles_list")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.token, p.patient_data, p.answers_json, p.ai_summary_status
                FROM intake_payload p
                JOIN intake_session s ON s.id = p.session_id
                """
            )
            rows = cursor.fetchall()

            profiles = []
            for row in rows:
                try:
                    patient_data = (
                        json.loads(row["patient_data"]) if row["patient_data"] else {}
                    )
                    answers_data = (
                        json.loads(row["answers_json"]) if row["answers_json"] else {}
                    )

                    profiles.append(
                        {
                            "id": row["token"],
                            "token": row["token"],
                            "profile": patient_data,
                            "appointment": answers_data,
                            "ai_summary_status": row["ai_summary_status"] or "pending",
                        }
                    )
                except json.JSONDecodeError:
                    log_warning(logger, "patient_profile_json_parse_failed")
                    continue

            return {"profiles": profiles}
    except Exception:
        log_error(logger, "patient_profiles_list_failed")
        raise HTTPException(status_code=500, detail="Failed to retrieve profiles")


@router.delete("/profile/{token}")
async def delete_patient_profile(token: str):
    """
    Delete patient profile and associated data by token.
    """
    log_info(logger, "patient_profile_delete")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            # First, get the session_id for this token
            cursor.execute("SELECT id FROM intake_session WHERE token = ?", (token,))
            session_row = cursor.fetchone()

            if not session_row:
                raise HTTPException(status_code=404, detail="Patient profile not found")

            session_id = session_row["id"]

            # Delete from intake_payload (this will cascade due to foreign key)
            cursor.execute(
                "DELETE FROM intake_payload WHERE session_id = ?", (session_id,)
            )

            # Delete from intake_session
            cursor.execute("DELETE FROM intake_session WHERE id = ?", (session_id,))

            conn.commit()

            return {"message": "Patient profile deleted successfully", "token": token}

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "patient_profile_delete_failed")
        raise HTTPException(status_code=500, detail="Failed to delete profile")


@router.put("/profile/{token}")
async def update_patient_profile(token: str, profile_data: dict):
    """
    Update patient profile information.
    """
    log_info(logger, "patient_profile_update")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            # Check if patient exists
            cursor.execute("SELECT id FROM intake_session WHERE token = ?", (token,))
            session_row = cursor.fetchone()

            if not session_row:
                raise HTTPException(status_code=404, detail="Patient profile not found")

            # Update patient data in intake_payload
            cursor.execute(
                "UPDATE intake_payload SET patient_data = ? WHERE session_id = ?",
                (json.dumps(profile_data), session_row["id"]),
            )

            conn.commit()

            return {"message": "Patient profile updated successfully", "token": token}

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "patient_profile_update_failed")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.get("/profile/{token}")
async def get_patient_profile(token: str):
    """
    Get specific patient profile by token.
    """
    log_info(logger, "patient_profile_get")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT s.token, p.patient_data, p.answers_json
                FROM intake_session s
                JOIN intake_payload p ON s.id = p.session_id
                WHERE s.token = ?
                """,
                (token,),
            )
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Patient profile not found")

            patient_data = (
                json.loads(row["patient_data"]) if row["patient_data"] else {}
            )
            appointment_data = (
                json.loads(row["answers_json"]) if row["answers_json"] else {}
            )

            return {
                "token": row["token"],
                "profile": patient_data,
                "appointment": appointment_data,
            }

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "patient_profile_get_failed")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.get("/stats")
async def get_patient_statistics():
    """
    Get patient statistics and analytics.
    """
    log_info(logger, "patient_stats")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            # Total patients
            cursor.execute("SELECT COUNT(*) as total FROM intake_session")
            total_patients = cursor.fetchone()["total"]

            # Patients by status
            cursor.execute(
                "SELECT status, COUNT(*) as count FROM intake_session GROUP BY status"
            )
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

            # Recent patients (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent
                FROM intake_session
                WHERE created_at >= datetime('now', '-7 days')
            """)
            recent_patients = cursor.fetchone()["recent"]

            # Patients by day (last 7 days)
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM intake_session
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            daily_counts = [
                {"date": row["date"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

            return {
                "total_patients": total_patients,
                "status_counts": status_counts,
                "recent_patients": recent_patients,
                "daily_counts": daily_counts,
            }

    except Exception:
        log_error(logger, "patient_stats_failed")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@router.get("/search")
async def search_patients(query: str = "", limit: int = 10, offset: int = 0):
    """
    Search patients by name, email, or other criteria.
    """
    log_info(logger, "patient_search")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            if query:
                # Search in patient_data JSON
                cursor.execute(
                    """
                    SELECT s.token, p.patient_data, p.answers_json
                    FROM intake_session s
                    JOIN intake_payload p ON s.id = p.session_id
                    WHERE p.patient_data LIKE ? OR p.answers_json LIKE ?
                    LIMIT ? OFFSET ?
                """,
                    (f"%{query}%", f"%{query}%", limit, offset),
                )
            else:
                # Return all patients with pagination
                cursor.execute(
                    """
                    SELECT s.token, p.patient_data, p.answers_json
                    FROM intake_session s
                    JOIN intake_payload p ON s.id = p.session_id
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

            rows = cursor.fetchall()
            results = []

            for row in rows:
                try:
                    patient_data = (
                        json.loads(row["patient_data"]) if row["patient_data"] else {}
                    )
                    appointment_data = (
                        json.loads(row["answers_json"]) if row["answers_json"] else {}
                    )

                    results.append(
                        {
                            "token": row["token"],
                            "profile": patient_data,
                            "appointment": appointment_data,
                        }
                    )
                except json.JSONDecodeError:
                    continue

            return {"results": results, "count": len(results)}

    except Exception:
        log_error(logger, "patient_search_failed")
        raise HTTPException(status_code=500, detail="Failed to search patients")


@router.put("/profile/{token}/ai-summary-status")
async def update_ai_summary_status(token: str, status: str = Body(...)):
    """
    Update AI summary status for a patient.
    """
    log_info(logger, "ai_summary_status_update")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            # Check if patient exists
            cursor.execute("SELECT id FROM intake_session WHERE token = ?", (token,))
            session_row = cursor.fetchone()

            if not session_row:
                raise HTTPException(status_code=404, detail="Patient profile not found")

            session_id = session_row["id"]

            # Update AI summary status
            cursor.execute(
                "UPDATE intake_payload SET ai_summary_status = ? WHERE session_id = ?",
                (status, session_id),
            )

            conn.commit()

            return {
                "message": "AI summary status updated successfully",
                "token": token,
                "status": status,
            }

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "ai_summary_status_update_failed")
        raise HTTPException(
            status_code=500, detail="Failed to update AI summary status"
        )


@router.post("/profile", response_model=AppointmentResponse)
async def save_patient_profile(profile_data: dict):
    """
    Save patient profile data. session_id is a correlation id, not authentication.
    """
    log_info(logger, "patient_profile_save")

    try:
        nested = profile_data.get("profile")
        profile = nested if isinstance(nested, dict) else profile_data
        identity = {
            k: profile.get(k)
            for k in ("name", "age", "gender", "bloodGroup", "phone", "email")
            if k in profile
        }
        enforce_synthetic_profile(identity)
        enforce_synthetic_payload(
            {k: v for k, v in profile.items() if k not in identity}
        )

        correlation_id = str(
            profile_data.get("session_id") or profile_data.get("token") or uuid.uuid4()
        )

        conn = _get_db_connection()
        with conn:
            _ensure_table_exists(conn)
            cursor = conn.cursor()

            session_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO intake_session (id, token, status, created_at, expires_at)
                VALUES (?, ?, 'SUBMITTED', datetime('now'), datetime('now', '+1 day'))
                """,
                (session_id, correlation_id),
            )

            cursor.execute(
                """
                INSERT INTO intake_payload (session_id, patient_data, answers_json, ai_summary_status)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_id,
                    json.dumps(identity or profile),
                    json.dumps({}),
                    "pending",
                ),
            )

            conn.commit()

            return AppointmentResponse(
                key=session_id, message="Patient profile saved successfully"
            )

    except HTTPException:
        raise
    except Exception:
        log_error(logger, "patient_profile_save_failed")
        raise HTTPException(status_code=500, detail="Failed to save profile")
