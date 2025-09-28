# api/services/llm/service.py
from __future__ import annotations

import json
import logging
from typing import Any

from api.services.llm.client import chat_json
from api.services.llm.fallback import templated as fallback_summary
from api.services.llm.gate import guard_and_redact
from api.services.llm.negation_processor import negation_processor
from api.services.llm.normalizer import medical_normalizer
from api.services.llm.prompts import SYSTEM
from api.services.llm.rule_engine import clinical_rule_engine
from api.services.llm.schema import SUMMARY_JSON_SCHEMA
from api.services.llm.validators import parse_and_validate as validate_out
from api.services.llm.validators import retry_with_correction

log = logging.getLogger("llm")


class LLMService:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    async def summary(self, intake: dict[str, Any]) -> dict[str, Any]:
        """Structured intake(JSON) → HPI/ROS/flags JSON with hardening"""
        log.info("Starting hardened summary generation")

        try:
            # 1) PHI protection
            safe = guard_and_redact(intake)
            log.debug("PHI redaction completed")

            # 2) Data normalization
            normalized_intake, normalization_log = (
                medical_normalizer.normalize_intake_data(safe)
            )
            log.info(
                f"Data normalization applied: {len(normalization_log)} fields processed"
            )

            # 3) Negation processing
            processed_intake, negation_log = negation_processor.process_intake_negation(
                normalized_intake
            )
            log.info(f"Negation processing completed: {negation_log}")

            # 4) Message construction with hardened prompts
            sys = SYSTEM.replace(
                "{INPUT_JSON}", json.dumps(processed_intake, ensure_ascii=False)
            )
            messages = [
                {"role": "system", "content": sys},
                {
                    "role": "user",
                    "content": json.dumps(processed_intake, ensure_ascii=False),
                },
            ]

            # 5) LLM call with stabilized parameters
            def _fallback():
                log.warning("Using fallback summary generation")
                return fallback_summary(intake)  # type: ignore

            raw = await chat_json(
                messages=messages,
                model=self.model,
                temperature=0.1,  # Low temperature for stability
                top_p=0.9,  # Controlled randomness
                response_schema=SUMMARY_JSON_SCHEMA,
                timeout_s=3.5,
                seed=42,  # Fixed seed for reproducibility
                use_cache=True,
                fallback_func=_fallback,
            )
            log.info("LLM response received")

            # 6) Enhanced validation with retry logic
            try:
                text = json.dumps(raw, ensure_ascii=False)
                out = validate_out(text)  # SummaryOut → dict conversion
                summary_data = out.model_dump()
                log.info("JSON validation successful")
            except Exception as e:
                log.warning(f"Initial validation failed, attempting correction: {e}")
                summary_data = retry_with_correction(raw)
                log.info("JSON correction successful")

            # 7) External flag calculation with rule engine
            log.info("Starting external flag calculation")
            calculated_flags, flag_justifications = (
                clinical_rule_engine.calculate_flags(processed_intake, summary_data)
            )

            # Update flags in summary
            summary_data["flags"] = calculated_flags

            # Add justification metadata for audit
            summary_data["_metadata"] = {
                "normalization_log": normalization_log,
                "negation_log": negation_log,
                "flag_justifications": flag_justifications,
                "processing_timestamp": json.dumps(
                    {"timestamp": "now"}
                ),  # Simplified for demo
            }

            log.info(f"Summary generation completed with flags: {calculated_flags}")
            return summary_data

        except Exception as e:
            log.error(f"Summary generation failed: {e}")
            log.warning("Falling back to basic summary")
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

    async def chat_completion(
        self, messages, model=None, temperature=0.7, max_tokens=1000
    ):
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
