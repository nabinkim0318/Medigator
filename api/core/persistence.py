# api/core/persistence.py
from core.config import settings


def write_guard():
    if settings.DEMO_MODE:
        raise RuntimeError("Demo mode: write operations disabled")
