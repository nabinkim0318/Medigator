"""Honest source labels for demo API responses. Not a clinical audit trail."""

from __future__ import annotations

from typing import Any


def provenance(
    *,
    source: str,
    provider: str | None = None,
    model: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    return {
        "source": source,
        "provider": provider,
        "model": model,
        "note": note,
    }
