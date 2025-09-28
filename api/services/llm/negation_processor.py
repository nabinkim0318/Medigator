# api/services/llm/negation_processor.py
import logging
import re
from typing import Any, Dict, List, Tuple

# Get logger
logger = logging.getLogger(__name__)


class NegationProcessor:
    """Process negation patterns in medical intake data"""

    # Clinical term canonicalization mapping
    CANON = {
        "spreads to left arm": "radiation to left arm",
        "shortness of breath": "dyspnea",
        "sweating": "diaphoresis",
        "nausea or vomiting": "nausea/vomiting",
        "fast or irregular heartbeat": "palpitations",
        "chest pain": "chest pain",
        "chest pressure": "chest pressure",
        "chest tightness": "chest tightness",
        "chest discomfort": "chest discomfort",
        "weight loss": "weight loss",
        "weight gain": "weight gain",
        "fever": "fever",
        "chills": "chills",
        "fatigue": "fatigue",
        "weakness": "weakness",
        "cough": "cough",
        "wheezing": "wheezing",
        "difficulty breathing": "dyspnea",
        "edema": "edema",
        "swelling": "edema",
    }

    def __init__(self):
        # Negation patterns
        self.negation_patterns = [
            r"\bno\b",
            r"\bnone\b",
            r"\bnothing\b",
            r"\bnot\b",
            r"\bdenies\b",
            r"\bdeny\b",
            r"\bwithout\b",
            r"\babsent\b",
            r"\bnegative\b",
            r"\bno, none of these\b",
            r"\bno, none\b",
            r"\bnone of the above\b",
            r"\bnone of these\b",
            r"\bnot applicable\b",
            r"\bnot present\b",
            r"\bnot experiencing\b",
            r"\bnot having\b",
        ]

        # Compile patterns for efficiency
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.negation_patterns
        ]

        # Contextual negation patterns (negation + symptom)
        self.contextual_patterns = [
            (r"\bno\s+([a-z\s]+)\b", "no_{}"),
            (r"\bnot\s+([a-z\s]+)\b", "not_{}"),
            (r"\bdenies\s+([a-z\s]+)\b", "denies_{}"),
            (r"\bwithout\s+([a-z\s]+)\b", "without_{}"),
        ]

        self.compiled_contextual = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.contextual_patterns
        ]

        logger.info(f"Initialized negation processor with {len(self.compiled_patterns)} patterns")

    def contains_negation(self, text: str) -> bool:
        """Check if text contains negation patterns"""
        if not text:
            return False

        text_lower = text.lower()
        return any(pattern.search(text_lower) for pattern in self.compiled_patterns)

    def extract_negated_items(self, text: str) -> list[str]:
        """Extract items that are being negated"""
        if not text:
            return []

        negated_items = []
        text_lower = text.lower()

        # Check contextual patterns
        for pattern, replacement in self.compiled_contextual:
            matches = pattern.findall(text_lower)
            for match in matches:
                negated_item = replacement.format(match.strip())
                negated_items.append(negated_item)

        # Check for "no, none of these" patterns
        if re.search(r"\bno,?\s*none\s*of\s*(?:the\s*)?(?:these|above)\b", text_lower):
            negated_items.append("all_symptoms_negative")

        return negated_items

    def process_negation_in_list(self, items: list[str]) -> tuple[list[str], list[str], list[str]]:
        """Process negation in a list of items

        Returns:
            - positive_items: Items that are not negated
            - negative_items: Items that are explicitly negated
            - negated_all: Whether "all" negation was found
        """
        if not items:
            return [], [], []

        positive_items = []
        negative_items = []
        negated_all = False

        for item in items:
            item_str = str(item).strip()

            if self.contains_negation(item_str):
                # Extract what is being negated
                negated_terms = self.extract_negated_items(item_str)

                if "all_symptoms_negative" in negated_terms:
                    negated_all = True
                    # Convert common symptoms to negative form
                    negative_items.extend(
                        [
                            "no chest pain",
                            "no shortness of breath",
                            "no nausea",
                            "no vomiting",
                            "no sweating",
                            "no dizziness",
                        ]
                    )
                else:
                    # Add specific negated items
                    negative_items.extend(negated_terms)
            else:
                # Not negated, add to positive
                positive_items.append(item_str)

        logger.debug(
            f"Negation processing: {len(positive_items)} positive, {len(negative_items)} negative, all_negated={negated_all}"
        )
        return positive_items, negative_items, negated_all

    def process_intake_negation(
        self, intake_data: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, list[str]]]:
        """Process negation in entire intake data structure"""
        processed_data = {}
        negation_log = {}

        for key, value in intake_data.items():
            if isinstance(value, (list, tuple)):
                # Process list items for negation
                positive_items, negative_items, all_negated = self.process_negation_in_list(
                    list(value)
                )

                processed_data[key] = {
                    "positive": positive_items,
                    "negative": negative_items,
                    "all_negated": all_negated,
                }

                negation_log[key] = {
                    "original": list(value),
                    "positive": positive_items,
                    "negative": negative_items,
                    "all_negated": all_negated,
                }

                logger.debug(
                    f"Processed {key}: {len(positive_items)} positive, {len(negative_items)} negative"
                )

            elif isinstance(value, str):
                # Process string for negation
                if self.contains_negation(value):
                    negated_items = self.extract_negated_items(value)
                    processed_data[key] = {
                        "positive": [],
                        "negative": negated_items,
                        "all_negated": "all_symptoms_negative" in negated_items,
                    }
                    negation_log[key] = {
                        "original": value,
                        "positive": [],
                        "negative": negated_items,
                        "all_negated": "all_symptoms_negative" in negated_items,
                    }
                else:
                    processed_data[key] = {
                        "positive": [value],
                        "negative": [],
                        "all_negated": False,
                    }
                    negation_log[key] = {
                        "original": value,
                        "positive": [value],
                        "negative": [],
                        "all_negated": False,
                    }
            else:
                # Keep non-string/list values as-is
                processed_data[key] = value
                negation_log[key] = {"original": value}

        logger.info(f"Processed negation for {len(processed_data)} fields")
        return processed_data, negation_log

    def apply_negation_to_ros(
        self, ros_data: dict[str, Any], negation_log: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply negation processing to ROS structure"""
        processed_ros = {
            "cardiovascular": {"positive": [], "negative": []},
            "respiratory": {"positive": [], "negative": []},
            "constitutional": {"positive": [], "negative": []},
        }

        # Map intake questions to ROS systems
        question_mapping = {
            "Q2_Where_is_the_pain": "cardiovascular",
            "Q6_Associated_symptoms": ["cardiovascular", "respiratory", "constitutional"],
            "Q4_Worse_with": "cardiovascular",
            "Q5_Better_with": "cardiovascular",
        }

        for question, systems in question_mapping.items():
            if question in negation_log:
                log_entry = negation_log[question]

                if isinstance(systems, str):
                    systems = [systems]

                for system in systems:
                    # Add positive findings
                    if "positive" in log_entry:
                        processed_ros[system]["positive"].extend(log_entry["positive"])

                    # Add negative findings
                    if "negative" in log_entry:
                        processed_ros[system]["negative"].extend(log_entry["negative"])

        # Clean up duplicates and canonicalize clinical terms
        for ros_system in processed_ros.values():
            ros_system["positive"] = sorted({self._canon(x) for x in ros_system["positive"]})
            ros_system["negative"] = sorted({self._canon(x) for x in ros_system["negative"]})

        logger.info("Applied negation processing to ROS structure")
        return processed_ros

    def _canon(self, item: str) -> str:
        """Canonicalize clinical terms"""
        t = item.lower().strip()
        for k, v in self.CANON.items():
            if k in t:
                return v
        return t

    def get_negation_summary(self, negation_log: dict[str, Any]) -> dict[str, Any]:
        """Get summary of negation processing results"""
        summary = {
            "total_fields": len(negation_log),
            "fields_with_negation": 0,
            "fields_with_all_negation": 0,
            "total_positive_items": 0,
            "total_negative_items": 0,
        }

        for log_entry in negation_log.values():
            if log_entry.get("all_negated"):
                summary["fields_with_all_negation"] += 1

            if log_entry.get("negative"):
                summary["fields_with_negation"] += 1
                summary["total_negative_items"] += len(log_entry["negative"])

            if log_entry.get("positive"):
                summary["total_positive_items"] += len(log_entry["positive"])

        return summary


# Global negation processor instance
negation_processor = NegationProcessor()
