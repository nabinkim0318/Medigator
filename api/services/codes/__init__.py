# api/services/codes/__init__.py
import logging
from pathlib import Path
from typing import Any

from .cpt import suggest_cpt
from .engine import load_cpt_rules, load_icd_rules
from .icd import suggest_icd

# Get logger
logger = logging.getLogger(__name__)

# Get the project root directory (assuming this file is in api/services/codes/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RULES_DIR = PROJECT_ROOT / "data" / "rules"
_icd = load_icd_rules(str(RULES_DIR / "symptom_icd.csv"))
_cpt = load_cpt_rules(str(RULES_DIR / "trigger_cpt.csv"))

logger.info(f"Loaded {len(_icd)} ICD rules, {len(_cpt)} CPT rules")


def generate_codes(
    summary: dict[str, Any],
    intake: dict[str, Any],
    emr: dict[str, Any],
) -> dict[str, Any]:
    logger.info("Generating medical codes")
    env = {"flags": summary.get("flags", {}), "intake": intake, "emr": emr}

    try:
        icd = suggest_icd(_icd, summary, intake, emr, k=3)
        logger.info(f"Generated {len(icd)} ICD codes")

        cpt = suggest_cpt(_cpt, env)
        logger.info(f"Generated {len(cpt)} CPT codes")

        result = {"icd": icd, "cpt": cpt, "meta": {"version": "1.0"}}
        logger.info("Code generation completed successfully")
        return result

    except Exception as e:
        logger.error(f"Code generation failed: {e!s}")
        raise
