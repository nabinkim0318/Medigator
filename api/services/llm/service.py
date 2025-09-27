# api/services/llm/service.py
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from services.llm.client import chat_json
from services.llm.fallback import templated as fallback_summary
from services.llm.gate import guard_and_redact
from services.llm.prompts import SYSTEM
from services.llm.schema import SUMMARY_JSON_SCHEMA
from services.llm.validators import parse_and_validate as validate_out

log = logging.getLogger("llm")


class LLMService:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    async def summary(self, intake: dict[str, Any]) -> dict[str, Any]:
        """Structured intake(JSON) → HPI/ROS/flags JSON"""
        # 1) PHI 보호
        safe = guard_and_redact(intake)

        # 2) 메시지 구성
        sys = SYSTEM
        usr = sys.replace("{INPUT_JSON}", json.dumps(safe, ensure_ascii=False))
        messages = [
            {"role": "system", "content": "You are a precise clinical summarizer."},
            {"role": "user", "content": usr},
        ]

        # 3) LLM 호출 + 폴백
        def _fallback():
            return fallback_summary(intake)  # type: ignore

        raw = await chat_json(
            messages=messages,
            model=self.model,
            temperature=0.1,
            response_schema=SUMMARY_JSON_SCHEMA,
            timeout_s=3.5,
            seed=42,
            use_cache=True,
            fallback_func=_fallback,
        )

        # 4) 검증/정화 → pydantic 모델로 보정
        try:
            text = json.dumps(raw, ensure_ascii=False)
            out = validate_out(text)  # SummaryOut → dict로 반환
            return out.model_dump()
        except Exception as e:
            log.warning(f"validation failed, using fallback: {e}")
            return fallback_summary(intake)  # type: ignore

    # Placeholder methods for compatibility (hackathon scope)
    async def medical_analysis(self, symptoms, patient_age, medical_history):
        # Placeholder implementation
        return {
            "primary_diagnosis": "General evaluation needed",
            "differential_diagnoses": [],
            "recommended_tests": [],
            "risk_level": "Low",
            "urgency": "Routine",
            "treatment_recommendations": [],
        }

    async def generate_report(self, patient_data, analysis_data):
        # Placeholder implementation
        return {"report": "Generated medical report"}

    async def treatment_plan(self, diagnosis, patient_data):
        # Placeholder implementation
        return {"plan": "Treatment plan generated"}

    async def extract_entities(self, text):
        # Placeholder implementation
        return {
            "symptoms": [],
            "diagnoses": [],
            "body_parts": [],
            "vital_signs": [],
        }

    async def summarize_medical_notes(self, notes):
        # Placeholder implementation
        return "Medical notes summarized"

    async def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=1000):
        # Placeholder implementation
        return {"response": "Chat completion response"}

    async def generate_medical_report(self, patient_data, analysis_data):
        # Placeholder implementation
        return {"report": "Generated medical report"}

    async def suggest_treatment_plan(self, diagnosis, patient_data):
        # Placeholder implementation
        return {"plan": "Treatment plan generated"}

    async def analyze_symptoms(self, symptoms, patient_age, medical_history):
        # Placeholder implementation
        return {
            "primary_diagnosis": "General evaluation needed",
            "differential_diagnoses": [],
            "recommended_tests": [],
            "risk_level": "Low",
            "urgency": "Routine",
            "treatment_recommendations": [],
        }

    async def suggest_treatment(self, diagnosis, patient_data):
        # Placeholder implementation
        return {"treatment": "Treatment suggested"}


llm_service = LLMService()
