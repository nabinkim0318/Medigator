"""
LLM API Router
Advanced LLM API endpoints for medical analysis
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.core.config import settings
from api.core.exceptions import LLMServiceException
from api.services.llm import llm_service

# Get logger
logger = logging.getLogger(__name__)


# Pydantic models
class MedicalAnalysisRequest(BaseModel):
    """Medical analysis request model"""

    symptoms: list[str]
    patient_age: int
    medical_history: list[str] | None = None


class MedicalAnalysisResponse(BaseModel):
    """Medical analysis response model"""

    primary_diagnosis: str | None = None
    differential_diagnoses: list[str] | None = None
    recommended_tests: list[str] | None = None
    risk_level: str | None = None
    urgency: str | None = None
    treatment_recommendations: list[str] | None = None


class ReportGenerationRequest(BaseModel):
    """Report generation request model"""

    patient_data: dict[str, Any]
    symptoms: list[str]
    provider_notes: str
    test_results: dict[str, Any] | None = None


class TreatmentPlanRequest(BaseModel):
    """Treatment plan request model"""

    diagnosis: str
    patient_age: int
    medical_history: list[str] | None = None
    allergies: list[str] | None = None


class EntityExtractionRequest(BaseModel):
    """Entity extraction request model"""

    text: str


class EntityExtractionResponse(BaseModel):
    """Entity extraction response model"""

    symptoms: list[str]
    medications: list[str]
    conditions: list[str]
    procedures: list[str]
    diagnoses: list[str] = []
    body_parts: list[str] = []
    vital_signs: list[str] = []


class NoteSummarizationRequest(BaseModel):
    """Note summarization request model"""

    notes: list[str]


class ChatRequest(BaseModel):
    """Chat request model"""

    messages: list[dict[str, str]]
    model: str | None = "gpt-4o-mini"
    temperature: float | None = 0.1
    max_tokens: int | None = 1000


# Router creation
router = APIRouter()


# Demo mode guard for advanced LLM features
def _demo_guard():
    if settings.DEMO_MODE:
        raise HTTPException(
            status_code=503,
            detail="Advanced LLM features disabled in demo mode. Use /summary, /evidence, or /codes endpoints instead.",
        )


@router.post("/analyze", response_model=MedicalAnalysisResponse)
async def analyze_symptoms(request: MedicalAnalysisRequest):
    """
    Analyze symptoms using LLM

    Args:
        request: Medical analysis request

    Returns:
        Analysis results
    """
    logger.info(
        "Medical analysis requested",
    )
    _demo_guard()
    try:
        analysis = await llm_service.medical_analysis(
            symptoms=request.symptoms,
            patient_age=request.patient_age,
            medical_history=request.medical_history,
        )

        return MedicalAnalysisResponse(
            primary_diagnosis=analysis.get("primary_diagnosis"),
            differential_diagnoses=analysis.get("differential_diagnoses", []),
            recommended_tests=analysis.get("recommended_tests", []),
            risk_level=analysis.get("risk_level"),
            urgency=analysis.get("urgency"),
            treatment_recommendations=analysis.get("treatment_recommendations", []),
        )

    except HTTPException:
        raise
    except Exception:
        logger.error("Medical analysis failed")
        raise LLMServiceException(
            message="Medical analysis failed",
        )


@router.post("/generate-report")
async def generate_medical_report(request: ReportGenerationRequest):
    """
    Generate comprehensive medical report

    Args:
        request: Report generation request

    Returns:
        Generated report
    """
    try:
        _demo_guard()
        report = await llm_service.generate_medical_report(
            patient_data=request.patient_data,
            analysis_data={
                "symptoms": request.symptoms,
                "provider_notes": request.provider_notes,
                "test_results": request.test_results,
            },
        )

        return {
            "report": report,
            "generated_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception:
        logger.error("Report generation failed")
        raise HTTPException(status_code=500, detail="Report generation error")


@router.post("/treatment-plan")
async def suggest_treatment_plan(request: TreatmentPlanRequest):
    """
    Research-prototype care-plan sketch. Not a treatment recommendation.

    Args:
        request: Treatment plan request

    Returns:
        Treatment plan
    """
    _demo_guard()
    try:
        plan = await llm_service.suggest_treatment_plan(
            diagnosis=request.diagnosis,
            patient_data={
                "age": request.patient_age,
                "medical_history": request.medical_history,
                "allergies": request.allergies,
            },
        )

        return plan

    except HTTPException:
        raise
    except Exception:
        logger.error("Treatment plan generation failed")
        raise HTTPException(status_code=500, detail="Treatment plan error")


@router.post("/extract-entities", response_model=EntityExtractionResponse)
async def extract_medical_entities(request: EntityExtractionRequest):
    """
    Extract medical entities from text

    Args:
        request: Entity extraction request

    Returns:
        Extracted entities
    """
    try:
        _demo_guard()
        entities = await llm_service.extract_entities(request.text)

        return EntityExtractionResponse(
            symptoms=entities.get("symptoms", []),
            medications=entities.get("medications", []),
            conditions=entities.get("conditions", []),
            procedures=entities.get("procedures", []),
            diagnoses=entities.get("diagnoses", []),
            body_parts=entities.get("body_parts", []),
            vital_signs=entities.get("vital_signs", []),
        )

    except HTTPException:
        raise
    except Exception:
        logger.error("Entity extraction failed")
        raise HTTPException(status_code=500, detail="Entity extraction error")


@router.post("/summarize-notes")
async def summarize_medical_notes(request: NoteSummarizationRequest):
    """
    Summarize medical notes

    Args:
        request: Note summarization request

    Returns:
        Summarized notes
    """
    try:
        _demo_guard()
        summary = await llm_service.summarize_medical_notes(request.notes)

        return {
            "summary": summary,
            "original_notes_count": len(request.notes),
            "generated_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception:
        logger.error("Note summarization failed")
        raise HTTPException(status_code=500, detail="Note summarization error")


@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    Generic chat completion

    Args:
        request: Chat request

    Returns:
        Chat completion response
    """
    try:
        _demo_guard()
        response = await llm_service.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return response

    except HTTPException:
        raise
    except Exception:
        logger.error("Chat completion failed")
        raise HTTPException(status_code=500, detail="Chat completion error")


@router.get("/health")
async def health_check():
    """LLM service health check"""
    return {
        "service": "llm",
        "status": "healthy",
        "model": llm_service.model,
        "timestamp": datetime.now().isoformat(),
    }
