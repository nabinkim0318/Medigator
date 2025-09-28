# api/services/llm/normalizer.py
import json
import logging
import re
from pathlib import Path
from typing import Any

# Get logger
logger = logging.getLogger(__name__)


class MedicalNormalizer:
    """Medical term normalization using synonym dictionary"""

    def __init__(self, synonyms_path: str = "rag_index/synonyms.json"):
        self.synonyms_path = Path(synonyms_path)
        self.synonyms_dict = self._load_synonyms()
        logger.info(f"Loaded {len(self.synonyms_dict)} synonym groups")

    def _load_synonyms(self) -> dict[str, dict[str, Any]]:
        """Load synonyms from JSON file"""
        try:
            if not self.synonyms_path.exists():
                logger.warning(f"Synonyms file not found: {self.synonyms_path}")
                return {}

            with open(self.synonyms_path, encoding="utf-8") as f:
                raw = json.load(f)

                # Adapter: flat dict -> normalized schema
                if all(isinstance(v, list) for v in raw.values()):
                    adapted = {}
                    for k, vals in raw.items():
                        adapted[k] = {"terms": list({k, *vals}), "normalized": k}
                    return adapted
                return raw
        except Exception as e:
            logger.error(f"Failed to load synonyms: {e}")
            return {}

    def normalize_text(self, text: str) -> tuple[str, list[str]]:
        """Normalize text and return (normalized_text, applied_rules)"""
        if not text:
            return "", []

        normalized = text.lower().strip()
        applied_rules = []

        # Apply synonym normalization
        for data in self.synonyms_dict.values():
            if isinstance(data, dict) and "terms" in data and "normalized" in data:
                terms = data["terms"]
                normalized_value = data["normalized"]

                for term in terms:
                    if term.lower() in normalized:
                        # Replace with normalized term
                        normalized = normalized.replace(term.lower(), normalized_value)
                        applied_rules.append(f"{term} -> {normalized_value}")

        # Apply regex-based normalization
        normalized, regex_rules = self._apply_regex_normalization(normalized)
        applied_rules.extend(regex_rules)

        if applied_rules:
            logger.debug(f"Applied normalizations: {applied_rules}")

        return normalized, applied_rules

    def _apply_regex_normalization(self, text: str) -> tuple[str, list[str]]:
        """Apply regex-based normalization rules"""
        rules_applied = []

        # Duration normalization
        duration_patterns = [
            (r"\b(\d+)\s*-\s*(\d+)\s*minutes?\b", r"\1-\2min"),
            (r"\bmore than (\d+)\s*minutes?\b", r"\1min+"),
            (r"\b(\d+)\s*minutes?\b", r"\1min"),
            (r"\bseconds?\b", "seconds"),
            (r"\bhours?\b", "hours"),
        ]

        for pattern, replacement in duration_patterns:
            if re.search(pattern, text):
                text = re.sub(pattern, replacement, text)
                rules_applied.append(f"Duration: {pattern} -> {replacement}")

        # Pain severity normalization
        severity_patterns = [
            (r"\b(\d+)\s*-\s*(\d+)\b", r"\1-\2"),
            (r"\bmild\b", "mild"),
            (r"\bmoderate\b", "moderate"),
            (r"\bsevere\b", "severe"),
            (r"\bvery severe\b", "very_severe"),
        ]

        for pattern, replacement in severity_patterns:
            if re.search(pattern, text):
                text = re.sub(pattern, replacement, text)
                rules_applied.append(f"Severity: {pattern} -> {replacement}")

        # Clean up multiple spaces
        text = re.sub(r"\s+", " ", text).strip()

        return text, rules_applied

    def normalize_intake_data(
        self, intake_data: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, list[str]]]:
        """Normalize entire intake data structure"""
        normalized_data = {}
        all_applied_rules = {}

        for key, value in intake_data.items():
            if isinstance(value, str):
                normalized, rules = self.normalize_text(value)
                normalized_data[key] = normalized
                all_applied_rules[key] = rules

            elif isinstance(value, (list, tuple)):
                normalized_items = []
                item_rules = []

                for item in value:
                    if isinstance(item, str):
                        normalized_item, rules = self.normalize_text(item)
                        normalized_items.append(normalized_item)
                        item_rules.extend(rules)
                    else:
                        normalized_items.append(item)

                normalized_data[key] = normalized_items
                all_applied_rules[key] = item_rules

            else:
                # Keep non-string values as-is
                normalized_data[key] = value
                all_applied_rules[key] = []

        logger.info(
            f"Normalized intake data with {sum(len(rules) for rules in all_applied_rules.values())} total rules"
        )
        return normalized_data, all_applied_rules

    def get_normalized_categories(self) -> dict[str, str]:
        """Get mapping of categories to normalized values"""
        return {
            category: data.get("normalized", category)
            for category, data in self.synonyms_dict.items()
            if isinstance(data, dict) and "normalized" in data
        }

    def find_matching_category(self, text: str) -> tuple[str, float]:
        """Find best matching category for given text"""
        text_lower = text.lower()
        best_match = None
        best_score = 0.0

        for category, data in self.synonyms_dict.items():
            if isinstance(data, dict) and "terms" in data:
                terms = data["terms"]

                # Calculate match score
                matches = sum(1 for term in terms if term.lower() in text_lower)
                score = matches / len(terms) if terms else 0.0

                if score > best_score:
                    best_score = score
                    best_match = category

        return best_match or "unknown", best_score


# Global normalizer instance
medical_normalizer = MedicalNormalizer()
