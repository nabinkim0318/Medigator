"""
FastAPI main application
Medical report generation and analysis API server
"""

import logging
import logging.config
import os
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from middleware.log_sanitizer import NoBodyLoggingFilter, RedactLogsMiddleware
from middleware.performance import PerformanceMiddleware
from routers import codes, evidence, llm, rag, report, summary
from routers import auth
from routers import patient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exceptions import setup_exception_handlers

# Configure structured logging
from core.logging_config import setup_logging
from core.startup import perform_startup_checks

logger = setup_logging()

# Perform startup health checks
startup_results = perform_startup_checks()


app = FastAPI(
    title="BBB Medical Report API",
    description="Medical report generation and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger.info("Starting BBB Medical Report API")
logger.info(f"Demo mode: {settings.DEMO_MODE}")
logger.info(f"HIPAA mode: {settings.HIPAA_MODE}")
logger.info(f"RAG enabled: {settings.enable_rag}")

# Register routers
app.include_router(report.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["llm"])
app.include_router(summary.router, prefix="/api/v1", tags=["summary"])
app.include_router(evidence.router, prefix="/api/v1", tags=["evidence"])
app.include_router(codes.router, prefix="/api/v1", tags=["codes"])
app.include_router(rag.router, prefix="/api/v1", tags=["rag"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(patient.router, prefix="/api/v1", tags=["patient"])
logger.info("API routers registered successfully")

# Configure logging with PHI protection
logger = logging.getLogger("uvicorn.access")
logger.addFilter(NoBodyLoggingFilter())


# Request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request size to prevent DoS attacks"""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
            raise HTTPException(status_code=413, detail="Request too large (max 1MB)")
    return await call_next(request)


# Add middleware (order matters: last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # allow all origins
    allow_credentials=True,  # allow credentials
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # allow all methods
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With",
    ],  # allow all headers
)
app.add_middleware(RedactLogsMiddleware)
app.add_middleware(PerformanceMiddleware)

# Setup global exception handlers
setup_exception_handlers(app)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "BBB Medical Report API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server on 0.0.0.0:8082")
    uvicorn.run(app, host="0.0.0.0", port=8082)  # nosec B104 - Development server binding
