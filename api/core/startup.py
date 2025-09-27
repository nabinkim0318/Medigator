"""
Startup checks and initialization logging
Database and service health checks on application startup
"""

import logging
import os
import sqlite3
from pathlib import Path

from api.core.config import settings
from api.services.rag.retrieve import USE_RAG, init_retriever

logger = logging.getLogger(__name__)


def check_database_connection():
    """Check database connectivity and log status"""
    try:
        db_path = settings.db_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()

            logger.info(f"Database connection successful: {db_path}")
            logger.info(f"Found {len(tables)} tables: {[table[0] for table in tables]}")
            return True
        logger.warning(f"Database file not found: {db_path}")
        return False
    except Exception as e:
        logger.error(f"Database connection failed: {e!s}")
        return False


def check_rag_system():
    """Check RAG system availability and log status"""
    if not USE_RAG:
        logger.info("RAG system disabled in configuration")
        return True

    try:
        init_retriever()
        logger.info("RAG system initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"RAG system initialization failed: {e!s}")
        return False


def check_file_permissions():
    """Check file system permissions for logs and reports"""
    try:
        # Check logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        test_file = logs_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        logger.info("Logs directory permissions OK")

        # Check reports directory
        reports_dir = Path(settings.PDF_OUTPUT_DIR)
        reports_dir.mkdir(exist_ok=True)
        test_file = reports_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        logger.info("Reports directory permissions OK")

        return True
    except Exception as e:
        logger.error(f"File permission check failed: {e!s}")
        return False


def check_environment_variables():
    """Check critical environment variables and log status"""
    critical_vars = {
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "DEMO_MODE": settings.DEMO_MODE,
        "HIPAA_MODE": settings.HIPAA_MODE,
    }

    for var_name, var_value in critical_vars.items():
        if var_value is None:
            logger.warning(f"Environment variable {var_name} not set")
        # Mask sensitive values
        elif "KEY" in var_name:
            masked_value = f"{str(var_value)[:8]}..." if var_value else "None"
            logger.info(f"{var_name}: {masked_value}")
        else:
            logger.info(f"{var_name}: {var_value}")


def perform_startup_checks():
    """Perform all startup checks and log results"""
    logger.info("Starting application health checks...")

    checks = {
        "Database": check_database_connection,
        "RAG System": check_rag_system,
        "File Permissions": check_file_permissions,
    }

    results = {}
    for check_name, check_func in checks.items():
        try:
            results[check_name] = check_func()
        except Exception as e:
            logger.error(f"{check_name} check failed with exception: {e!s}")
            results[check_name] = False

    # Log environment variables
    check_environment_variables()

    # Summary
    passed = sum(results.values())
    total = len(results)
    logger.info(f"Startup checks completed: {passed}/{total} passed")

    if passed < total:
        logger.warning("Some startup checks failed - application may not function correctly")

    return results
