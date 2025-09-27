"""
Pydantic schemas for API requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class SummaryIn(BaseModel):
    """Input schema for medical content summarization"""
    encounterId: str
    patient: Dict[str, Any]  # e.g., {"age": 55, "sex": "M"}
    answers: Dict[str, Any]  # normalized follow-up answers
    vitals: Optional[Dict[str, Any]] = None  # e.g., {"bp_sys": 148, "hr": 96}
    
    class Config:
        json_schema_extra = {
            "example": {
                "encounterId": "enc_12345",
                "patient": {"age": 55, "sex": "M"},
                "answers": {
                    "cc": "chest pain",
                    "onset": "2 days ago",
                    "exertion": True,
                    "relievedByRest": True,
                    "associated": ["diaphoresis", "nausea"],
                    "radiation": "left arm"
                },
                "vitals": {"bp_sys": 148, "hr": 96}
            }
        }


class ROSSection(BaseModel):
    """Review of Systems section"""
    positive: List[str] = []
    negative: List[str] = []


class SummaryOut(BaseModel):
    """Output schema for medical content summarization"""
    hpi: str
    ros: Dict[str, ROSSection]
    pmh: List[str] = []
    meds: List[str] = []
    flags: Dict[str, bool] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "hpi": "55-year-old male patient reports 2 days ago history of chest pain. Pain worsens with exertion and improves with rest. Associated symptoms: diaphoresis, nausea. Radiation: left arm.",
                "ros": {
                    "cardiovascular": {"positive": ["chest pain"], "negative": []},
                    "respiratory": {"positive": [], "negative": []},
                    "constitutional": {"positive": ["diaphoresis"], "negative": []}
                },
                "pmh": ["hypertension", "diabetes"],
                "meds": ["metformin", "lisinopril"],
                "flags": {
                    "ischemic_features": True,
                    "dm_followup": True,
                    "labs_a1c_needed": False
                }
            }
        }


class MedicalAnalysisRequest(BaseModel):
    """Request schema for medical analysis"""
    symptoms: List[str]
    patient_age: int
    medical_history: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["chest pain", "shortness of breath"],
                "patient_age": 65,
                "medical_history": ["hypertension", "diabetes"]
            }
        }


class MedicalAnalysisResponse(BaseModel):
    """Response schema for medical analysis"""
    primary_diagnosis: str
    differential_diagnoses: List[str]
    recommended_tests: List[str]
    risk_level: str
    urgency: str
    treatment_recommendations: List[str]


class TreatmentPlanRequest(BaseModel):
    """Request schema for treatment plan"""
    diagnosis: str
    patient_age: int
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class TreatmentPlanResponse(BaseModel):
    """Response schema for treatment plan"""
    medications: List[dict]
    lifestyle_modifications: List[str]
    follow_up_schedule: str
    warning_signs: List[str]
    emergency_care: str


class HealthResponse(BaseModel):
    """Health check response schema"""
    service: str
    status: str
    timestamp: str
    cache_info: Optional[dict] = None
