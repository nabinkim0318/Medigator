"""
Logging configuration for BBB Medical Report API
Centralized logging setup with PHI protection and structured formatting
"""

import logging
import logging.config
from pathlib import Path

from api.core.config import settings


def setup_logging():
    """Setup structured logging configuration"""

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/api.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "security_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "WARNING",
                "formatter": "json",
                "filename": "logs/security.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "api": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "api.services": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "api.routers": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "security": {
                "handlers": ["security_file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    # Apply configuration
    logging.config.dictConfig(logging_config)

    # Log startup information
    logger = logging.getLogger("api")
    logger.info("BBB Medical Report API logging initialized")
    logger.info(f"Demo mode: {settings.DEMO_MODE}")
    logger.info(f"HIPAA mode: {settings.HIPAA_MODE}")
    logger.info(f"RAG enabled: {settings.enable_rag}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with proper naming convention"""
    return logging.getLogger(f"api.{name}")


def log_security_event(event_type: str, details: str, user_id: str | None = None):
    """Log security-related events"""
    security_logger = logging.getLogger("security")
    security_logger.warning(
        f"Security event: {event_type} - {details} - User: {user_id or 'Unknown'}",
    )


def log_performance_metric(operation: str, duration: float, details: str | None = None):
    """Log performance metrics"""
    logger = logging.getLogger("api.performance")
    logger.info(f"Performance: {operation} took {duration:.3f}s - {details or ''}")


def log_phi_access(operation: str, patient_id: str | None = None):
    """Log PHI access events (HIPAA compliance)"""
    if settings.HIPAA_MODE:
        security_logger = logging.getLogger("security")
        security_logger.warning(
            f"PHI Access: {operation} - Patient: {patient_id or 'Unknown'}"
        )
