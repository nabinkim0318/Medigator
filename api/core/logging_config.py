"""
Logging configuration for the Medigator API
Centralized logging setup with sensitive-value filtering and structured formatting
"""

import logging
import logging.config
from pathlib import Path

from api.core.config import settings
from api.core.safe_logging import SensitiveLogFilter, log_info, log_warning


def setup_logging(logs_dir: str | Path = "logs"):
    """Setup structured logging configuration"""

    # Create logs directory
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(exist_ok=True)

    # Logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sensitive": {
                "()": SensitiveLogFilter,
            },
        },
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
                "filters": ["sensitive"],
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filters": ["sensitive"],
                "filename": str(logs_dir / "api.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filters": ["sensitive"],
                "filename": str(logs_dir / "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "security_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "WARNING",
                "formatter": "json",
                "filters": ["sensitive"],
                "filename": str(logs_dir / "security.log"),
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

    sensitive_filter = SensitiveLogFilter()
    for existing_logger in logging.root.manager.loggerDict.values():
        if isinstance(existing_logger, logging.Logger):
            existing_logger.addFilter(sensitive_filter)
    logging.getLogger().addFilter(sensitive_filter)

    logger = logging.getLogger("api")
    log_info(logger, "logging_initialized")
    log_info(logger, "demo_mode", enabled=settings.DEMO_MODE)
    log_info(logger, "synthetic_data_only", enabled=settings.SYNTHETIC_DATA_ONLY)
    log_info(logger, "rag_enabled", enabled=settings.enable_rag)
    log_info(logger, "rag_retrieval_mode", mode=settings.rag_retrieval_mode)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with proper naming convention"""
    return logging.getLogger(f"api.{name}")


def log_security_event(event_type: str, details: str, user_id: str | None = None):
    """Log security-related events without content payloads."""
    security_logger = logging.getLogger("security")
    log_warning(
        security_logger,
        "security_event",
        reason=event_type,
        resource=event_type,
    )


def log_performance_metric(operation: str, duration: float, details: str | None = None):
    """Log performance metrics"""
    logger = logging.getLogger("api.performance")
    log_info(
        logger, "performance", resource=operation, duration_ms=int(duration * 1000)
    )


def log_phi_access(operation: str, patient_id: str | None = None):
    """Log that a sensitive operation occurred, without identifiers."""
    security_logger = logging.getLogger("security")
    log_warning(security_logger, "sensitive_operation", resource=operation)
