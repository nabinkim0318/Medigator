import sqlite3
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    username: str


@router.post("/login")
def login(body: LoginIn):
    uname = body.username.strip()
    if not uname:
        raise HTTPException(status_code=400, detail="username required")

    # Ensure DB/table exists and then either return existing token or create a new one
    with sqlite3.connect("copilot.db") as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS user_tokens (username TEXT PRIMARY KEY, token TEXT UNIQUE, created_at TEXT)"
        )
        row = c.execute(
            "SELECT token FROM user_tokens WHERE username=?", (uname,)
        ).fetchone()
        if row:
            return {"username": uname, "token": row[0], "existing": True}
        # create a stable token for this username
        token = str(uuid.uuid5(uuid.NAMESPACE_DNS, uname))
        created_at = datetime.utcnow().isoformat()
        c.execute(
            "INSERT INTO user_tokens(username, token, created_at) VALUES(?,?,?)",
            (uname, token, created_at),
        )
        c.commit()
    return {"username": uname, "token": token, "existing": False}
