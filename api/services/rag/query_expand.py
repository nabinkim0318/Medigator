# api/services/rag/query_expand.py
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

_WORD = re.compile(r"[A-Za-z0-9+/.-]+")


def _normalize(s: str) -> str:
    """소문자, 다중 공백 정리, 특수기호 통일"""
    s = s.lower()
    s = s.replace("–", "-").replace("—", "-")  # noqa: RUF001
    s = s.replace("_", " ").replace("'", "'")
    s = re.sub(r"\s+", " ", s).strip()
    return s


@lru_cache(maxsize=1)
def load_synonyms(path: str | Path) -> dict[str, list[str]]:
    """동의어 사전 로드 및 정규화"""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    norm = {}
    for k, vals in data.items():
        nk = _normalize(k)
        uniq = {_normalize(v) for v in vals if v.strip()}
        # 키 자체도 포함(자기 동의어)
        uniq.add(nk)
        norm[nk] = sorted(uniq)
    return norm


def expand_terms(terms: list[str], syn: dict[str, list[str]], max_per_term: int = 6) -> list[str]:
    """용어 리스트를 동의어로 확장"""
    expanded: list[str] = []
    seen = set()
    for t in terms:
        nt = _normalize(t)
        candidates = syn.get(nt, [nt])
        # 너무 많으면 자르기
        candidates = candidates[:max_per_term]
        for c in candidates:
            if c not in seen:
                seen.add(c)
                expanded.append(c)
    return expanded


def tokenize_query(q: str) -> list[str]:
    """단어/패턴 토큰들을 추출(0/1h, hs-cTn 같은 기호 포함)"""
    return [m.group(0) for m in _WORD.finditer(q)]


def expand_query_text(q: str, syn: dict[str, list[str]], max_total: int = 40) -> str:
    """임베딩용 질의 확장 (공백으로 연결)"""
    base_terms = tokenize_query(q)
    expanded = expand_terms(base_terms, syn)
    # 과도한 팽창 방지
    expanded = expanded[:max_total]
    # 임베딩용: 공백으로 나열 (의미 신호 강화)
    return " ".join(expanded)


def bm25_or_clause(q: str, syn: dict[str, list[str]], max_per_term: int = 6) -> str:
    """
    BM25 문자열 쿼리에서 동의어를 OR 그룹으로 확장:
    예: hs-troponin -> ("hs troponin" OR "hs ctn" OR "high sensitivity troponin")
    """
    terms = tokenize_query(q)
    groups = []
    for t in terms:
        nt = _normalize(t)
        cand = syn.get(nt, [nt])[:max_per_term]
        # 공백 포함 구절은 따옴표로 감싸기
        cand = [f'"{c}"' if " " in c else c for c in cand]
        group = "(" + " OR ".join(cand) + ")"
        groups.append(group)
    # 그룹을 AND로 연결 (필요 시 조정)
    return " AND ".join(groups)


def boost_key_terms(q: str, syn: dict[str, list[str]], key_terms: list[str] | None = None) -> str:
    """
    핵심 용어에 가중치 부여 (2회 반복으로 임베딩 가중치↑)
    """
    if not key_terms:
        return q

    expanded = expand_query_text(q, syn)
    terms = expanded.split()

    # 핵심 용어 2회 반복
    boosted = []
    for term in terms:
        boosted.append(term)
        if any(key in term.lower() for key in key_terms):
            boosted.append(term)  # 핵심 용어 2회 반복

    return " ".join(boosted)
