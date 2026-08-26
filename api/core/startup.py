"""
Startup checks and initialization logging
Database and service health checks on application startup
"""

import logging
from pathlib import Path

from api.core.config import settings
from api.core.database import connect_db, get_database_path
from api.services.rag.retrieve import USE_RAG

logger = logging.getLogger(__name__)


def check_database_connection():
    """Check database connectivity and log status"""
    try:
        db_path = get_database_path()
        if db_path.exists():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()

            logger.info("Database connection successful")
            logger.info("Found %s tables", len(tables))
            return True
        logger.warning("Database file not found")
        return False
    except Exception:
        logger.error("Database connection failed")
        return False


def check_rag_system():
    """Check RAG system availability and log status"""
    if not USE_RAG:
        logger.info("RAG system disabled in configuration")
        return True

    try:
        # Lazy loading: Defer RAG initialization to first use
        logger.info(
            "RAG retrieval mode=%s; initialized on first use",
            settings.rag_retrieval_mode,
        )
        return True
    except Exception:
        logger.warning("RAG system check failed")
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
    except Exception:
        logger.error("File permission check failed")
        return False


def check_environment_variables():
    """Check critical environment variables and log status"""
    critical_vars = {
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "DEMO_MODE": settings.DEMO_MODE,
        "HIPAA_MODE": settings.HIPAA_MODE,
    }

    for var_name, var_value in critical_vars.items():
        if "KEY" in var_name:
            if var_value:
                logger.info("Environment variable %s is set", var_name)
            else:
                logger.warning("Environment variable %s is unset", var_name)
        else:
            logger.info("Environment variable %s configured", var_name)


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
        except Exception:
            logger.error("%s check failed", check_name)
            results[check_name] = False

    # Log environment variables
    check_environment_variables()

    # Summary
    passed = sum(results.values())
    total = len(results)
    logger.info(f"Startup checks completed: {passed}/{total} passed")

    if passed < total:
        logger.warning(
            "Some startup checks failed - application may not function correctly"
        )

    return results
