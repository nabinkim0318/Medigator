# api/services/rag/summarize.py
from __future__ import annotations

import logging
import re
from typing import Any

# Get logger
logger = logging.getLogger(__name__)

MAX_CHARS = 220
WS = re.compile(r"\s+")


def _clean(text: str) -> str:
    text = WS.sub(" ", (text or "").strip())
    return text[:MAX_CHARS].rstrip()


def to_cards(
    rets: list[dict], max_cards: int = 2, keywords: list[str] | None = None
) -> list[dict[str, Any]]:
    logger.info(f"Converting {len(rets)} RAG results to {max_cards} evidence cards")

    # 1. sort bsed on score
    ranked = sorted(rets, key=lambda x: x.get("score", 0), reverse=True)

    seen = set()
    cards = []

    for rank, r in enumerate(ranked, start=1):
        chunk = r.get("chunk", {})
        title = (chunk.get("title") or "").strip()
        source = (chunk.get("source") or "").strip()

        # duplicate check (title, year, section combination)
        key = (
            title.lower(),
            str(chunk.get("year", "")),
            chunk.get("section", "").lower(),
        )
        if key in seen:
            logger.debug(f"Skipping duplicate card: {title}")
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

        # keyword highlight (optional)
        snippet = _clean(chunk.get("text") or "")
        if keywords:
            for kw in keywords:
                if kw.lower() in snippet.lower():
                    snippet = snippet.replace(kw, f"**{kw}**")

        cards.append(
            {
                "rank": rank,
                "score": float(r.get("score", 0.0)),
                "title": title or source or "Evidence",
                "snippet": snippet,
                "source": source or title or "",
                "link": chunk.get("url") or "",
                "year": chunk.get("year") or "",
                "section": chunk.get("section") or "",
                "tags": tags,
            }
        )

        if len(cards) >= max_cards:
            break

    logger.info(f"Generated {len(cards)} evidence cards")
    return cards
