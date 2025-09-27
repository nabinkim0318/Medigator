"""
FastAPI main application
Medical report generation and analysis API server
"""

import logging
import logging.config
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.middleware.log_sanitizer import NoBodyLoggingFilter, RedactLogsMiddleware
from api.middleware.performance import PerformanceMiddleware
from api.routers import codes, evidence, llm, rag, report, summary

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.exceptions import setup_exception_handlers

# Configure structured logging
from api.core.logging_config import setup_logging
from api.core.startup import perform_startup_checks

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
logger.info("API routers registered successfully")

# Configure logging with PHI protection
logger = logging.getLogger("uvicorn.access")
logger.addFilter(NoBodyLoggingFilter())

# Add middleware (order matters: last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    uvicorn.run(app, host="0.0.0.0", port=8082)
