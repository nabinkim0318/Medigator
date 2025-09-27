# api/services/rag/summarize.py
from __future__ import annotations
from typing import List, Dict
import re

MAX_CHARS = 220
WS = re.compile(r"\s+")

def _clean(text: str) -> str:
    text = WS.sub(" ", (text or "").strip())
    return text[:MAX_CHARS].rstrip()

def to_cards(rets: List[Dict], max_cards: int = 2) -> List[Dict[str, str]]:
    seen = set()
    cards = []
    for r in rets:
        chunk = r.get("chunk", {})
        title = (chunk.get("title") or "").strip()
        source = (chunk.get("source") or "").strip()
        key = (title, source)
        if key in seen:
            continue
        seen.add(key)
        
        # Parse tags_json if available
        tags = {}
        try:
            tags_json = chunk.get("tags_json")
            if isinstance(tags_json, str):
                import json
                tags = json.loads(tags_json)
            elif isinstance(tags_json, dict):
                tags = tags_json
        except (json.JSONDecodeError, TypeError):
            tags = {}
        
        cards.append({
            "title": title or source or "Evidence",
            "snippet": _clean(chunk.get("text") or ""),
            "source": source or title or "",
            "link": chunk.get("url") or "",
            "year": chunk.get("year") or "",           # NEW
            "section": chunk.get("section") or "",     # NEW
            "tags": tags,                              # NEW (for frontend chips)
        })
        if len(cards) >= max_cards:
            break
    return cards
