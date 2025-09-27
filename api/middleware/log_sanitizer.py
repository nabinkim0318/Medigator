# api/middleware/log_sanitizer.py
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class NoBodyLoggingFilter(logging.Filter):
    def filter(self, record):
        """Filter out potentially sensitive data from logs"""
        # Remove request body and response body from access logs
        if hasattr(record, "args") and isinstance(record.args, tuple):
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, (dict, list, str)):
                    # Strip large data structures that might contain PHI
                    if len(str(arg)) > 100:
                        sanitized_args.append("[REDACTED]")
                    else:
                        sanitized_args.append(arg)
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)

        # Also sanitize the message itself
        if hasattr(record, "msg") and isinstance(record.msg, str):
            # Remove common PHI patterns
            import re

            record.msg = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]", record.msg)  # SSN
            record.msg = re.sub(r"\b\d{10,}\b", "[ID]", record.msg)  # Long numbers
            record.msg = re.sub(
                r"\b[A-Za-z]+@[A-Za-z]+\.[A-Za-z]+\b",
                "[EMAIL]",
                record.msg,
            )  # Email

        return True


class RedactLogsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request without sensitive data
        logger = logging.getLogger("api.middleware")
        if settings.HIPAA_MODE:
            # Don't log request body in HIPAA mode
            logger.info(f"{request.method} {request.url.path} [PHI REDACTED]")
        else:
            logger.info(f"{request.method} {request.url.path}")

        response = await call_next(request)

        if settings.HIPAA_MODE:
            # add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
