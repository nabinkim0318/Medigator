from __future__ import annotations

import pytest

from api.core.config import settings


@pytest.fixture(autouse=True)
def isolate_sqlite(monkeypatch, tmp_path):
    """Keep API tests off the repository runtime database."""
    monkeypatch.setattr(
        settings, "db_url", f"sqlite:///{tmp_path / 'medigator-test.db'}"
    )
