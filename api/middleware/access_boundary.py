"""Server-side deny-by-default boundary. UI routing is not authorization."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.core.access import AccessAction, classify_with_rule, is_operator_request
from api.core.safe_logging import log_warning
import logging

logger = logging.getLogger(__name__)


_DISABLED_DETAIL = {
    "error": "endpoint_disabled",
    "message": (
        "This endpoint is disabled on the prototype security boundary. "
        "UI routing is not authorization."
    ),
}

_OPERATOR_DETAIL = {
    "error": "operator_required",
    "message": (
        "This endpoint requires a demo operator session. "
        "POST /api/v1/auth/demo-operator with DEMO_ACCESS_CODE. "
        "This is not production authentication."
    ),
}


_UNIMPLEMENTED_DETAIL = {
    "error": "not_implemented",
    "message": (
        "This is a placeholder clinical endpoint. It does not diagnose, treat, "
        "or generate a real clinical report. Research prototype only."
    ),
}


class AccessBoundaryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        action, rule = classify_with_rule(request.method, request.url.path)
        if action in {AccessAction.PUBLIC, AccessAction.DEMO_OPEN}:
            return await call_next(request)

        if action == AccessAction.OPERATOR:
            if is_operator_request(request):
                return await call_next(request)
            log_warning(
                logger,
                "operator_required",
                method=request.method,
                path=request.url.path,
                status_code=401,
            )
            return JSONResponse(status_code=401, content=_OPERATOR_DETAIL)

        if action == AccessAction.UNIMPLEMENTED:
            log_warning(
                logger,
                "endpoint_unimplemented",
                method=request.method,
                path=request.url.path,
                status_code=501,
                reason=(rule.note if rule else "placeholder"),
            )
            return JSONResponse(status_code=501, content=_UNIMPLEMENTED_DETAIL)

        log_warning(
            logger,
            "endpoint_disabled",
            method=request.method,
            path=request.url.path,
            status_code=403,
            reason=(rule.note if rule else "deny_by_default"),
        )
        return JSONResponse(status_code=403, content=_DISABLED_DETAIL)
