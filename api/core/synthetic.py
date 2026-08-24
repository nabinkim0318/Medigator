"""
Synthetic/demo-data-only policy.

This is a portfolio-prototype guardrail, not de-identification and not a
production control. DEMO_MODE does not make arbitrary identifiers safe.
"""

from __future__ import annotations

import re
from typing import Any

from fastapi import HTTPException

from api.core.config import settings

# North American fictional/test exchange (not a complete phone-number policy).
_FAKE_NANP_PHONE = re.compile(r"^555\d{7}$")
_ALLOWED_EMAIL_DOMAINS = ("@example.com", "@demo.local", "@test.local")

_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_SSN_COMPACT = re.compile(r"\b\d{9}\b")
_PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_MRN_HINT = re.compile(r"\b(?:MRN|SSN|DOB|medical record)\s*[:#]?\s*\S+", re.I)


class SyntheticDataRejected(HTTPException):
    """Raised when a payload looks like real identifiers rather than demo data."""

    def __init__(self, reason_code: str):
        super().__init__(
            status_code=400,
            detail={
                "error": "synthetic_data_required",
                "reason": reason_code,
                "message": (
                    "This prototype accepts synthetic/demo data only. "
                    "DEMO_MODE does not make real identifiers safe. "
                    "Do not submit real patient information."
                ),
            },
        )


def synthetic_data_only_enabled() -> bool:
    return bool(getattr(settings, "SYNTHETIC_DATA_ONLY", True) or settings.DEMO_MODE)


def is_allowed_demo_email(value: str) -> bool:
    email = value.strip().lower()
    return email.endswith(_ALLOWED_EMAIL_DOMAINS) and "@" in email


def is_allowed_demo_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return bool(_FAKE_NANP_PHONE.match(digits))


def _strings_in(obj: Any) -> list[str]:
    if obj is None:
        return []
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        out: list[str] = []
        for v in obj.values():
            out.extend(_strings_in(v))
        return out
    if isinstance(obj, (list, tuple, set)):
        out = []
        for v in obj:
            out.extend(_strings_in(v))
        return out
    return [str(obj)]


def find_identifier_reason(obj: Any, *, profile_fields: bool = False) -> str | None:
    """
    Return a stable reason code if obvious real-identifier patterns are present.

    This is heuristic and incomplete. It does not de-identify data.
    """
    texts = _strings_in(obj)
    joined = " ".join(texts)

    if _SSN.search(joined):
        return "ssn_pattern"
    if _MRN_HINT.search(joined):
        return "record_locator_hint"

    emails = _EMAIL.findall(joined)
    for email in emails:
        if not is_allowed_demo_email(email):
            return "non_demo_email"

    phones = _PHONE.findall(joined)
    for phone in phones:
        if not is_allowed_demo_phone(phone):
            return "non_demo_phone"

    if (
        not profile_fields
        and _SSN_COMPACT.search(joined)
        and not any(is_allowed_demo_phone(t) for t in texts)
    ):
        return "ssn_compact"

    return None


def enforce_synthetic_payload(obj: Any, *, profile_fields: bool = False) -> None:
    """Reject obvious real identifiers. Does not claim complete de-identification."""
    if not synthetic_data_only_enabled():
        return
    reason = find_identifier_reason(obj, profile_fields=profile_fields)
    if reason:
        raise SyntheticDataRejected(reason)


def enforce_synthetic_profile(profile: dict[str, Any]) -> None:
    """Stricter checks for explicit identity fields collected by the demo form."""
    if not synthetic_data_only_enabled():
        return

    email = str(profile.get("email") or "").strip()
    phone = str(profile.get("phone") or "").strip()
    name = str(profile.get("name") or "").strip()

    if email and not is_allowed_demo_email(email):
        raise SyntheticDataRejected("non_demo_email")
    if phone and not is_allowed_demo_phone(phone):
        raise SyntheticDataRejected("non_demo_phone")
    if name and _SSN.search(name):
        raise SyntheticDataRejected("ssn_pattern")

    remainder = {
        k: v for k, v in profile.items() if k not in {"email", "phone", "name"}
    }
    enforce_synthetic_payload(remainder)
