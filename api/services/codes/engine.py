# api/services/codes/engine.py
from __future__ import annotations
import csv, re, json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

@dataclass
class ICDRule:
    symptom: str
    pattern: re.Pattern
    code: str
    label: str
    weight: float
    excludes: Optional[re.Pattern]
    requires_flag: str
    rationale_key: str

@dataclass
class CPTRule:
    trigger: str
    predicate: str     # safe eval target
    code: str
    label: str
    pos: List[str]
    bundling: List[str]
    payer_note: str
    rationale_key: str
    tags: List[str]

@dataclass
class EMRule:
    context: str
    mdm_problems: str
    mdm_data: str
    mdm_risk: str
    em_cpt: str
    rationale_key: str

def _re_or(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.I) if pattern else re.compile(r"$^")

def load_icd_rules(path: str) -> List[ICDRule]:
    rules = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rules.append(ICDRule(
                symptom=r["symptom"].strip(),
                pattern=_re_or(r["pattern"]),
                code=r["icd_code"].strip(),
                label=r["icd_label"].strip(),
                weight=float(r.get("weight", "0") or 0),
                excludes=_re_or(r["excludes"]) if r.get("excludes") else None,
                requires_flag=(r.get("requires_flag") or "").strip(),
                rationale_key=r["rationale_key"].strip(),
            ))
    return rules

def load_cpt_rules(path: str) -> List[CPTRule]:
    rules = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rules.append(CPTRule(
                trigger=r["trigger"].strip(),
                predicate=(r["predicate"] or "").strip(),
                code=r["cpt"].strip(),
                label=r["label"].strip(),
                pos=[p.strip() for p in (r.get("pos") or "").split("|") if p.strip()],
                bundling=[b.strip() for b in (r.get("bundling") or "").split("|") if b.strip()],
                payer_note=(r.get("payer_note") or "").strip(),
                rationale_key=r["rationale_key"].strip(),
                tags=[t.strip() for t in (r.get("tags") or "").split("|") if t.strip()],
            ))
    return rules

def load_em_rules(path: str) -> List[EMRule]:
    rules = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rules.append(EMRule(
                context=r["context"].strip(),
                mdm_problems=r["mdm_problems"].strip(),
                mdm_data=r["mdm_data"].strip(),
                mdm_risk=r["mdm_risk"].strip(),
                em_cpt=r["em_cpt"].strip(),
                rationale_key=r["rationale_key"].strip(),
            ))
    return rules
