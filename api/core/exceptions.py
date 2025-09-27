"""
Global exception handlers and custom exceptions
Centralized error handling for the application
"""

import logging
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import traceback

logger = logging.getLogger(__name__)


class MedicalAPIException(Exception):
    """Base exception for medical API"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class LLMServiceException(MedicalAPIException):
    """LLM service related exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class RAGServiceException(MedicalAPIException):
    """RAG service related exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class DatabaseException(MedicalAPIException):
    """Database related exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 500, details)


class ValidationException(MedicalAPIException):
    """Data validation exceptions"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 400, details)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for the application"""
    
    @app.exception_handler(MedicalAPIException)
    async def medical_api_exception_handler(request: Request, exc: MedicalAPIException):
        """Handle custom medical API exceptions"""
        logger.error(f"Medical API Exception: {exc.message}", extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        })
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Medical API Error",
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with logging"""
        logger.warning(f"HTTP Exception: {exc.detail}", extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        })
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation Error: {exc.errors()}", extra={
            "path": request.url.path,
            "method": request.method,
            "body": str(exc.body) if hasattr(exc, 'body') else None
        })
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions"""
        logger.error(f"Value Error: {str(exc)}", extra={
            "path": request.url.path,
            "method": request.method
        })
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Value Error",
                "message": str(exc),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other unhandled exceptions"""
        logger.error(f"Unhandled Exception: {str(exc)}", extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        })
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "path": request.url.path
            }
        )
