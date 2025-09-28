# api/services/llm/validators.py
import json
import logging
import re
from typing import Any

from api.core.schemas import SummaryOut

# Get logger
logger = logging.getLogger(__name__)

# Enhanced forbidden patterns with medical terms
FORBIDDEN = re.compile(
    r"\b(diagnos|treat|prescrib|medication|drug|risk\s*\d+%|mortality|death|fatal|prognos)\b",
    re.IGNORECASE,
)

# Duration enum validation
VALID_DURATIONS = {
    "seconds",
    "1-5min",
    "5-30min",
    "30min+",
    "hours",
    "continuous",
    "intermittent",
}

# Pain severity validation
VALID_SEVERITY = {
    "0-2",
    "3-5",
    "6-7",
    "8-10",
    "mild",
    "moderate",
    "severe",
    "very severe",
}

# Body location validation
VALID_LOCATIONS = {
    "chest",
    "left arm",
    "right arm",
    "jaw",
    "neck",
    "back",
    "shoulder",
    "abdomen",
}


def _norm(s: str) -> str:
    """Normalize string for comparison"""
    return s.strip().lower()


def validate_duration(value: str) -> bool:
    """Validate duration values with exact match"""
    if not value:
        return True
    normalized = _norm(value)
    return normalized in VALID_DURATIONS


def validate_severity(value: str) -> bool:
    """Validate pain severity values with exact match"""
    if not value:
        return True
    normalized = _norm(value)
    return normalized in VALID_SEVERITY


def validate_location(value: str) -> bool:
    """Validate body location values with exact match"""
    if not value:
        return True
    normalized = _norm(value)
    return normalized in VALID_LOCATIONS


def sanitize_hpi(text: str) -> str:
    """Remove forbidden medical terms from HPI"""
    if not text:
        return ""

    # Remove forbidden patterns
    sanitized = FORBIDDEN.sub("[REDACTED]", text)

    # Log if any redaction occurred
    if sanitized != text:
        logger.warning(
            f"HPI sanitization applied: {len(text)} -> {len(sanitized)} chars"
        )

    return sanitized


def validate_json_structure(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate JSON structure and return validation results"""
    errors = []

    # Required fields check
    required_fields = ["hpi", "ros", "pmh", "meds", "flags"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Type validation
    if "hpi" in data and not isinstance(data["hpi"], str):
        errors.append("hpi must be string")

    if "pmh" in data and not isinstance(data["pmh"], list):
        errors.append("pmh must be array")

    if "meds" in data and not isinstance(data["meds"], list):
        errors.append("meds must be array")

    if "flags" in data:
        if not isinstance(data["flags"], dict):
            errors.append("flags must be object")
        else:
            required_flags = ["ischemic_features", "dm_followup", "labs_a1c_needed"]
            for flag in required_flags:
                if flag not in data["flags"]:
                    errors.append(f"Missing required flag: {flag}")
                elif not isinstance(data["flags"][flag], bool):
                    errors.append(f"Flag {flag} must be boolean")

    # ROS validation
    if "ros" in data:
        if not isinstance(data["ros"], dict):
            errors.append("ros must be object")
        else:
            required_systems = ["cardiovascular", "respiratory", "constitutional"]
            for system in required_systems:
                if system not in data["ros"]:
                    errors.append(f"Missing required ROS system: {system}")
                elif not isinstance(data["ros"][system], dict):
                    errors.append(f"ROS {system} must be object")
                else:
                    ros_data = data["ros"][system]
                    if "positive" not in ros_data or not isinstance(
                        ros_data["positive"], list
                    ):
                        errors.append(f"ROS {system}.positive must be array")
                    if "negative" not in ros_data or not isinstance(
                        ros_data["negative"], list
                    ):
                        errors.append(f"ROS {system}.negative must be array")

    return len(errors) == 0, errors


def parse_and_validate(text: str) -> SummaryOut:
    """Parse and validate LLM response with enhanced validation"""
    try:
        # Parse JSON
        data = json.loads(text)

        # Structure validation
        is_valid, errors = validate_json_structure(data)
        if not is_valid:
            logger.error(f"JSON structure validation failed: {errors}")
            raise ValueError(f"Structure validation failed: {'; '.join(errors)}")

        # Sanitize HPI
        if "hpi" in data:
            data["hpi"] = sanitize_hpi(data["hpi"])

        # Validate content constraints
        if "hpi" in data and len(data["hpi"]) > 600:
            logger.warning(f"HPI too long ({len(data['hpi'])} chars), truncating")
            data["hpi"] = data["hpi"][:600]

        # Create and validate Pydantic model
        summary = SummaryOut.model_validate(data)

        logger.info("JSON validation successful")
        return summary

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        raise ValueError(f"Invalid JSON: {e}")
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise ValueError(f"Validation error: {e}")


def retry_with_correction(data: dict[str, Any], max_retries: int = 2) -> SummaryOut:
    """Retry parsing with corrections"""
    for attempt in range(max_retries):
        try:
            return parse_and_validate(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                # Apply corrections
                data = apply_corrections(data)
            else:
                raise

    raise ValueError("Max retries exceeded")


def apply_corrections(data: dict[str, Any]) -> dict[str, Any]:
    """Apply common corrections to malformed data"""
    # Ensure required fields exist
    if "hpi" not in data:
        data["hpi"] = ""

    if "pmh" not in data:
        data["pmh"] = []

    if "meds" not in data:
        data["meds"] = []

    if "flags" not in data:
        data["flags"] = {
            "ischemic_features": False,
            "dm_followup": False,
            "labs_a1c_needed": False,
        }

    if "ros" not in data:
        data["ros"] = {
            "cardiovascular": {"positive": [], "negative": []},
            "respiratory": {"positive": [], "negative": []},
            "constitutional": {"positive": [], "negative": []},
        }

    # Ensure correct types
    if not isinstance(data["pmh"], list):
        data["pmh"] = []

    if not isinstance(data["meds"], list):
        data["meds"] = []

    if not isinstance(data["flags"], dict):
        data["flags"] = {
            "ischemic_features": False,
            "dm_followup": False,
            "labs_a1c_needed": False,
        }

    return data
