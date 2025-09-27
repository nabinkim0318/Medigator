"""
Pydantic schemas for API requests and responses
"""

from typing import Any

from pydantic import BaseModel


class SummaryIn(BaseModel):
    """Input schema for medical content summarization"""

    encounterId: str
    patient: dict[str, Any]  # e.g., {"age": 55, "sex": "M"}
    answers: dict[str, Any]  # normalized follow-up answers
    vitals: dict[str, Any] | None = None  # e.g., {"bp_sys": 148, "hr": 96}

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
                    "radiation": "left arm",
                },
                "vitals": {"bp_sys": 148, "hr": 96},
            },
        }


class ROSSection(BaseModel):
    """Review of Systems section"""

    positive: list[str] = []
    negative: list[str] = []


class SummaryOut(BaseModel):
    """Output schema for medical content summarization"""

    hpi: str
    ros: dict[str, ROSSection]
    pmh: list[str] = []
    meds: list[str] = []
    flags: dict[str, bool] = {}

    class Config:
        json_schema_extra = {
            "example": {
                "hpi": "55-year-old male patient reports 2 days ago history of chest pain. Pain worsens with exertion and improves with rest. Associated symptoms: diaphoresis, nausea. Radiation: left arm.",
                "ros": {
                    "cardiovascular": {"positive": ["chest pain"], "negative": []},
                    "respiratory": {"positive": [], "negative": []},
                    "constitutional": {"positive": ["diaphoresis"], "negative": []},
                },
                "pmh": ["hypertension", "diabetes"],
                "meds": ["metformin", "lisinopril"],
                "flags": {
                    "ischemic_features": True,
                    "dm_followup": True,
                    "labs_a1c_needed": False,
                },
            },
        }


class MedicalAnalysisRequest(BaseModel):
    """Request schema for medical analysis"""

    symptoms: list[str]
    patient_age: int
    medical_history: list[str] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["chest pain", "shortness of breath"],
                "patient_age": 65,
                "medical_history": ["hypertension", "diabetes"],
            },
        }


class MedicalAnalysisResponse(BaseModel):
    """Response schema for medical analysis"""

    primary_diagnosis: str
    differential_diagnoses: list[str]
    recommended_tests: list[str]
    risk_level: str
    urgency: str
    treatment_recommendations: list[str]


class TreatmentPlanRequest(BaseModel):
    """Request schema for treatment plan"""

    diagnosis: str
    patient_age: int
    medical_history: list[str] | None = None
    allergies: list[str] | None = None


class TreatmentPlanResponse(BaseModel):
    """Response schema for treatment plan"""

    medications: list[dict]
    lifestyle_modifications: list[str]
    follow_up_schedule: str
    warning_signs: list[str]
    emergency_care: str


class HealthResponse(BaseModel):
    """Health check response schema"""

    service: str
    status: str
    timestamp: str
    cache_info: dict | None = None
