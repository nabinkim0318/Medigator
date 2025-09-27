# api/services/llm/tasks/summarize.py
import json
import logging

from api.core.schemas import SummaryIn, SummaryOut
from api.services.llm.client import chat_json
from api.services.llm.fallback import templated
from api.services.llm.gate import guard_and_redact
from api.services.llm.prompts import SYSTEM
from api.services.llm.schema import SUMMARY_JSON_SCHEMA
from api.services.llm.validators import parse_and_validate

logger = logging.getLogger(__name__)


async def run(body: SummaryIn) -> SummaryOut:
    """
    Generate medical summary using LLM with fallback support
    """
    try:
        # Keep instructions in system, put raw JSON in user message
        system_prompt = SYSTEM
        payload = guard_and_redact(body.model_dump())
        user_payload = json.dumps(payload, ensure_ascii=False)

        data = await chat_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload},
            ],
            response_schema=SUMMARY_JSON_SCHEMA,
            fallback_func=lambda: templated(body),
        )

        # Apply validator with FORBIDDEN scrub on success path
        try:
            return parse_and_validate(json.dumps(data))
        except Exception:
            return SummaryOut.model_validate(data)

    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return SummaryOut.model_validate(templated(body))
