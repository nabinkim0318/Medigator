from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.core.claims import PDF_WATERMARK, RESEARCH_PROTOTYPE_DISCLAIMER
from api.main import app
from api.services import pdf as pdf_module

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = (
    "HIPAA compliant",
    "HIPAA-compliant",
    "for clinical use",
    "For clinical use",
    "production-ready",
    "production ready",
    "Automatic ICD-10/CPT coding",
)


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_shared_disclaimer_is_explicit():
    text = RESEARCH_PROTOTYPE_DISCLAIMER.lower()
    assert "research prototype" in text
    assert "not for diagnosis" in text
    assert "clinical use" in text
    assert "hipaa" in text
    assert "does not claim" in text


def test_readme_and_docs_carry_the_boundary():
    readme = _read("README.md")
    api_docs = _read("docs/API.md")
    security = _read("docs/SECURITY.md")
    for text in (readme, api_docs, security):
        assert "Research prototype" in text
        assert "Not for diagnosis" in text
        assert "HIPAA" in text
    for phrase in FORBIDDEN:
        assert phrase not in readme, phrase
        assert phrase not in api_docs, phrase


def test_openapi_description_is_research_prototype():
    description = app.openapi()["info"]["description"]
    assert RESEARCH_PROTOTYPE_DISCLAIMER in description
    for phrase in FORBIDDEN:
        assert phrase not in description, phrase


def test_pdf_never_claims_clinical_use():
    assert pdf_module.DISCLAIMER == PDF_WATERMARK
    assert "For clinical use" not in pdf_module.DISCLAIMER
    assert "clinical use" in pdf_module.DISCLAIMER.lower()
    source = _read("api/services/pdf.py")
    assert "For clinical use" not in source


def test_ui_banner_states_the_boundary():
    banner = _read("src/app/components/ResearchPrototypeBanner.tsx")
    layout = _read("src/app/layout.tsx")
    assert "Research prototype" in banner
    assert "Not for diagnosis" in banner
    assert "HIPAA" in banner
    assert "ResearchPrototypeBanner" in layout
