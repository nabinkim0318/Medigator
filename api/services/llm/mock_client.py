# api/services/llm/mock_client.py
"""
Mock LLM client for testing without OpenAI API calls
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any

logger = logging.getLogger("llm.mock")


class MockOpenAIClient:
    """Mock OpenAI client for testing"""

    def __init__(self, **kwargs):
        self.api_key = kwargs.get("api_key", "mock-key")
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")
        logger.info("Mock OpenAI client initialized")

    async def chat_completions_create(self, **kwargs) -> dict[str, Any]:
        """Mock chat completion response"""
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "gpt-4o-mini")
        temperature = kwargs.get("temperature", 0.1)
        response_format = kwargs.get("response_format", {})

        logger.info(f"Mock LLM call: model={model}, temp={temperature}")

        # Generate mock response based on input
        mock_response = self._generate_mock_response(messages, response_format)

        return {
            "id": f"mock-{random.randint(1000, 9999)}",
            "object": "chat.completion",
            "created": int(asyncio.get_event_loop().time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": mock_response},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }

    def _generate_mock_response(self, messages: list[dict], response_format: dict) -> str:
        """Generate mock response based on input messages"""
        if not messages:
            return "Mock response"

        # Check if this is a medical summary request
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if "summary" in user_message.lower() or "hpi" in user_message.lower():
            return self._generate_medical_summary()
        if "chest pain" in user_message.lower():
            return self._generate_chest_pain_summary()
        if "diabetes" in user_message.lower():
            return self._generate_diabetes_summary()
        return self._generate_generic_summary()

    def _generate_medical_summary(self) -> str:
        """Generate mock medical summary response"""
        return json.dumps(
            {
                "hpi": "55-year-old male patient reports 2-hour history of chest pain with exertion. Pain improves with rest and radiates to left arm. Associated with diaphoresis.",
                "ros": {
                    "cardiovascular": {
                        "positive": ["chest pain", "diaphoresis"],
                        "negative": ["palpitations", "syncope"],
                    },
                    "respiratory": {
                        "positive": ["dyspnea on exertion"],
                        "negative": ["cough", "sputum"],
                    },
                    "constitutional": {
                        "positive": ["diaphoresis"],
                        "negative": ["fever", "weight loss"],
                    },
                },
                "pmh": ["hypertension"],
                "meds": ["lisinopril"],
                "flags": {
                    "ischemic_features": True,
                    "dm_followup": False,
                    "labs_a1c_needed": False,
                },
            }
        )

    def _generate_chest_pain_summary(self) -> str:
        """Generate mock chest pain summary"""
        return json.dumps(
            {
                "hpi": "Patient with acute chest pain, duration 2 hours. Pain is substernal, pressure-like, associated with exertion. Relieved by rest.",
                "ros": {
                    "cardiovascular": {
                        "positive": ["chest pain", "pressure sensation"],
                        "negative": ["palpitations"],
                    },
                    "respiratory": {"positive": ["dyspnea"], "negative": ["cough"]},
                    "constitutional": {"positive": ["diaphoresis"], "negative": ["fever"]},
                },
                "pmh": ["hypertension", "hyperlipidemia"],
                "meds": ["lisinopril", "atorvastatin"],
                "flags": {
                    "ischemic_features": True,
                    "dm_followup": False,
                    "labs_a1c_needed": False,
                },
            }
        )

    def _generate_diabetes_summary(self) -> str:
        """Generate mock diabetes summary"""
        return json.dumps(
            {
                "hpi": "Patient with type 2 diabetes mellitus for routine follow-up. Last HbA1c 6 months ago was 7.2%. No acute symptoms.",
                "ros": {
                    "cardiovascular": {"positive": [], "negative": ["chest pain", "palpitations"]},
                    "respiratory": {"positive": [], "negative": ["dyspnea", "cough"]},
                    "constitutional": {"positive": [], "negative": ["fever", "weight loss"]},
                },
                "pmh": ["type 2 diabetes mellitus", "hypertension"],
                "meds": ["metformin", "lisinopril"],
                "flags": {"ischemic_features": False, "dm_followup": True, "labs_a1c_needed": True},
            }
        )

    def _generate_generic_summary(self) -> str:
        """Generate generic mock summary"""
        return json.dumps(
            {
                "hpi": "Patient presents for evaluation. No acute symptoms reported.",
                "ros": {
                    "cardiovascular": {"positive": [], "negative": ["chest pain", "palpitations"]},
                    "respiratory": {"positive": [], "negative": ["dyspnea", "cough"]},
                    "constitutional": {"positive": [], "negative": ["fever", "weight loss"]},
                },
                "pmh": [],
                "meds": [],
                "flags": {
                    "ischemic_features": False,
                    "dm_followup": False,
                    "labs_a1c_needed": False,
                },
            }
        )


# Mock client instances
mock_sync_client = MockOpenAIClient()
mock_async_client = MockOpenAIClient()
