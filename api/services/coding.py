# api/services/coding.py
from typing import List, Dict

ICD_RULES = {
    "chest_pain": "R07.9",
    "t2dm_followup": "E11.9",
}

CPT_RULES = {
    "ecg_if_ischemic": "93000",
    "troponin": "84484",
    "a1c": "83036",
    "lipid": "80061",
    "bmp": "80048",
    "cxr": "71046",
}

EM_RULES = {
    "low": "99213",
    "moderate": "99214",
    "new_low": "99203",
    "new_mod": "99204",
}

MOCK_FEES: Dict[str, int] = {
    "93000": 35,
    "84484": 22,
    "83036": 14,
    "80061": 19,
    "80048": 12,
    "71046": 60,
    "99213": 95,
    "99214": 145,
    "99203": 140,
    "99204": 210,
}

# ---- Mapping helpers ----
def map_icd(flags, text_hint: str = "") -> List[str]:
    out = []
    t = text_hint.lower()
    if flags.ischemic_features or ("chest" in t and "pain" in t):
        out.append(ICD_RULES["chest_pain"])
    if flags.dm_followup:
        out.append(ICD_RULES["t2dm_followup"])
    return sorted(set(out)) or ["Z13.9"]  # fallback

def map_cpt(flags, ros, text_hint: str = "") -> List[str]:
    out = []
    if flags.ischemic_features:
        out += [CPT_RULES["ecg_if_ischemic"], CPT_RULES["troponin"]]
    if len(ros.respiratory.positive) >= 2 and "chest" in text_hint.lower():
        out.append(CPT_RULES["cxr"])
    if flags.dm_followup:
        out.append(CPT_RULES["a1c"])
    out += [CPT_RULES["lipid"], CPT_RULES["bmp"]]
    return sorted(set(out)) or ["99999"]

def map_em(flags) -> str:
    return EM_RULES["moderate"] if flags.ischemic_features else EM_RULES["low"]

def estimate_costs(cpts: List[str]) -> Dict:
    items, lo, hi = [], 0, 0
    for c in cpts:
        fee = MOCK_FEES.get(c, {"min": 50, "max": 150})
        if isinstance(fee, dict):  # structured fee
            items.append({"cpt": c, **fee})
            lo += fee["min"]; hi += fee["max"]
        else:  # simple int fallback
            items.append({"cpt": c, "min": fee, "max": fee})
            lo += fee; hi += fee
    return {"range_min": lo, "range_max": hi, "items": items}
