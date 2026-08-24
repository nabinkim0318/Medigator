"""
Scan the current tree and git history for secret-like patterns.

This test reports rule name + path + line number only. It never prints matched
values. Placeholder example files are allowlisted.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

ROOT = Path(__file__).resolve().parents[2]

RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "pem_private_key",
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    ),
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "generic_assigned_secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret_key|aws_secret|private_key)\s*[:=]\s*['\"][^'\"]{16,}['\"]"
        ),
    ),
]

ALLOWLIST_PATHS = {
    "api/.env.example",
    ".env.example",
}

SKIP_DIR_PARTS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    ".next",
    "__pycache__",
}


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".faiss",
            ".pdf",
        }:
            continue
        files.append(path)
    return files


def _scan_text(path: Path, text: str) -> list[tuple[str, str, int]]:
    rel = str(path.relative_to(ROOT))
    if rel in ALLOWLIST_PATHS:
        return []
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "your_key" in line or "replace-me-locally" in line:
            continue
        for name, pattern in RULES:
            if pattern.search(line):
                hits.append((name, rel, lineno))
    return hits


def test_current_tree_has_no_literal_secrets():
    hits: list[tuple[str, str, int]] = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits.extend(_scan_text(path, text))
    assert hits == [], f"secret-like patterns in current tree: {hits}"


def test_git_history_scan_reports_paths_only():
    result = subprocess.run(
        [
            "git",
            "grep",
            "-I",
            "-n",
            "-E",
            r"BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|AKIA[0-9A-Z]{16}",
            "HEAD",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    # git grep exits 1 when there are no matches.
    assert result.returncode in {0, 1}
    if result.returncode == 0:
        locations = []
        for line in result.stdout.splitlines():
            loc = line.split(":", 2)[:2]
            locations.append(":".join(loc))
        assert False, f"secret-like patterns in HEAD tree: {locations}"
