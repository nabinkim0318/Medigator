# api/services/evidence.py
import logging
from typing import List, Dict

# Get logger
logger = logging.getLogger(__name__)

EVIDENCE_DB: Dict[str, List[Dict[str, str]]] = {
    "chest_pain": [
        {
            "title": "ACC/AHA Chest Pain Guideline (2021)",
            "snippet": "For suspected ischemic chest pain, obtain 12-lead ECG promptly and risk-stratify; consider serial troponin testing in appropriate settings.",
            "source": "ACC/AHA 2021 Guideline",
            "link": ""  # placeholder for hackathon
        }
    ],
    "dm_followup": [
        {
            "title": "ADA Standards of Care (2025)",
            "snippet": "Assess HbA1c at least twice yearly in patients meeting goals; quarterly if therapy changed or not at goal. Evaluate lipids as per cardiovascular risk.",
            "source": "ADA 2025 Standards",
            "link": ""
        }
    ]
}

def select_evidence(summary: dict) -> List[Dict[str, str]]:
    logger.info("Selecting evidence based on flags")
    flags = summary.get("flags", {})
    out: List[Dict[str, str]] = []
    
    if flags.get("ischemic_features"): 
        out += EVIDENCE_DB["chest_pain"]
        logger.info("Added chest pain evidence")
    if flags.get("dm_followup"): 
        out += EVIDENCE_DB["dm_followup"]
        logger.info("Added diabetes follow-up evidence")
    
    # limit to 2~3
    result = out[:3]
    logger.info(f"Selected {len(result)} evidence items")
    return result
