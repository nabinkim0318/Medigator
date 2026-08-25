from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.rag.eval import evaluate


def test_golden_queries_hit_expected_demo_files():
    result = evaluate(k=5, use_query_expansion=True)
    assert result["n"] >= 6
    assert result["mmr"] is False
    assert result["hit_at_k"] >= 5 / 6, result["rows"]
    missed = [row["id"] for row in result["rows"] if not row["hit"]]
    assert missed == [] or result["hits"] >= 5, missed


def test_eval_does_not_claim_mmr():
    result = evaluate(k=5)
    assert result["mmr"] is False
    assert "not mmr" in result["note"].lower()


def test_readme_does_not_claim_mmr_diversity():
    readme = Path(__file__).resolve().parents[2] / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert "MMR diversity" not in text
    assert "MMR is not implemented" in text
