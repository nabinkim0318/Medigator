# api/core/persistence.py
# Demo write guard only. SQLite connections live in api.core.database.
from api.core.config import settings


def write_guard():
    if settings.DEMO_MODE:
        raise RuntimeError("Demo mode: write operations disabled")
