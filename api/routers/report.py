"""
Report API router
Medical report generation and management API endpoints
"""

import logging
import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.core.exceptions import MedicalAPIException
from api.core.persistence import write_guard
from api.services.llm import llm_service
from api.services.pdf import pdf_service
from api.services.rules import rules_service

# Get logger
logger = logging.getLogger(__name__)


# Pydantic model definition
class PatientData(BaseModel):
    """Patient data model"""

    name: str
    age: int
    gender: str
    birth_date: str | None = None
    patient_id: str | None = None
    medical_history: list[str] | None = None


class ProviderData(BaseModel):
    """Provider data model"""

    name: str
    specialty: str
    license_number: str
    provider_id: str | None = None


class ReportRequest(BaseModel):
    """Report creation request model"""

    patient: PatientData
    provider: ProviderData
    symptoms: list[str]
    provider_notes: str
    vital_signs: dict[str, Any] | None = None


class ReportResponse(BaseModel):
    """Report response model"""

    report_id: str
    status: str
    content: str
    diagnosis: str | None = None
    treatment_plan: str | None = None
    created_at: str


class AnalysisRequest(BaseModel):
    """Symptom analysis request model"""

    symptoms: list[str]
    patient_age: int
    medical_history: list[str] | None = None


class AnalysisResponse(BaseModel):
    """Symptom analysis response model"""

    primary_diagnosis: str | None = None
    icd_code: str | None = None
    risk_level: str | None = None
    recommended_tests: str | None = None


# Router creation
router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate medical report.

    Args:
        request: Report creation request

    Returns:
        Created report information
    """
    logger.info(f"Generating report for patient: {request.patient.name}")
    try:
        # Use LLM to generate report
        report_content = await llm_service.generate_report(
            patient_data=request.patient.dict(),
            analysis_data={"symptoms": request.symptoms, "provider_notes": request.provider_notes},
        )

        # Symptom analysis
        analysis = await llm_service.analyze_symptoms(
            symptoms=request.symptoms,
            patient_age=request.patient.age,
            medical_history=[],
        )

        # Treatment suggestion
        treatment = await llm_service.suggest_treatment(
            diagnosis=analysis.get("primary_diagnosis", ""),
            patient_data={
                "age": request.patient.age,
                "medical_history": request.patient.medical_history or [],
            },
        )

        # Report ID creation
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        response = ReportResponse(
            report_id=report_id,
            status="completed",
            content=report_content,
            diagnosis=analysis.get("primary_diagnosis"),
            treatment_plan=treatment.get("medications", ""),
            created_at=datetime.now().isoformat(),
        )
        logger.info(f"Report generated successfully: {report_id}")
        return response

    except Exception as e:
        logger.error(f"Report generation failed: {e!s}")
        raise MedicalAPIException(
            message="Report generation failed",
            status_code=500,
            details={"error": str(e), "patient_name": request.patient.name},
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_symptoms(request: AnalysisRequest):
    """
    Analyze symptoms and suggest diagnosis.

    Args:
        request: Symptom analysis request

    Returns:
        Analysis result
    """
    try:
        # Use LLM to analyze symptoms
        analysis = await llm_service.analyze_symptoms(
            symptoms=request.symptoms,
            patient_age=request.patient_age,
            medical_history=request.medical_history or [],
        )

        return AnalysisResponse(
            primary_diagnosis=analysis.get("primary_diagnosis"),
            icd_code=analysis.get("icd_code"),
            risk_level=analysis.get("risk_level"),
            recommended_tests=analysis.get("recommended_tests"),
        )

    except Exception as e:
        logger.error(f"Symptom analysis failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Symptom analysis error: {e!s}")


@router.get("/symptoms/{symptom}/icd")
async def get_symptom_icd_mapping(symptom: str):
    """
    Get ICD code mapping for symptom.

    Args:
        symptom: Symptom name

    Returns:
        ICD code mapping list
    """
    try:
        mappings = await rules_service.get_symptom_icd_mapping(symptom)
        return {"symptom": symptom, "mappings": mappings}

    except Exception as e:
        logger.error(f"ICD mapping lookup failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"ICD mapping lookup error: {e!s}")


@router.get("/conditions/{condition}/cpt")
async def get_condition_cpt_codes(condition: str):
    """
    Get CPT codes for condition.

    Args:
        condition: Condition name

    Returns:
        CPT code list
    """
    try:
        cpt_codes = await rules_service.get_cpt_codes_for_condition(condition)
        return {"condition": condition, "cpt_codes": cpt_codes}

    except Exception as e:
        logger.error(f"CPT code lookup failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"CPT code lookup error: {e!s}")


@router.post("/pdf")
async def generate_pdf_report(request: ReportRequest):
    """
    Generate report PDF.

    Args:
        request: Report creation request

    Returns:
        Created PDF file
    """
    write_guard()  # if DEMO_MODE, RuntimeError
    try:
        # Prepare report data
        report_data = {
            "chief_complaint": ", ".join(request.symptoms),
            "history": request.provider_notes,
            "physical_exam": "Normal",
            "diagnosis": "Diagnosing",
            "treatment": "Treatment planning",
        }

        # Generate PDF
        pdf_path = await pdf_service.generate_report_pdf(
            report_data=report_data,
            patient_data=request.patient.dict(),
            provider_data=request.provider.dict(),
        )

        # Check file existence
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF generation failed")

        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type="application/pdf",
        )

    except Exception as e:
        logger.error(f"PDF generation failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {e!s}")


@router.get("/demo/pdf")
async def generate_demo_pdf():
    """
    Generate demo PDF.

    Returns:
        Demo PDF file
    """
    write_guard()  # RuntimeError if DEMO_MODE
    try:
        pdf_path = await pdf_service.generate_demo_pdf()

        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Demo PDF generation failed")

        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type="application/pdf",
        )

    except Exception as e:
        logger.error(f"Demo PDF generation failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Demo PDF generation error: {e!s}")


@router.get("/rules")
async def get_active_rules():
    """
    Get active rules.

    Returns:
        Active rules list
    """
    try:
        rules = await rules_service.get_active_rules()
        return {"rules": rules}

    except Exception as e:
        logger.error(f"Rule lookup failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Rule lookup error: {e!s}")


@router.post("/rules/evaluate")
async def evaluate_rules(
    patient_data: PatientData = Body(...),
    symptoms: list[str] = Body(...),
    vital_signs: dict[str, Any] | None = Body(default=None),
):
    """
    Evaluate rules for patient data.

    Args:
        patient_data: Patient data
        symptoms: Symptoms list
        vital_signs: Vital signs

    Returns:
        Applied rules list
    """
    try:
        applied_rules = await rules_service.evaluate_rules(
            patient_data=patient_data.dict(),
            symptoms=symptoms,
            vital_signs=vital_signs or {},
        )

        return {"applied_rules": applied_rules}

    except Exception as e:
        logger.error(f"Rule evaluation failed: {e!s}")
        raise HTTPException(status_code=500, detail=f"Rule evaluation error: {e!s}")


@router.get("/health")
async def health_check():
    """Report service health check"""
    return {
        "service": "report",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }
