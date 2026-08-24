"""
Global exception handlers and custom exceptions
Centralized error handling for the application
"""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.core.safe_logging import log_error, log_warning

logger = logging.getLogger(__name__)


class MedicalAPIException(Exception):
    """Base exception for medical API"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class LLMServiceException(MedicalAPIException):
    """LLM service related exceptions"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, 503, details)


class PlaceholderClinicalException(MedicalAPIException):
    """Stub clinical method invoked. Not a real diagnosis/treatment path."""

    def __init__(self, message: str = "placeholder clinical endpoint"):
        super().__init__(
            message,
            501,
            {
                "error_type": "not_implemented",
                "reason": "research prototype placeholder",
            },
        )


class RAGServiceException(MedicalAPIException):
    """RAG service related exceptions"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, 503, details)


class DatabaseException(MedicalAPIException):
    """Database related exceptions"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, 500, details)


class ValidationException(MedicalAPIException):
    """Data validation exceptions"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message, 400, details)


def _public_exception_details(details: dict[str, Any] | None) -> dict[str, Any]:
    if not details:
        return {}
    allowed = {"error_type", "resource", "reason"}
    return {k: v for k, v in details.items() if k in allowed}


def _safe_validation_details(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    safe = []
    for err in errors:
        safe.append(
            {
                "loc": err.get("loc"),
                "type": err.get("type"),
            }
        )
    return safe


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the application"""

    @app.exception_handler(MedicalAPIException)
    async def medical_api_exception_handler(request: Request, exc: MedicalAPIException):
        """Handle custom medical API exceptions"""
        log_error(
            logger,
            "medical_api_exception",
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method,
            error_type=type(exc).__name__,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Medical API Error",
                "message": exc.message,
                "details": _public_exception_details(exc.details),
                "path": request.url.path,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with logging"""
        log_warning(
            logger,
            "http_exception",
            status_code=exc.status_code,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle Pydantic validation errors without logging request bodies."""
        errors = exc.errors()
        log_warning(
            logger,
            "validation_failed",
            path=request.url.path,
            method=request.method,
            error_count=len(errors),
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": _safe_validation_details(errors),
                "path": request.url.path,
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions"""
        log_error(
            logger,
            "value_error",
            path=request.url.path,
            method=request.method,
            error_type="ValueError",
        )

        return JSONResponse(
            status_code=400,
            content={
                "error": "Value Error",
                "message": "Invalid request",
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other unhandled exceptions without third-party payloads."""
        log_error(
            logger,
            "unhandled_exception",
            path=request.url.path,
            method=request.method,
            error_type=type(exc).__name__,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "path": request.url.path,
            },
        )
