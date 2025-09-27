# api/services/codes/icd.py
import re
from typing import Any

from .engine import ICDRule


def _search_text(summary: dict[str, Any], intake: dict[str, Any]) -> str:
    parts = []
    parts.append(summary.get("hpi", ""))
    ros = summary.get("ros", {})
    for sys in ("cardiovascular", "respiratory", "constitutional"):
        sec = ros.get(sys, {})
        parts += sec.get("positive", []) + sec.get("negative", [])
    ans = intake.get("answers", {})
    parts += [str(v) for v in ans.values() if isinstance(v, str)]
    return " ".join(parts).lower()


def suggest_icd(
    rules: list[ICDRule],
    summary: dict[str, Any],
    intake: dict[str, Any],
    emr: dict[str, Any],
    k: int = 3,
) -> list[dict[str, Any]]:
    flags = summary.get("flags", {}) or {}
    text = _search_text(summary, intake)
    ctx_tokens = set(re.findall(r"[a-z0-9]+", text))
    candidates = []
    for r in rules:
        if r.requires_flag and not flags.get(r.requires_flag, False):
            continue
        if not r.pattern.search(text):
            continue
        if r.excludes and r.excludes.search(text):
            continue
        score = r.weight
        # specificity correction (simple rules)
        if r.code.startswith("R07") and ("precordial" in ctx_tokens):
            score += 0.07
        if "left" in ctx_tokens and "arm" in ctx_tokens:
            score += 0.05
        candidates.append(
            {
                "code": r.code,
                "label": r.label,
                "score": round(score, 3),
                "rationale_key": r.rationale_key,
                "tags": ["symptom"] if r.code.startswith("R") else ["diagnosis"],
            },
        )
    # symptom first sort
    candidates.sort(key=lambda x: (not str(x["code"]).startswith("R"), x["score"]), reverse=True)
    return candidates[:k]
