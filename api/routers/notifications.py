"""
Notifications API router
Handles patient notifications, reminders, and alerts
"""

import logging
import sqlite3
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

# Router creation
router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationRequest(BaseModel):
    """Request model for creating notifications"""

    patient_token: str
    type: str  # "reminder", "alert", "update"
    title: str
    message: str
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    scheduled_at: Optional[str] = None


class NotificationResponse(BaseModel):
    """Response model for notifications"""

    id: str
    patient_token: str
    type: str
    title: str
    message: str
    priority: str
    status: str
    created_at: str
    scheduled_at: Optional[str] = None


def _get_db_connection():
    """Get database connection"""
    db_path = settings.db_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_notifications_table_exists(conn):
    """Ensure notifications table exists"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            patient_token TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'normal',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            scheduled_at TEXT,
            sent_at TEXT,
            read_at TEXT
        );
    """)
    conn.commit()


@router.post("/", response_model=NotificationResponse)
async def create_notification(request: NotificationRequest):
    """
    Create a new notification for a patient.
    """
    logger.info(f"Creating notification for patient: {request.patient_token}")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_notifications_table_exists(conn)
            cursor = conn.cursor()

            notification_id = str(uuid.uuid4())
            scheduled_at = request.scheduled_at or datetime.now().isoformat()

            cursor.execute(
                """
                INSERT INTO notifications (
                    id, patient_token, type, title, message, priority, scheduled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    notification_id,
                    request.patient_token,
                    request.type,
                    request.title,
                    request.message,
                    request.priority,
                    scheduled_at,
                ),
            )

            conn.commit()

            return NotificationResponse(
                id=notification_id,
                patient_token=request.patient_token,
                type=request.type,
                title=request.title,
                message=request.message,
                priority=request.priority,
                status="pending",
                created_at=datetime.now().isoformat(),
                scheduled_at=scheduled_at,
            )

    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create notification: {e}"
        )


@router.get("/patient/{token}")
async def get_patient_notifications(token: str, status: Optional[str] = None):
    """
    Get notifications for a specific patient.
    """
    logger.info(f"Retrieving notifications for patient: {token}")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_notifications_table_exists(conn)
            cursor = conn.cursor()

            if status:
                cursor.execute(
                    """
                    SELECT * FROM notifications
                    WHERE patient_token = ? AND status = ?
                    ORDER BY created_at DESC
                """,
                    (token, status),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM notifications
                    WHERE patient_token = ?
                    ORDER BY created_at DESC
                """,
                    (token,),
                )

            rows = cursor.fetchall()
            notifications = []

            for row in rows:
                notifications.append(
                    {
                        "id": row["id"],
                        "patient_token": row["patient_token"],
                        "type": row["type"],
                        "title": row["title"],
                        "message": row["message"],
                        "priority": row["priority"],
                        "status": row["status"],
                        "created_at": row["created_at"],
                        "scheduled_at": row["scheduled_at"],
                        "sent_at": row["sent_at"],
                        "read_at": row["read_at"],
                    }
                )

            return {"notifications": notifications}

    except Exception as e:
        logger.error(f"Failed to retrieve notifications: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve notifications: {e}"
        )


@router.put("/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """
    Mark a notification as read.
    """
    logger.info(f"Marking notification as read: {notification_id}")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_notifications_table_exists(conn)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE notifications
                SET status = 'read', read_at = datetime('now')
                WHERE id = ?
            """,
                (notification_id,),
            )

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Notification not found")

            conn.commit()

            return {"message": "Notification marked as read", "id": notification_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to mark notification as read: {e}"
        )


@router.get("/stats")
async def get_notification_statistics():
    """
    Get notification statistics.
    """
    logger.info("Retrieving notification statistics")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_notifications_table_exists(conn)
            cursor = conn.cursor()

            # Total notifications
            cursor.execute("SELECT COUNT(*) as total FROM notifications")
            total_notifications = cursor.fetchone()["total"]

            # Notifications by status
            cursor.execute(
                "SELECT status, COUNT(*) as count FROM notifications GROUP BY status"
            )
            status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

            # Notifications by type
            cursor.execute(
                "SELECT type, COUNT(*) as count FROM notifications GROUP BY type"
            )
            type_counts = {row["type"]: row["count"] for row in cursor.fetchall()}

            # Recent notifications (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent
                FROM notifications
                WHERE created_at >= datetime('now', '-7 days')
            """)
            recent_notifications = cursor.fetchone()["recent"]

            return {
                "total_notifications": total_notifications,
                "status_counts": status_counts,
                "type_counts": type_counts,
                "recent_notifications": recent_notifications,
            }

    except Exception as e:
        logger.error(f"Failed to retrieve notification statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve statistics: {e}"
        )
