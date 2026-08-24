# api/middleware/log_sanitizer.py
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.core.safe_logging import log_info, sanitize_path


class NoBodyLoggingFilter(logging.Filter):
    def filter(self, record):
        """Filter out potentially sensitive data from logs"""
        if hasattr(record, "args") and isinstance(record.args, tuple):
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, (dict, list)):
                    sanitized_args.append("[REDACTED]")
                elif isinstance(arg, str) and len(arg) > 80:
                    sanitized_args.append("[REDACTED]")
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        return True


class RedactLogsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger("api.middleware")
        log_info(
            logger,
            "http_request",
            method=request.method,
            path=sanitize_path(request.url.path),
        )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response
