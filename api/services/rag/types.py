# api/services/rag/types.py
from typing import TypedDict


class DocChunk(TypedDict):
    id: str
    title: str
    source: str  # "ACC/AHA 2021"
    text: str
    url: str | None


class Retrieval(TypedDict):
    chunk: DocChunk
    score: float


class EvidenceCard(TypedDict):
    title: str
    snippet: str
    source: str
    link: str | None
