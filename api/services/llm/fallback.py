# api/services/llm/fallback.py
from typing import Mapping
from api.core.schemas import SummaryIn, SummaryOut

def templated(body: SummaryIn) -> dict:
    """
    Fallback template for medical content summarization
    Returns dict matching the new schema structure
    """
    if isinstance(body, SummaryIn):
        answers = body.answers or {}
        patient = body.patient or {}
    elif isinstance(body, Mapping):
        answers = body.get("answers", {}) or {}
        patient = body.get("patient", {}) or {}
    else:
        answers = getattr(body, 'answers', {})
        patient = getattr(body, 'patient', {})
    # Extract information from input data
    
    # Generate HPI
    hpi_parts = []
    if patient.get("age"):
        hpi_parts.append(f"{patient['age']}-year-old")
    if patient.get("sex") in ("M", "F"):
        gender = "male" if patient["sex"] == "M" else "female"
        hpi_parts.append(gender)
    
    if hpi_parts:
        hpi = " ".join(hpi_parts) + " patient"
    else:
        hpi = "Patient"
    
    if answers.get("cc"):
        hpi += f" reports {answers.get('onset', '')} history of {answers['cc']}."
    
    if answers.get("exertion") and answers.get("relievedByRest"):
        hpi += " Pain worsens with exertion and improves with rest."
    
    if answers.get("associated"):
        hpi += f" Associated symptoms: {', '.join(answers['associated'])}."
    
    if answers.get("radiation"):
        hpi += f" Radiation: {answers['radiation']}."
    
    # Generate ROS
    ros = {
        "cardiovascular": {
            "positive": ["chest pain"] if str(answers.get("cc", "")).lower().startswith("chest") else [],
            "negative": []
        },
        "respiratory": {
            "positive": ["dyspnea"] if "dyspnea" in (answers.get("associated") or []) else [],
            "negative": []
        },
        "constitutional": {
            "positive": ["diaphoresis"] if "diaphoresis" in (answers.get("associated") or []) else [],
            "negative": []
        }
    }
    
    dm_followup = "diabetes" in str(answers.get("cc", "")).lower() or "dm" in str(answers.get("cc", "")).lower()
    labs_a1c_needed = bool(dm_followup and (
        answers.get("a1c_due") is True or
        (answers.get("a1c_recent") is False if answers.get("a1c_recent") is not None else False)
    ))

    # PMH and Meds
    pmh = answers.get("pmh", [])
    meds = answers.get("meds", [])
    
    # Calculate Flags
    flags = {
        "ischemic_features": bool(
            (answers.get("exertion") and answers.get("relievedByRest")) or
            ("left arm" in (answers.get("radiation") or "")) or
            ("diaphoresis" in (answers.get("associated") or []))
        ),
        "dm_followup": dm_followup,
        "labs_a1c_needed": labs_a1c_needed
    }
    
    return {
        "hpi": hpi,
        "ros": ros,
        "pmh": pmh,
        "meds": meds,
        "flags": flags
    }
