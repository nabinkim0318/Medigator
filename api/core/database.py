"""Canonical SQLite helper for this research prototype.

There is one runtime database, configured via settings.db_url / DB_URL.
PostgreSQL is not implemented. Importing this module does not create files.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from api.core.config import settings

REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RELATIVE_PATH = Path("data") / "medigator.db"
DEFAULT_DB_URL = "sqlite:///data/medigator.db"


def get_database_path(db_url: str | None = None) -> Path:
    """Resolve the configured SQLite path without creating files."""
    raw = (settings.db_url if db_url is None else db_url) or ""
    raw = raw.strip()
    if not raw:
        return (REPO_ROOT / CANONICAL_RELATIVE_PATH).resolve()

    if "://" in raw and not raw.startswith("sqlite:"):
        raise ValueError(
            "Only SQLite DB_URL values are supported by this research prototype"
        )

    if raw.startswith("sqlite:"):
        # sqlite:///relative.db  -> relative.db
        # sqlite:////abs/path.db -> /abs/path.db
        remainder = raw[len("sqlite:") :]
        path_part = (
            remainder[3:] if remainder.startswith("///") else remainder.lstrip("/")
        )
        path = Path(path_part)
    else:
        path = Path(raw)

    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def connect_db(
    *, row_factory: bool = True, db_url: str | None = None
) -> sqlite3.Connection:
    """Open the configured SQLite database, creating parent dirs if needed."""
    path = get_database_path(db_url)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    if row_factory:
        conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_connection(
    *, row_factory: bool = True, db_url: str | None = None
) -> Iterator[sqlite3.Connection]:
    conn = connect_db(row_factory=row_factory, db_url=db_url)
    try:
        yield conn
    finally:
        conn.close()
