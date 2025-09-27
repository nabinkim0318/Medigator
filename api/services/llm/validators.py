# api/services/llm/validators.py
import json
import re

from core.schemas import SummaryOut

FORBIDDEN = re.compile(
    r"(diagnos|treat|prescrib|admit|discharge|risk\s*%|riskpercent|risk\s*percent|probabilit)",
    re.IGNORECASE,
)
SENTENCE_SPLIT = re.compile(r"(?<=[\.\!\?])\s+")


def parse_and_validate(text: str) -> SummaryOut:
    data = json.loads(text or "{}")
    out = SummaryOut.model_validate(data)
    sentences = SENTENCE_SPLIT.split(out.hpi)
    clean = [s for s in sentences if not FORBIDDEN.search(s)]
    out.hpi = " ".join(s.strip() for s in clean if s.strip())
    return out
