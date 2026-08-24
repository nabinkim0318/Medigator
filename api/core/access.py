"""
Deny-by-default API access boundary for the portfolio prototype.

This is not production IAM. The username-derived UUID login is not
authentication and is disabled. Doctor/admin-style reads require a
random operator session issued after DEMO_ACCESS_CODE verification.
"""

from __future__ import annotations

import hmac
import re
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from fastapi import Request

from api.core.config import settings

OPERATOR_SESSION_TTL_SEC = 8 * 3600
OPERATOR_SCHEME = "Bearer"


class AccessAction(str, Enum):
    PUBLIC = "public"
    DEMO_OPEN = "demo_open"
    OPERATOR = "operator"
    DISABLED = "disabled"


@dataclass(frozen=True)
class RouteRule:
    methods: frozenset[str]
    pattern: re.Pattern[str]
    action: AccessAction
    note: str = ""


_operator_sessions: dict[str, float] = {}


def reset_operator_sessions() -> None:
    _operator_sessions.clear()


def issue_operator_session(ttl_sec: int = OPERATOR_SESSION_TTL_SEC) -> str:
    token = secrets.token_urlsafe(32)
    _operator_sessions[token] = time.time() + ttl_sec
    return token


def revoke_operator_session(token: str) -> None:
    _operator_sessions.pop(token, None)


def _extract_bearer(request: Request) -> str | None:
    header = request.headers.get("authorization") or request.headers.get(
        "Authorization"
    )
    if not header:
        return None
    parts = header.split(None, 1)
    if len(parts) != 2 or parts[0] != OPERATOR_SCHEME:
        return None
    return parts[1].strip() or None


def is_operator_request(request: Request) -> bool:
    token = _extract_bearer(request)
    if not token:
        return False
    expires = _operator_sessions.get(token)
    if expires is None:
        return False
    if expires < time.time():
        _operator_sessions.pop(token, None)
        return False
    return True


def access_code_matches(submitted: str) -> bool:
    expected = (settings.DEMO_ACCESS_CODE or "").strip()
    if not expected or not submitted:
        return False
    return hmac.compare_digest(submitted.strip(), expected)


def _rule(
    methods: Iterable[str], path_regex: str, action: AccessAction, note: str = ""
) -> RouteRule:
    return RouteRule(
        methods=frozenset(m.upper() for m in methods),
        pattern=re.compile(path_regex),
        action=action,
        note=note,
    )


# First match wins. Disabled/operator rules are listed before any catch-alls.
ROUTE_RULES: tuple[RouteRule, ...] = (
    # Auth: demo operator session is the only credentialed entry.
    _rule({"POST"}, r"^/api/v1/auth/demo-operator$", AccessAction.PUBLIC),
    _rule({"POST"}, r"^/api/v1/auth/logout$", AccessAction.PUBLIC),
    _rule({"GET"}, r"^/api/v1/auth/status$", AccessAction.PUBLIC),
    _rule(
        {"POST"},
        r"^/api/v1/auth/login$",
        AccessAction.DISABLED,
        "username-derived UUID is not authentication",
    ),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/auth(?:/.*)?$",
        AccessAction.DISABLED,
    ),
    # Patient writes (synthetic intake) vs bulk/IDOR/admin operations.
    _rule({"POST"}, r"^/api/v1/patient/appointment$", AccessAction.DEMO_OPEN),
    _rule({"POST"}, r"^/api/v1/patient/profile$", AccessAction.DEMO_OPEN),
    _rule({"GET"}, r"^/api/v1/patient/profile$", AccessAction.OPERATOR),
    _rule({"GET"}, r"^/api/v1/patient/profile/[^/]+$", AccessAction.OPERATOR),
    _rule({"DELETE"}, r"^/api/v1/patient/profile/[^/]+$", AccessAction.OPERATOR),
    _rule({"GET"}, r"^/api/v1/patient/stats$", AccessAction.OPERATOR),
    _rule(
        {"GET", "PUT", "PATCH", "DELETE", "POST"},
        r"^/api/v1/patient(?:/.*)?$",
        AccessAction.DISABLED,
        "token-in-path, search, export-style, and unauthenticated mutation",
    ),
    # Files, notifications, intake: disabled rather than fake IAM.
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/files(?:/.*)?$",
        AccessAction.DISABLED,
        "unauthenticated file store",
    ),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/notifications(?:/.*)?$",
        AccessAction.DISABLED,
        "unauthenticated notification store",
    ),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/intake(?:/.*)?$",
        AccessAction.DISABLED,
        "intake tokens in URLs",
    ),
    # Analytics: aggregate dashboard only with operator session; export disabled.
    _rule({"GET"}, r"^/api/v1/analytics/dashboard$", AccessAction.OPERATOR),
    _rule({"GET"}, r"^/api/v1/analytics/trends$", AccessAction.OPERATOR),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/analytics(?:/.*)?$",
        AccessAction.DISABLED,
        "export and symptom dumps",
    ),
    # RAG: read/search allowed; index mutation disabled.
    _rule({"GET"}, r"^/api/v1/rag/status$", AccessAction.DEMO_OPEN),
    _rule({"GET"}, r"^/api/v1/rag/health$", AccessAction.DEMO_OPEN),
    _rule({"GET"}, r"^/api/v1/rag/query-example$", AccessAction.DEMO_OPEN),
    _rule({"POST"}, r"^/api/v1/rag/search$", AccessAction.DEMO_OPEN),
    _rule(
        {"POST"},
        r"^/api/v1/rag/build-index$",
        AccessAction.DISABLED,
        "index mutation",
    ),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/rag(?:/.*)?$",
        AccessAction.DISABLED,
    ),
    # Clinical helpers used by the demo UI.
    _rule({"POST"}, r"^/api/v1/summary$", AccessAction.DEMO_OPEN),
    _rule({"POST"}, r"^/api/v1/evidence$", AccessAction.DEMO_OPEN),
    _rule({"POST"}, r"^/api/v1/codes$", AccessAction.DEMO_OPEN),
    # LLM: health only. Advanced endpoints stay disabled in this prototype.
    _rule({"GET"}, r"^/api/v1/llm/health$", AccessAction.DEMO_OPEN),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/llm(?:/.*)?$",
        AccessAction.DISABLED,
        "unauthenticated LLM/chat/report generation",
    ),
    # Reports: lookups/health only. PDF/generate/evaluate disabled.
    _rule({"GET"}, r"^/api/v1/reports/health$", AccessAction.DEMO_OPEN),
    _rule({"GET"}, r"^/api/v1/reports/rules$", AccessAction.DEMO_OPEN),
    _rule({"GET"}, r"^/api/v1/reports/symptoms/[^/]+/icd$", AccessAction.DEMO_OPEN),
    _rule({"GET"}, r"^/api/v1/reports/conditions/[^/]+/cpt$", AccessAction.DEMO_OPEN),
    _rule(
        {"GET", "POST", "PUT", "PATCH", "DELETE"},
        r"^/api/v1/reports(?:/.*)?$",
        AccessAction.DISABLED,
        "pdf/export/generate",
    ),
    _rule({"GET"}, r"^/api/v1/compliance$", AccessAction.PUBLIC),
)


def normalize_path(path: str) -> str:
    if not path:
        return "/"
    if len(path) > 1 and path.endswith("/"):
        return path.rstrip("/")
    return path


def classify(method: str, path: str) -> AccessAction:
    method_u = method.upper()
    path_n = normalize_path(path)
    if method_u == "OPTIONS":
        return AccessAction.PUBLIC
    if not path_n.startswith("/api/"):
        return AccessAction.PUBLIC
    for rule in ROUTE_RULES:
        if method_u in rule.methods and rule.pattern.match(path_n):
            return rule.action
    return AccessAction.DISABLED


def classify_with_rule(method: str, path: str) -> tuple[AccessAction, RouteRule | None]:
    method_u = method.upper()
    path_n = normalize_path(path)
    if method_u == "OPTIONS" or not path_n.startswith("/api/"):
        return AccessAction.PUBLIC, None
    for rule in ROUTE_RULES:
        if method_u in rule.methods and rule.pattern.match(path_n):
            return rule.action, rule
    return AccessAction.DISABLED, None
