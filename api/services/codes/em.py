# api/services/codes/em.py
from typing import Dict, Any, List
from .engine import EMRule

# simple mapping table
_ORDER = {"Low":0, "Moderate":1, "High":2}

def _problems_level(summary: Dict[str, Any], emr: Dict[str, Any]) -> str:
    flags = summary.get("flags", {})
    chronic = len([c for c in emr.get("problems",[]) if c.get("clinicalStatus")=="active"])  # Simplified
    if flags.get("ischemic_features"): 
        return "Moderate"
    if chronic >= 2:
        return "Moderate"
    return "Low"

def _data_level(cpt_suggestions: List[Dict[str,Any]]) -> str:
    codes = {c["code"] for c in cpt_suggestions}
    tests = {"84484","93000","93005","93010","83036"}
    n = len(codes & tests)
    if n >= 2: return "Moderate"
    if n >= 1: return "Limited"
    return "Limited"

def _risk_level(summary: Dict[str, Any]) -> str:
    if summary.get("flags", {}).get("ischemic_features"): 
        return "Moderate"
    return "Low"

def suggest_em(rules: List[EMRule], is_established: bool, summary: Dict[str,Any], emr: Dict[str,Any], cpt_suggestions: List[Dict[str,Any]]) -> Dict[str,Any]:
    problems = _problems_level(summary, emr)
    data = _data_level(cpt_suggestions)
    risk = _risk_level(summary)
    target = ("office_est_" if is_established else "office_new_") + ("mod" if problems=="Moderate" and data!="None" and risk in ("Moderate","High") else "low")
    match = next((r for r in rules if r.context == target), None)
    if not match:
        return {}
    return {
        "code": match.em_cpt,
        "basis": match.rationale_key,
        "mdm": {"problems": problems, "data": data, "risk": risk}
    }
