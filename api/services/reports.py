# api/services/reports.py
"""
Report service for saving and managing medical reports
"""

from typing import Dict, Any, Optional
from datetime import datetime
from api.core.persistence import write_guard
from api.core.config import settings


def save_report(
    report_data: Dict[str, Any], 
    patient_id: Optional[str] = None,
    encounter_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Save medical report with demo mode guard
    
    Args:
        report_data: Report content and metadata
        patient_id: Patient identifier
        encounter_id: Encounter identifier
        
    Returns:
        Dict with save status and report ID
        
    Raises:
        RuntimeError: In demo mode when write operations are disabled
    """
    write_guard()  # Demo mode protection
    
    # Actual save logic would go here
    # For demo purposes, this raises an exception
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "status": "saved",
        "report_id": report_id,
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "encounter_id": encounter_id
    }


def get_report(report_id: str) -> Dict[str, Any]:
    """
    Retrieve saved medical report
    
    Args:
        report_id: Report identifier
        
    Returns:
        Report data or empty dict if not found
    """
    if settings.DEMO_MODE:
        return {
            "report_id": report_id,
            "status": "demo_mode",
            "message": "Report retrieval disabled in demo mode"
        }
    
    # Actual retrieval logic would go here
    return {}


def list_reports(patient_id: Optional[str] = None) -> list:
    """
    List available reports
    
    Args:
        patient_id: Filter by patient ID
        
    Returns:
        List of report summaries
    """
    if settings.DEMO_MODE:
        return [
            {
                "report_id": "demo_report_001",
                "patient_id": patient_id or "demo_patient",
                "created_at": datetime.now().isoformat(),
                "status": "demo_mode"
            }
        ]
    
    # Actual listing logic would go here
    return []
