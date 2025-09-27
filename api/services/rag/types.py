# api/services/rag/types.py
from typing import Any, TypedDict


class DocChunk(TypedDict):
    id: str
    title: str
    source: str  # "ACC/AHA 2021"
    text: str
    url: str | None
    file: str | None
    start: int | None
    end: int | None
    year: int | None
    section: str | None
    tags_json: dict[str, Any] | None


class Retrieval(TypedDict):
    chunk: DocChunk
    score: float


class EvidenceCard(TypedDict):
    title: str
    snippet: str
    source: str
    link: str | None
