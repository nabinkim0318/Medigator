"""
Analytics API router
Provides analytics, reporting, and dashboard data
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

# Router creation
router = APIRouter(prefix="/analytics", tags=["analytics"])


class DashboardStats(BaseModel):
    """Dashboard statistics model"""

    total_patients: int
    active_patients: int
    completed_appointments: int
    pending_appointments: int
    total_files: int
    total_notifications: int


class TrendData(BaseModel):
    """Trend data model"""

    date: str
    patients: int
    appointments: int
    files: int


def _get_db_connection():
    """Get database connection"""
    db_path = settings.db_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    """
    Get dashboard statistics.
    """
    logger.info("Retrieving dashboard statistics")
    try:
        conn = _get_db_connection()
        with conn:
            cursor = conn.cursor()

            # Total patients
            cursor.execute("SELECT COUNT(*) as total FROM intake_session")
            total_patients = cursor.fetchone()["total"]

            # Active patients (last 30 days)
            cursor.execute("""
                SELECT COUNT(*) as active
                FROM intake_session
                WHERE created_at >= datetime('now', '-30 days')
            """)
            active_patients = cursor.fetchone()["active"]

            # Completed appointments
            cursor.execute("""
                SELECT COUNT(*) as completed
                FROM intake_session
                WHERE status = 'SUBMITTED'
            """)
            completed_appointments = cursor.fetchone()["completed"]

            # Pending appointments
            cursor.execute("""
                SELECT COUNT(*) as pending
                FROM intake_session
                WHERE status = 'PENDING'
            """)
            pending_appointments = cursor.fetchone()["pending"]

            # Total files (if files table exists)
            try:
                cursor.execute("SELECT COUNT(*) as total FROM files")
                total_files = cursor.fetchone()["total"]
            except sqlite3.OperationalError:
                total_files = 0

            # Total notifications (if notifications table exists)
            try:
                cursor.execute("SELECT COUNT(*) as total FROM notifications")
                total_notifications = cursor.fetchone()["total"]
            except sqlite3.OperationalError:
                total_notifications = 0

            return DashboardStats(
                total_patients=total_patients,
                active_patients=active_patients,
                completed_appointments=completed_appointments,
                pending_appointments=pending_appointments,
                total_files=total_files,
                total_notifications=total_notifications,
            )

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dashboard stats: {e}"
        )


@router.get("/trends")
async def get_trend_data(days: int = 30):
    """
    Get trend data for the specified number of days.
    """
    logger.info(f"Retrieving trend data for {days} days")
    try:
        conn = _get_db_connection()
        with conn:
            cursor = conn.cursor()

            # Patients by day
            cursor.execute(
                """
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM intake_session
                WHERE created_at >= datetime('now', '-{} days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """.format(days)
            )

            patient_trends = {row["date"]: row["count"] for row in cursor.fetchall()}

            # Files by day (if files table exists)
            file_trends = {}
            try:
                cursor.execute(
                    """
                    SELECT DATE(uploaded_at) as date, COUNT(*) as count
                    FROM files
                    WHERE uploaded_at >= datetime('now', '-{} days')
                    GROUP BY DATE(uploaded_at)
                    ORDER BY date
                """.format(days)
                )
                file_trends = {row["date"]: row["count"] for row in cursor.fetchall()}
            except sqlite3.OperationalError:
                pass

            # Generate date range
            start_date = datetime.now() - timedelta(days=days)
            date_range = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                date_range.append(date_str)

            # Combine trends
            trends = []
            for date in date_range:
                trends.append(
                    {
                        "date": date,
                        "patients": patient_trends.get(date, 0),
                        "files": file_trends.get(date, 0),
                    }
                )

            return {"trends": trends}

    except Exception as e:
        logger.error(f"Failed to retrieve trend data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve trend data: {e}"
        )


@router.get("/symptoms/analysis")
async def get_symptom_analysis():
    """
    Analyze common symptoms from patient data.
    """
    logger.info("Analyzing symptoms from patient data")
    try:
        conn = _get_db_connection()
        with conn:
            cursor = conn.cursor()

            # Get all appointment data
            cursor.execute("""
                SELECT answers_json FROM intake_payload
            """)

            rows = cursor.fetchall()
            symptom_counts = {}

            for row in rows:
                try:
                    answers = json.loads(row["answers_json"])
                    # Analyze Q&A data for symptoms
                    for key, value in answers.items():
                        if isinstance(value, str) and value.strip():
                            # Simple keyword analysis
                            if "pain" in value.lower():
                                symptom_counts["pain"] = (
                                    symptom_counts.get("pain", 0) + 1
                                )
                            if "chest" in value.lower():
                                symptom_counts["chest"] = (
                                    symptom_counts.get("chest", 0) + 1
                                )
                            if "breathing" in value.lower():
                                symptom_counts["breathing"] = (
                                    symptom_counts.get("breathing", 0) + 1
                                )
                            if "heart" in value.lower():
                                symptom_counts["heart"] = (
                                    symptom_counts.get("heart", 0) + 1
                                )
                except json.JSONDecodeError:
                    continue

            # Sort by frequency
            sorted_symptoms = sorted(
                symptom_counts.items(), key=lambda x: x[1], reverse=True
            )

            return {"symptom_analysis": sorted_symptoms, "total_responses": len(rows)}

    except Exception as e:
        logger.error(f"Failed to analyze symptoms: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze symptoms: {e}")


@router.get("/export/patients")
async def export_patients(format: str = "json"):
    """
    Export patient data in specified format.
    """
    logger.info(f"Exporting patient data in {format} format")
    try:
        conn = _get_db_connection()
        with conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT s.token, s.status, s.created_at, p.patient_data, p.answers_json
                FROM intake_session s
                LEFT JOIN intake_payload p ON s.id = p.session_id
                ORDER BY s.created_at DESC
            """)

            rows = cursor.fetchall()
            patients = []

            for row in rows:
                try:
                    patient_data = (
                        json.loads(row["patient_data"]) if row["patient_data"] else {}
                    )
                    appointment_data = (
                        json.loads(row["answers_json"]) if row["answers_json"] else {}
                    )

                    patients.append(
                        {
                            "token": row["token"],
                            "status": row["status"],
                            "created_at": row["created_at"],
                            "profile": patient_data,
                            "appointment": appointment_data,
                        }
                    )
                except json.JSONDecodeError:
                    continue

            if format.lower() == "csv":
                # Convert to CSV format
                import csv
                import io

                output = io.StringIO()
                if patients:
                    writer = csv.DictWriter(output, fieldnames=patients[0].keys())
                    writer.writeheader()
                    writer.writerows(patients)

                return {"data": output.getvalue(), "format": "csv"}
            else:
                return {"data": patients, "format": "json"}

    except Exception as e:
        logger.error(f"Failed to export patients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export patients: {e}")
