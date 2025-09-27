# api/services/intake/tokens.py
import hmac, base64, os, time, uuid
from hashlib import sha256
SECRET = os.getenv("INTAKE_TOKEN_SECRET", "dev-secret").encode()

def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def mk_token(session_id: str, ttl_sec: int = 8*3600) -> tuple[str, int]:
    iat = int(time.time())
    exp = iat + ttl_sec
    payload = f"{session_id}.{iat}.{os.urandom(8).hex()}".encode()
    sig = hmac.new(SECRET, payload, sha256).digest()
    token = f"{b64u(payload)}.{b64u(sig)}"
    return token, exp

def verify(token: str) -> dict | None:
    try:
        p64, s64 = token.split(".")
        payload = base64.urlsafe_b64decode(p64 + "==")
        sig = base64.urlsafe_b64decode(s64 + "==")
        if not hmac.compare_digest(hmac.new(SECRET, payload, sha256).digest(), sig):
            return None
        sid, iat, _ = payload.decode().split(".")
        return {"session_id": sid, "iat": int(iat)}
    except Exception:
        return None
