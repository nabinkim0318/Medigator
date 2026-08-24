"""Demo operator session — not production authentication."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from api.core.access import (
    access_code_matches,
    issue_operator_session,
    is_operator_request,
    revoke_operator_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class OperatorIn(BaseModel):
    access_code: str


class LoginIn(BaseModel):
    username: str


@router.post("/demo-operator")
def demo_operator(body: OperatorIn):
    if not access_code_matches(body.access_code):
        raise HTTPException(status_code=401, detail="invalid demo access code")
    session = issue_operator_session()
    return {
        "operator_session": session,
        "token_type": "bearer",
        "note": "Prototype operator session. Not production authentication.",
    }


@router.post("/logout")
def logout(request: Request):
    header = request.headers.get("authorization") or ""
    parts = header.split(None, 1)
    if len(parts) == 2:
        revoke_operator_session(parts[1].strip())
    return {"ok": True}


@router.get("/status")
def status(request: Request):
    return {
        "operator": is_operator_request(request),
        "auth_model": "demo_operator_session",
        "username_derived_uuid_is_auth": False,
    }


@router.post("/login")
def login(_body: LoginIn):
    """Disabled: deterministic username-derived UUIDs are not authentication."""
    raise HTTPException(
        status_code=403,
        detail=(
            "Disabled. Username-derived tokens are not authentication. "
            "Patients use a local demo session id; operators use /auth/demo-operator."
        ),
    )
