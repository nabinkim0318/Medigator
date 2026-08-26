"""
Operational logging that avoids patient content.

Never log request bodies, patient/operator tokens, raw queries, raw LLM
output, or third-party exception payloads. Event names, status, counts,
and non-content IDs are allowed.
"""

from __future__ import annotations

import logging
import re
from typing import Any

_TOKEN_QUERY = re.compile(r"([?&](?:token|access_token|session|key)=)[^&]+", re.I)
_BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+", re.I)
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PHONE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
_UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.I,
)

_ALLOWED_KEYS = frozenset(
    {
        "event",
        "status",
        "path",
        "method",
        "status_code",
        "error_type",
        "error_count",
        "resource",
        "count",
        "duration_ms",
        "reason",
        "action",
        "enabled",
        "initialized",
        "attempt",
        "max_attempts",
        "field_count",
        "result_count",
        "chars",
        "mode",
    }
)


def sanitize_text(value: str) -> str:
    out = _TOKEN_QUERY.sub(r"\1[REDACTED]", value)
    out = _BEARER.sub(r"\1[REDACTED]", out)
    out = _EMAIL.sub("[EMAIL]", out)
    out = _SSN.sub("[SSN]", out)
    out = _PHONE.sub("[PHONE]", out)
    out = _UUID.sub("[ID]", out)
    return out


def sanitize_path(path: str) -> str:
    return sanitize_text(path.split("?", 1)[0])


def _safe_fields(**fields: Any) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in fields.items():
        if key not in _ALLOWED_KEYS:
            continue
        if value is None:
            continue
        if isinstance(value, (int, float, bool)):
            safe[key] = value
        else:
            safe[key] = sanitize_text(str(value))
    return safe


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    payload = _safe_fields(event=event, **fields)
    parts = [f"{k}={payload[k]}" for k in sorted(payload)]
    logger.log(level, " ".join(parts))


def log_info(logger: logging.Logger, event: str, **fields: Any) -> None:
    log_event(logger, logging.INFO, event, **fields)


def log_warning(logger: logging.Logger, event: str, **fields: Any) -> None:
    log_event(logger, logging.WARNING, event, **fields)


def log_error(logger: logging.Logger, event: str, **fields: Any) -> None:
    log_event(logger, logging.ERROR, event, **fields)


class SensitiveLogFilter(logging.Filter):
    """Last-resort redaction if a logger interpolates sensitive text anyway."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if isinstance(record.msg, str):
                record.msg = sanitize_text(record.msg)
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {
                        k: sanitize_text(v) if isinstance(v, str) else v
                        for k, v in record.args.items()
                    }
                elif isinstance(record.args, tuple):
                    record.args = tuple(
                        sanitize_text(a) if isinstance(a, str) else a
                        for a in record.args
                    )
        except Exception:
            record.msg = "[log_redaction_failed]"
            record.args = ()
        return True
