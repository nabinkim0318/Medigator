from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from api.core.synthetic import (
    enforce_synthetic_profile,
    find_identifier_reason,
    is_allowed_demo_email,
    is_allowed_demo_phone,
    SyntheticDataRejected,
)


def test_demo_email_and_phone_allowed():
    assert is_allowed_demo_email("user@example.com")
    assert is_allowed_demo_phone("5550101234")
    enforce_synthetic_profile(
        {
            "name": "Demo Patient",
            "email": "user@example.com",
            "phone": "5550101234",
        }
    )


def test_real_email_rejected():
    assert find_identifier_reason({"email": "person@gmail.com"}) == "non_demo_email"
    with pytest.raises(SyntheticDataRejected):
        enforce_synthetic_profile(
            {"name": "Jane", "email": "person@gmail.com", "phone": "5550101234"}
        )


def test_ssn_in_free_text_rejected():
    assert find_identifier_reason({"notes": "ssn 123-45-6789"}) == "ssn_pattern"


def test_demo_mode_does_not_imply_arbitrary_ids_safe():
    reason = find_identifier_reason({"mrn": "MRN: 998877"})
    assert reason == "record_locator_hint"
