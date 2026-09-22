"""Event-code check + HMAC-signed admin session cookie."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from http.cookies import SimpleCookie

ADMIN_COOKIE = "cap_admin"
ADMIN_TTL_SECONDS = 60 * 60 * 12  # 12 hours


def event_code_ok(supplied: str | None) -> bool:
    expected = (os.environ.get("EVENT_CODE") or "").strip()
    if not expected:
        return True  # no code configured => open
    if not supplied:
        return False
    return hmac.compare_digest(supplied.strip(), expected)


def _secret() -> bytes:
    key = (os.environ.get("ADMIN_SESSION_SECRET") or "").encode("utf-8")
    if not key:
        raise RuntimeError("ADMIN_SESSION_SECRET is not set")
    return key


def _b64u_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign_admin_token() -> str:
    payload = {"exp": int(time.time()) + ADMIN_TTL_SECONDS}
    body = _b64u_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(_secret(), body.encode(), hashlib.sha256).digest()
    return f"{body}.{_b64u_encode(sig)}"


def admin_ok(cookie_header: str | None) -> bool:
    if not cookie_header:
        return False
    try:
        jar = SimpleCookie()
        jar.load(cookie_header)
        if ADMIN_COOKIE not in jar:
            return False
        body, sig = jar[ADMIN_COOKIE].value.split(".", 1)
        want = hmac.new(_secret(), body.encode(), hashlib.sha256).digest()
        got = _b64u_decode(sig)
        if not hmac.compare_digest(want, got):
            return False
        payload = json.loads(_b64u_decode(body))
        return int(payload.get("exp", 0)) > int(time.time())
    except Exception:
        return False


def admin_cookie_header(token: str) -> str:
    return (
        f"{ADMIN_COOKIE}={token}; "
        f"Max-Age={ADMIN_TTL_SECONDS}; "
        "Path=/; HttpOnly; Secure; SameSite=Strict"
    )


def clear_admin_cookie_header() -> str:
    return (
        f"{ADMIN_COOKIE}=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Strict"
    )
