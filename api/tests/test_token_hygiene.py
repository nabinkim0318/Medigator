from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

QUERY_TOKEN = re.compile(r"\?token=")
SEARCH_TOKEN = re.compile(r"searchParams.*get\(\s*[\"']token[\"']")
VISIBLE_TOKEN_LABEL = re.compile(r"Auth token:")


def test_frontend_does_not_put_tokens_in_query_strings():
    hits = []
    for path in SRC.rglob("*.tsx"):
        text = path.read_text(encoding="utf-8")
        if QUERY_TOKEN.search(text) or SEARCH_TOKEN.search(text):
            hits.append(str(path.relative_to(ROOT)))
    assert hits == [], f"token query-string usage remains in {hits}"


def test_frontend_does_not_render_access_tokens():
    hits = []
    for path in SRC.rglob("*.tsx"):
        text = path.read_text(encoding="utf-8")
        if VISIBLE_TOKEN_LABEL.search(text) or "Token copied to clipboard" in text:
            hits.append(str(path.relative_to(ROOT)))
    assert hits == [], f"visible token UI remains in {hits}"


def test_demo_session_helper_exists():
    helper = SRC / "lib" / "demoSession.ts"
    assert helper.exists()
    text = helper.read_text(encoding="utf-8")
    assert "sessionStorage" in text
    assert "operator_session" in text or "OPERATOR_SESSION_KEY" in text
    assert "crypto.randomUUID" in text
