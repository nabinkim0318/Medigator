"""
Performance monitoring middleware
Track request duration and log performance metrics
"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.core.logging_config import log_performance_metric

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track and log request performance"""

    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log performance metrics
        operation = f"{request.method} {request.url.path}"
        log_performance_metric(operation, duration)

        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        # Log slow requests
        if duration > 2.0:  # Requests taking more than 2 seconds
            logger.warning(f"Slow request detected: {operation} took {duration:.3f}s")

        return response
