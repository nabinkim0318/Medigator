# api/services/codes/__init__.py
import logging
from pathlib import Path
from typing import Any

from .cpt import suggest_cpt
from .em import suggest_em
from .engine import load_cpt_rules, load_em_rules, load_icd_rules
from .icd import suggest_icd

# Get logger
logger = logging.getLogger(__name__)

RULES_DIR = Path("data/rules")
_icd = load_icd_rules(str(RULES_DIR / "symptom_icd.csv"))
_cpt = load_cpt_rules(str(RULES_DIR / "trigger_cpt.csv"))
_em = load_em_rules(str(RULES_DIR / "em_rules.csv"))

logger.info(f"Loaded {len(_icd)} ICD rules, {len(_cpt)} CPT rules, {len(_em)} EM rules")


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

        em = suggest_em(
            _em,
            is_established=bool(emr.get("established", True)),
            summary=summary,
            emr=emr,
            cpt_suggestions=cpt,
        )
        logger.info(f"Generated {len(em)} EM codes")

        result = {"icd": icd, "cpt": cpt, "em": em, "meta": {"version": "1.0"}}
        logger.info("Code generation completed successfully")
        return result

    except Exception as e:
        logger.error(f"Code generation failed: {e!s}")
        raise
