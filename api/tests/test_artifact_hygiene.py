from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_IGNORE_FRAGMENTS = [
    "*.db",
    "uploads/",
    "reports/**",
    "logs/**",
    "*.pdf",
    ".env",
]


def test_gitignore_covers_runtime_artifacts():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    missing = [frag for frag in REQUIRED_IGNORE_FRAGMENTS if frag not in gi]
    assert missing == [], f"gitignore missing {missing}"


def test_tracked_tree_has_no_runtime_db_or_upload_dumps():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = result.stdout.splitlines()
    blocked_suffixes = (".db", ".sqlite", ".sqlite3", ".log")
    blocked_prefixes = ("uploads/", "api/uploads/", "logs/")
    offenders = [
        path
        for path in tracked
        if not path.endswith(".gitkeep")
        and (path.endswith(blocked_suffixes) or path.startswith(blocked_prefixes))
    ]
    assert offenders == [], f"runtime artifacts are tracked: {offenders}"


def test_synthetic_fixtures_are_not_removed():
    assert (ROOT / "data" / "intake" / "mock_patient.json").exists()
    assert (ROOT / "data" / "fhir" / "example_input.json").exists()
    assert (ROOT / "rag_index" / "synonyms.json").exists()
