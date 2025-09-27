"""
Report API router
Medical report generation and management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import os

from api.services.llm import llm_service
from api.services.pdf import pdf_service
from api.services.rules import rules_service


# Pydantic model definition
class PatientData(BaseModel):
    """Patient data model"""
    name: str
    age: int
    gender: str
    birth_date: Optional[str] = None
    patient_id: Optional[str] = None
    medical_history: Optional[List[str]] = None


class ProviderData(BaseModel):
    """Provider data model"""
    name: str
    specialty: str
    license_number: str
    provider_id: Optional[str] = None


class ReportRequest(BaseModel):
    """Report creation request model"""
    patient: PatientData
    provider: ProviderData
    symptoms: List[str]
    provider_notes: str
    vital_signs: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Report response model"""
    report_id: str
    status: str
    content: str
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    created_at: str


class AnalysisRequest(BaseModel):
    """Symptom analysis request model"""
    symptoms: List[str]
    patient_age: int
    medical_history: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    """Symptom analysis response model"""
    primary_diagnosis: Optional[str] = None
    icd_code: Optional[str] = None
    risk_level: Optional[str] = None
    recommended_tests: Optional[str] = None


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
    try:
        # Use LLM to generate report
        report_content = await llm_service.generate_report(
            patient_data=request.patient.dict(),
            symptoms=request.symptoms,
            provider_notes=request.provider_notes
        )
        
        # Symptom analysis
        analysis = await llm_service.analyze_symptoms(request.symptoms)
        
        # Treatment suggestion
        treatment = await llm_service.suggest_treatment(
            diagnosis=analysis.get('primary_diagnosis', ''),
            patient_age=request.patient.age,
            medical_history=request.patient.medical_history or []
        )
        
        # Report ID creation
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ReportResponse(
            report_id=report_id,
            status="completed",
            content=report_content,
            diagnosis=analysis.get('primary_diagnosis'),
            treatment_plan=treatment.get('medications', ''),
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report creation error: {str(e)}")


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
        analysis = await llm_service.analyze_symptoms(request.symptoms)
        
        return AnalysisResponse(
            primary_diagnosis=analysis.get('primary_diagnosis'),
            icd_code=analysis.get('icd_code'),
            risk_level=analysis.get('risk_level'),
            recommended_tests=analysis.get('recommended_tests')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Symptom analysis error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"ICD mapping lookup error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"CPT code lookup error: {str(e)}")


@router.get("/cpt/{cpt_code}/fee")
async def get_cpt_fee(cpt_code: str):
    """
    Get fee information for CPT code.
    
    Args:
        cpt_code: CPT code
        
    Returns:
        Fee information
    """
    try:
        fee_info = await rules_service.get_fee_for_cpt(cpt_code)
        if fee_info:
            return fee_info
        else:
            raise HTTPException(status_code=404, detail="Fee information not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fee lookup error: {str(e)}")


@router.post("/pdf")
async def generate_pdf_report(request: ReportRequest):
    """
    Generate report PDF.
    
    Args:
        request: Report creation request
        
    Returns:
        Created PDF file
    """
    try:
        # Prepare report data
        report_data = {
            'chief_complaint': ', '.join(request.symptoms),
            'history': request.provider_notes,
            'physical_exam': 'Normal',
            'diagnosis': 'Diagnosing',
            'treatment': 'Treatment planning'
        }
        
        # Generate PDF
        pdf_path = await pdf_service.generate_report_pdf(
            report_data=report_data,
            patient_data=request.patient.dict(),
            provider_data=request.provider.dict()
        )
        
        # Check file existence
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type='application/pdf'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


@router.get("/demo/pdf")
async def generate_demo_pdf():
    """
    Generate demo PDF.
    
    Returns:
        Demo PDF file
    """
    try:
        pdf_path = await pdf_service.generate_demo_pdf()
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Demo PDF generation failed")
        
        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type='application/pdf'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo PDF generation error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Rule lookup error: {str(e)}")


@router.post("/rules/evaluate")
async def evaluate_rules(
    patient_data: PatientData,
    symptoms: List[str],
    vital_signs: Optional[Dict[str, Any]] = None
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
            vital_signs=vital_signs or {}
        )
        
        return {"applied_rules": applied_rules}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rule evaluation error: {str(e)}")


@router.get("/health")
async def health_check():
    """Report service health check"""
    return {
        "service": "report",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
