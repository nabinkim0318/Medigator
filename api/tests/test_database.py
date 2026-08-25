from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.core.config import Settings, settings
from api.core.database import (
    CANONICAL_RELATIVE_PATH,
    DEFAULT_DB_URL,
    REPO_ROOT,
    connect_db,
    get_database_path,
)

OBSOLETE_RUNTIME_NAMES = ("copilot.db", "data/app.db")
RUNTIME_SCAN_ROOTS = [
    REPO_ROOT / "api" / "core",
    REPO_ROOT / "api" / "routers",
    REPO_ROOT / "api" / "services",
    REPO_ROOT / "api" / "db",
    REPO_ROOT / "scripts",
    REPO_ROOT / "docker",
]
RUNTIME_SCAN_FILES = [
    REPO_ROOT / "api" / "main.py",
    REPO_ROOT / "api" / ".env.example",
    REPO_ROOT / "Makefile",
]


def test_settings_default_url_is_canonical():
    assert Settings.model_fields["db_url"].default == DEFAULT_DB_URL
    assert CANONICAL_RELATIVE_PATH.as_posix() == "data/medigator.db"


def test_default_path_resolves_under_repo(monkeypatch):
    monkeypatch.delenv("DB_URL", raising=False)
    monkeypatch.setattr(settings, "db_url", DEFAULT_DB_URL)
    assert get_database_path() == (REPO_ROOT / CANONICAL_RELATIVE_PATH).resolve()


def test_override_uses_tmp_path(monkeypatch, tmp_path):
    target = tmp_path / "test.db"
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{target}")
    assert get_database_path() == target.resolve()
    assert not target.exists()


def test_parent_dirs_created_only_on_connect(monkeypatch, tmp_path):
    target = tmp_path / "nested" / "dir" / "test.db"
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{target}")
    assert get_database_path() == target.resolve()
    assert not target.parent.exists()
    conn = connect_db()
    conn.close()
    assert target.parent.is_dir()
    assert target.exists()


def test_override_does_not_write_repo_runtime_db(monkeypatch, tmp_path):
    canonical = REPO_ROOT / CANONICAL_RELATIVE_PATH
    existed = canonical.exists()
    target = tmp_path / "isolated.db"
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{target}")
    conn = connect_db()
    conn.execute("CREATE TABLE ping (v TEXT)")
    conn.execute("INSERT INTO ping VALUES ('ok')")
    conn.commit()
    conn.close()
    assert target.exists()
    assert canonical.exists() is existed


def test_two_helper_connections_see_the_same_db(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{tmp_path / 'shared.db'}")
    conn = connect_db()
    conn.execute("CREATE TABLE ping (id INTEGER PRIMARY KEY, v TEXT)")
    conn.execute("INSERT INTO ping (v) VALUES ('hello')")
    conn.commit()
    conn.close()

    other = connect_db()
    row = other.execute("SELECT v FROM ping").fetchone()
    other.close()
    assert row["v"] == "hello"


def test_get_database_path_does_not_create_files(monkeypatch, tmp_path):
    target = tmp_path / "nope" / "untouched.db"
    monkeypatch.setattr(settings, "db_url", f"sqlite:///{target}")
    path = get_database_path()
    assert path == target.resolve()
    assert not target.exists()
    assert not target.parent.exists()


def test_obsolete_runtime_db_paths_are_absent():
    files: list[Path] = list(RUNTIME_SCAN_FILES)
    for root in RUNTIME_SCAN_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file())

    hits: list[str] = []
    for path in files:
        if path.suffix.lower() in {".pyc", ".png", ".jpg"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(REPO_ROOT).as_posix()
        for needle in OBSOLETE_RUNTIME_NAMES:
            if needle in text:
                hits.append(f"{rel}:{needle}")
    assert hits == [], f"obsolete runtime DB paths remain: {hits}"
