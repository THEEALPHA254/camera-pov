"""POST /api/admin/login

Body: {"password": "..."}

If the password matches ADMIN_PASSWORD, sets an HMAC-signed httpOnly cookie
that later /api/admin/* endpoints check via auth.admin_ok.
"""
from __future__ import annotations

import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from _lib.auth import (  # noqa: E402
    admin_cookie_header,
    sign_admin_token,
)
from _lib.http_util import write_error, write_json  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            data = json.loads(raw or b"{}")
        except Exception:
            return write_error(self, 400, "invalid JSON body")

        supplied = (data.get("password") or "").encode("utf-8")
        expected = (os.environ.get("ADMIN_PASSWORD") or "").encode("utf-8")
        if not expected:
            return write_error(self, 500, "admin password not configured")
        if not supplied or not hmac.compare_digest(supplied, expected):
            return write_error(self, 401, "incorrect password")

        token = sign_admin_token()
        body = json.dumps({"ok": True}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Set-Cookie", admin_cookie_header(token))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
