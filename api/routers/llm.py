"""
LLM API Router
Advanced LLM API endpoints for medical analysis
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import logging

from api.services.llm import llm_service
from api.core.config import settings
from api.core.exceptions import LLMServiceException, MedicalAPIException

# Get logger
logger = logging.getLogger(__name__)


# Pydantic models
class MedicalAnalysisRequest(BaseModel):
    """Medical analysis request model"""
    symptoms: List[str]
    patient_age: int
    medical_history: Optional[List[str]] = None


class MedicalAnalysisResponse(BaseModel):
    """Medical analysis response model"""
    primary_diagnosis: Optional[str] = None
    differential_diagnoses: Optional[List[str]] = None
    recommended_tests: Optional[List[str]] = None
    risk_level: Optional[str] = None
    urgency: Optional[str] = None
    treatment_recommendations: Optional[List[str]] = None


class ReportGenerationRequest(BaseModel):
    """Report generation request model"""
    patient_data: Dict[str, Any]
    symptoms: List[str]
    provider_notes: str
    test_results: Optional[Dict[str, Any]] = None


class TreatmentPlanRequest(BaseModel):
    """Treatment plan request model"""
    diagnosis: str
    patient_age: int
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class EntityExtractionRequest(BaseModel):
    """Entity extraction request model"""
    text: str


class EntityExtractionResponse(BaseModel):
    """Entity extraction response model"""
    symptoms: List[str]
    medications: List[str]
    conditions: List[str]
    procedures: List[str]


class NoteSummarizationRequest(BaseModel):
    """Note summarization request model"""
    notes: List[str]


class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[Dict[str, str]]
    model: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 1000


# Router creation
router = APIRouter()

# Demo mode guard for advanced LLM features
def _demo_guard():
    if settings.DEMO_MODE:
        raise HTTPException(
            status_code=503, 
            detail="Advanced LLM features disabled in demo mode. Use /summary, /evidence, or /codes endpoints instead."
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
    logger.info(f"Medical analysis requested for age {request.patient_age} with {len(request.symptoms)} symptoms")
    try:
        analysis = await llm_service.medical_analysis(
            symptoms=request.symptoms,
            patient_age=request.patient_age,
            medical_history=request.medical_history
        )
        
        return MedicalAnalysisResponse(
            primary_diagnosis=analysis.get('primary_diagnosis'),
            differential_diagnoses=analysis.get('differential_diagnoses', []),
            recommended_tests=analysis.get('recommended_tests', []),
            risk_level=analysis.get('risk_level'),
            urgency=analysis.get('urgency'),
            treatment_recommendations=analysis.get('treatment_recommendations', [])
        )
        
    except Exception as e:
        logger.error(f"Medical analysis failed: {str(e)}")
        raise LLMServiceException(
            message="Medical analysis failed",
            details={"error": str(e), "symptoms_count": len(request.symptoms)}
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
        report = await llm_service.generate_medical_report(
            patient_data=request.patient_data,
            symptoms=request.symptoms,
            provider_notes=request.provider_notes,
            test_results=request.test_results
        )
        
        return {
            "report": report,
            "generated_at": datetime.now().isoformat(),
            "patient_name": request.patient_data.get('name', 'N/A')
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")


@router.post("/treatment-plan")
async def suggest_treatment_plan(request: TreatmentPlanRequest):
    """
    Suggest treatment plan based on diagnosis
    
    Args:
        request: Treatment plan request
        
    Returns:
        Treatment plan
    """
    try:
        plan = await llm_service.suggest_treatment_plan(
            diagnosis=request.diagnosis,
            patient_age=request.patient_age,
            medical_history=request.medical_history,
            allergies=request.allergies
        )
        
        return plan
        
    except Exception as e:
        logger.error(f"Treatment plan generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Treatment plan error: {str(e)}")


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
        entities = await llm_service.extract_medical_entities(request.text)
        
        return EntityExtractionResponse(
            symptoms=entities.get('symptoms', []),
            medications=entities.get('medications', []),
            procedures=entities.get('procedures', []),
            diagnoses=entities.get('diagnoses', []),
            body_parts=entities.get('body_parts', []),
            vital_signs=entities.get('vital_signs', [])
        )
        
    except Exception as e:
        logger.error(f"Entity extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Entity extraction error: {str(e)}")


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
        summary = await llm_service.summarize_medical_notes(request.notes)
        
        return {
            "summary": summary,
            "original_notes_count": len(request.notes),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Note summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Note summarization error: {str(e)}")


class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000

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
        response = await llm_service.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat completion error: {str(e)}")


@router.get("/health")
async def health_check():
    """LLM service health check"""
    return {
        "service": "llm",
        "status": "healthy",
        "model": llm_service.model,
        "timestamp": datetime.now().isoformat()
    }
