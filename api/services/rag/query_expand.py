# api/services/rag/query_expand.py
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

_WORD = re.compile(r"[A-Za-z0-9+/.-]+")


def _normalize(s: str) -> str:
    """Normalize text: lowercase, clean whitespace, unify special characters"""
    s = s.lower()
    s = s.replace("–", "-").replace("—", "-")  # noqa: RUF001
    s = s.replace("_", " ").replace("'", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s


@lru_cache(maxsize=1)
def load_synonyms(path: str | Path) -> dict[str, list[str]]:
    """Load and normalize synonym dictionary"""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    norm = {}
    for k, vals in data.items():
        nk = _normalize(k)
        uniq = {_normalize(v) for v in vals if v.strip()}
        # Include the key itself (self-synonym)
        uniq.add(nk)
        norm[nk] = sorted(uniq)
    return norm


def expand_terms(terms: list[str], syn: dict[str, list[str]], max_per_term: int = 6) -> list[str]:
    """Expand term list with synonyms"""
    expanded: list[str] = []
    seen = set()
    for t in terms:
        nt = _normalize(t)
        candidates = syn.get(nt, [nt])
        # Limit if too many
        candidates = candidates[:max_per_term]
        for c in candidates:
            if c not in seen:
                seen.add(c)
                expanded.append(c)
    return expanded


def tokenize_query(q: str) -> list[str]:
    """Extract word/pattern tokens (including symbols like 0/1h, hs-cTn)"""
    return [m.group(0) for m in _WORD.finditer(q)]


def expand_query_text(q: str, syn: dict[str, list[str]], max_total: int = 40) -> str:
    """Expand query for embedding (space-separated)"""
    base_terms = tokenize_query(q)
    expanded = expand_terms(base_terms, syn)
    # Prevent excessive expansion
    expanded = expanded[:max_total]
    # For embedding: space-separated (enhance semantic signals)
    return " ".join(expanded)


def bm25_or_clause(q: str, syn: dict[str, list[str]], max_per_term: int = 6) -> str:
    """
    Expand synonyms into OR groups for BM25 string query:
    Example: hs-troponin -> ("hs troponin" OR "hs ctn" OR "high sensitivity troponin")
    """
    terms = tokenize_query(q)
    groups = []
    for t in terms:
        nt = _normalize(t)
        cand = syn.get(nt, [nt])[:max_per_term]
        # Quote phrases containing spaces
        cand = [f'"{c}"' if " " in c else c for c in cand]
        group = "(" + " OR ".join(cand) + ")"
        groups.append(group)
    # Connect groups with AND (adjust if needed)
    return " AND ".join(groups)


def boost_key_terms(q: str, syn: dict[str, list[str]], key_terms: list[str] | None = None) -> str:
    """
    Boost key terms with weights (2x repetition for embedding weight↑)
    """
    if not key_terms:
        return q

    expanded = expand_query_text(q, syn)
    terms = expanded.split()

    # Repeat key terms 2x
    boosted = []
    for term in terms:
        boosted.append(term)
        if any(key in term.lower() for key in key_terms):
            boosted.append(term)  # Repeat key terms 2x

    return " ".join(boosted)
