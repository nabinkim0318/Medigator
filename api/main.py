"""
FastAPI main application
Medical report generation and analysis API server
"""

import logging
import os
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.core.config import settings
from api.core.safe_logging import SensitiveLogFilter, log_info, log_warning
from api.middleware.access_boundary import AccessBoundaryMiddleware
from api.middleware.log_sanitizer import NoBodyLoggingFilter, RedactLogsMiddleware
from api.middleware.performance import PerformanceMiddleware
from api.routers import codes, evidence, llm, rag, report, summary
from api.routers import auth, patient, notifications, files, analytics

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.exceptions import setup_exception_handlers

from api.core.logging_config import setup_logging
from api.core.startup import perform_startup_checks

logger = setup_logging()
logging.getLogger().addFilter(SensitiveLogFilter())

startup_results = perform_startup_checks()


app = FastAPI(
    title="BBB Medical Report API",
    description=(
        "Portfolio prototype for synthetic/demo medical-intake workflows. "
        "Not a production security control. Synthetic data only."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

log_info(logger, "api_starting", enabled=settings.DEMO_MODE)
log_info(logger, "demo_mode", enabled=settings.DEMO_MODE)
log_info(logger, "synthetic_data_only", enabled=settings.SYNTHETIC_DATA_ONLY)
log_info(logger, "rag_enabled", enabled=settings.enable_rag)

app.include_router(report.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["llm"])
app.include_router(summary.router, prefix="/api/v1", tags=["summary"])
app.include_router(evidence.router, prefix="/api/v1", tags=["evidence"])
app.include_router(codes.router, prefix="/api/v1", tags=["codes"])
app.include_router(rag.router, prefix="/api/v1", tags=["rag"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(patient.router, prefix="/api/v1", tags=["patient"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
log_info(logger, "routers_registered")

access_logger = logging.getLogger("uvicorn.access")
access_logger.addFilter(NoBodyLoggingFilter())
access_logger.addFilter(SensitiveLogFilter())


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request size to prevent DoS attacks"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            log_warning(
                logger,
                "request_too_large",
                status_code=413,
                method=request.method,
                path=request.url.path,
            )
            raise HTTPException(status_code=413, detail="Request too large (max 1MB)")
    return await call_next(request)


# Last added runs first. CORS must wrap 401/403 from the access boundary.
app.add_middleware(RedactLogsMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(AccessBoundaryMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With",
    ],
)

setup_exception_handlers(app)

try:
    app.mount("/", StaticFiles(directory="app/dist", html=True), name="frontend")
except Exception:
    log_warning(logger, "static_mount_skipped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BBB Medical Report API",
        "version": "1.0.0",
        "docs": "/docs",
        "synthetic_data_only": True,
        "note": "Portfolio prototype. Not production security. Synthetic/demo data only.",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "synthetic_data_only": settings.SYNTHETIC_DATA_ONLY,
        "demo_mode": settings.DEMO_MODE,
    }


if __name__ == "__main__":
    import uvicorn

    log_info(logger, "uvicorn_bind")
    uvicorn.run(app, host="0.0.0.0", port=8082)  # nosec B104 - Development server binding
