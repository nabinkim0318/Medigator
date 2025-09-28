"""
Files API router
Handles file uploads, downloads, and management for patient documents
"""

import logging
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

# Router creation
router = APIRouter(prefix="/files", tags=["files"])

# File upload directory
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".txt"}


class FileInfo(BaseModel):
    """Response model for file operations"""

    id: str
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    patient_token: str
    uploaded_at: str
    file_path: str


def _get_db_connection():
    """Get database connection"""
    db_path = settings.db_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_files_table_exists(conn):
    """Ensure files table exists"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            patient_token TEXT NOT NULL,
            uploaded_at TEXT NOT NULL DEFAULT (datetime('now')),
            file_path TEXT NOT NULL,
            description TEXT
        );
    """)
    conn.commit()


def _get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()


def _is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    return _get_file_extension(filename) in ALLOWED_EXTENSIONS


@router.post("/upload/{patient_token}", response_model=FileInfo)
async def upload_file(
    patient_token: str, file: UploadFile = File(...), description: Optional[str] = None
):
    """
    Upload a file for a patient.
    """
    logger.info(f"Uploading file for patient: {patient_token}")

    if not _is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = _get_file_extension(file.filename)
        unique_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Save file metadata to database
        conn = _get_db_connection()
        with conn:
            _ensure_files_table_exists(conn)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO files (
                    id, filename, original_filename, file_size, content_type,
                    patient_token, file_path, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    file_id,
                    unique_filename,
                    file.filename,
                    len(content),
                    file.content_type,
                    patient_token,
                    file_path,
                    description,
                ),
            )

            conn.commit()

        return FileInfo(
            id=file_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_size=len(content),
            content_type=file.content_type,
            patient_token=patient_token,
            uploaded_at=datetime.now().isoformat(),
            file_path=file_path,
        )

    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")


@router.get("/patient/{patient_token}")
async def get_patient_files(patient_token: str):
    """
    Get all files for a specific patient.
    """
    logger.info(f"Retrieving files for patient: {patient_token}")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_files_table_exists(conn)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM files
                WHERE patient_token = ?
                ORDER BY uploaded_at DESC
            """,
                (patient_token,),
            )

            rows = cursor.fetchall()
            files = []

            for row in rows:
                files.append(
                    {
                        "id": row["id"],
                        "filename": row["filename"],
                        "original_filename": row["original_filename"],
                        "file_size": row["file_size"],
                        "content_type": row["content_type"],
                        "patient_token": row["patient_token"],
                        "uploaded_at": row["uploaded_at"],
                        "description": row["description"],
                    }
                )

            return {"files": files}

    except Exception as e:
        logger.error(f"Failed to retrieve files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {e}")


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Download a file by ID.
    """
    logger.info(f"Downloading file: {file_id}")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_files_table_exists(conn)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM files WHERE id = ?
            """,
                (file_id,),
            )

            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="File not found")

            file_path = row["file_path"]
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found on disk")

            return FileResponse(
                path=file_path,
                filename=row["original_filename"],
                media_type=row["content_type"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}")


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file by ID.
    """
    logger.info(f"Deleting file: {file_id}")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_files_table_exists(conn)
            cursor = conn.cursor()

            # Get file info
            cursor.execute(
                """
                SELECT * FROM files WHERE id = ?
            """,
                (file_id,),
            )

            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="File not found")

            # Delete file from disk
            file_path = row["file_path"]
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete from database
            cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()

            return {"message": "File deleted successfully", "id": file_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {e}")


@router.get("/stats")
async def get_file_statistics():
    """
    Get file statistics.
    """
    logger.info("Retrieving file statistics")
    try:
        conn = _get_db_connection()
        with conn:
            _ensure_files_table_exists(conn)
            cursor = conn.cursor()

            # Total files
            cursor.execute("SELECT COUNT(*) as total FROM files")
            total_files = cursor.fetchone()["total"]

            # Total file size
            cursor.execute("SELECT SUM(file_size) as total_size FROM files")
            total_size = cursor.fetchone()["total_size"] or 0

            # Files by content type
            cursor.execute(
                "SELECT content_type, COUNT(*) as count FROM files GROUP BY content_type"
            )
            type_counts = {
                row["content_type"]: row["count"] for row in cursor.fetchall()
            }

            # Recent files (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) as recent
                FROM files
                WHERE uploaded_at >= datetime('now', '-7 days')
            """)
            recent_files = cursor.fetchone()["recent"]

            return {
                "total_files": total_files,
                "total_size": total_size,
                "type_counts": type_counts,
                "recent_files": recent_files,
            }

    except Exception as e:
        logger.error(f"Failed to retrieve file statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve statistics: {e}"
        )
