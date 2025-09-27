# api/services/llm/rule_engine.py
import json
import logging
from typing import Any, Dict, List, Tuple

# Get logger
logger = logging.getLogger(__name__)


class ClinicalFlagRule:
    """Individual clinical flag rule with justification tracking"""

    def __init__(self, name: str, condition_func, description: str):
        self.name = name
        self.condition_func = condition_func
        self.description = description
        self.justification: list[str] = []

    def evaluate(
        self, intake_data: dict[str, Any], summary_data: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Evaluate rule and return (result, justifications)"""
        self.justification = []
        try:
            result = self.condition_func(intake_data, summary_data, self.justification)
            return result, self.justification.copy()
        except Exception as e:
            logger.error(f"Rule {self.name} evaluation failed: {e}")
            return False, [f"Rule evaluation error: {e}"]


class ClinicalRuleEngine:
    """Clinical flag calculation engine with rule justification logging"""

    def __init__(self):
        self.rules = self._initialize_rules()
        logger.info(f"Initialized clinical rule engine with {len(self.rules)} rules")

    def _initialize_rules(self) -> dict[str, ClinicalFlagRule]:
        """Initialize clinical flag rules"""
        return {
            "ischemic_features": ClinicalFlagRule(
                name="ischemic_features",
                condition_func=self._ischemic_features_rule,
                description="Detects signs of myocardial ischemia",
            ),
            "dm_followup": ClinicalFlagRule(
                name="dm_followup",
                condition_func=self._dm_followup_rule,
                description="Identifies diabetes mellitus follow-up needs",
            ),
            "labs_a1c_needed": ClinicalFlagRule(
                name="labs_a1c_needed",
                condition_func=self._labs_a1c_needed_rule,
                description="Determines if HbA1c lab is needed",
            ),
        }

    def _ischemic_features_rule(
        self, intake: dict[str, Any], summary: dict[str, Any], justification: list[str]
    ) -> bool:
        """Rule for ischemic features detection"""
        try:
            # Extract relevant data from intake
            q4_worse = intake.get("Q4_Worse_with", [])
            q5_better = intake.get("Q5_Better_with", [])
            q2_location = intake.get("Q2_Where_is_the_pain", [])
            q6_symptoms = intake.get("Q6_Associated_symptoms", [])

            # Rule 1: Exertional chest pain relieved by rest
            exertion_worse = any(
                "physical activity" in str(item).lower() or "exercise" in str(item).lower()
                for item in q4_worse
            )
            rest_better = any(
                "rest" in str(item).lower() or "stopping activity" in str(item).lower()
                for item in q5_better
            )

            if exertion_worse and rest_better:
                justification.append("Exertional chest pain relieved by rest")

            # Rule 2: Left arm radiation
            left_arm_radiation = any("left arm" in str(item).lower() for item in q2_location)
            if left_arm_radiation:
                justification.append("Pain radiates to left arm")

            # Rule 3: Diaphoresis/sweating
            diaphoresis = any(
                "sweating" in str(item).lower() or "diaphoresis" in str(item).lower()
                for item in q6_symptoms
            )
            if diaphoresis:
                justification.append("Associated diaphoresis/sweating")

            # Rule 4: Nausea/vomiting with chest pain
            nausea = any(
                "nausea" in str(item).lower() or "vomiting" in str(item).lower()
                for item in q6_symptoms
            )
            if nausea:
                justification.append("Associated nausea/vomiting")

            # Rule 5: Pressure/squeezing quality
            q3_character = intake.get("Q3_Pain_character", [])
            pressure_quality = any(
                "pressure" in str(item).lower() or "squeezing" in str(item).lower()
                for item in q3_character
            )
            if pressure_quality:
                justification.append("Pressure/squeezing pain quality")

            # Combine conditions (any 2 or more = positive)
            conditions_met = sum(
                [
                    exertion_worse and rest_better,
                    left_arm_radiation,
                    diaphoresis,
                    nausea,
                    pressure_quality,
                ]
            )

            result = conditions_met >= 2
            if result:
                justification.append(f"Total conditions met: {conditions_met}/5")

            return result

        except Exception as e:
            logger.error(f"Ischemic features rule error: {e}")
            justification.append(f"Rule error: {e}")
            return False

    def _dm_followup_rule(
        self, intake: dict[str, Any], summary: dict[str, Any], justification: list[str]
    ) -> bool:
        """Rule for diabetes mellitus follow-up detection"""
        try:
            # Check for diabetes-related terms in any field
            diabetes_terms = [
                "diabetes",
                "dm",
                "diabetic",
                "glucose",
                "sugar",
                "insulin",
                "a1c",
                "hba1c",
            ]

            # Search through all intake fields
            for key, value in intake.items():
                if isinstance(value, (list, tuple)):
                    value_str = " ".join(str(item) for item in value).lower()
                else:
                    value_str = str(value).lower()

                for term in diabetes_terms:
                    if term in value_str:
                        justification.append(f"Diabetes term '{term}' found in {key}")
                        return True

            return False

        except Exception as e:
            logger.error(f"DM follow-up rule error: {e}")
            justification.append(f"Rule error: {e}")
            return False

    def _labs_a1c_needed_rule(
        self, intake: dict[str, Any], summary: dict[str, Any], justification: list[str]
    ) -> bool:
        """Rule for HbA1c lab necessity"""
        try:
            # First check if DM follow-up is needed
            dm_needed = self._dm_followup_rule(intake, summary, justification)

            if not dm_needed:
                justification.append("DM follow-up not needed")
                return False

            # Check for A1c-related indicators
            a1c_terms = ["a1c", "hba1c", "hemoglobin a1c", "glycated hemoglobin"]
            a1c_due_terms = ["due", "overdue", "needed", "check", "test", "monitor"]

            for key, value in intake.items():
                if isinstance(value, (list, tuple)):
                    value_str = " ".join(str(item) for item in value).lower()
                else:
                    value_str = str(value).lower()

                # Check for A1c mention
                for term in a1c_terms:
                    if term in value_str:
                        justification.append(f"A1c term '{term}' found in {key}")
                        return True

                # Check for "due" indicators
                for term in a1c_due_terms:
                    if term in value_str and any(a1c_term in value_str for a1c_term in a1c_terms):
                        justification.append(f"A1c monitoring indicator '{term}' found")
                        return True

            # Default: if DM follow-up needed, A1c may be needed
            justification.append("DM follow-up needed - A1c may be indicated")
            return True

        except Exception as e:
            logger.error(f"A1c labs rule error: {e}")
            justification.append(f"Rule error: {e}")
            return False

    def calculate_flags(
        self, intake_data: dict[str, Any], summary_data: dict[str, Any]
    ) -> tuple[dict[str, bool], dict[str, list[str]]]:
        """Calculate all clinical flags with justifications"""
        flags = {}
        justifications = {}

        logger.info("Starting clinical flag calculation")

        for rule_name, rule in self.rules.items():
            try:
                result, justification = rule.evaluate(intake_data, summary_data)
                flags[rule_name] = result
                justifications[rule_name] = justification

                logger.info(f"Flag {rule_name}: {result} - {', '.join(justification)}")

            except Exception as e:
                logger.error(f"Flag calculation failed for {rule_name}: {e}")
                flags[rule_name] = False
                justifications[rule_name] = [f"Calculation error: {e}"]

        logger.info(f"Flag calculation completed: {flags}")
        return flags, justifications

    def get_rule_descriptions(self) -> dict[str, str]:
        """Get descriptions of all rules"""
        return {name: rule.description for name, rule in self.rules.items()}


# Global rule engine instance
clinical_rule_engine = ClinicalRuleEngine()
