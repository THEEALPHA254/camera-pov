"""POST /api/admin/hide  {"id": "<uuid>", "hidden": true|false}

Toggles the is_hidden flag on a photo. Requires admin cookie.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from _lib.auth import admin_ok  # noqa: E402
from _lib.db import db  # noqa: E402
from _lib.http_util import write_error, write_json  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        if not admin_ok(self.headers.get("Cookie")):
            return write_error(self, 401, "auth required")

        try:
            length = int(self.headers.get("Content-Length") or 0)
            data = json.loads(self.rfile.read(length) if length else b"{}")
        except Exception:
            return write_error(self, 400, "invalid JSON body")

        photo_id = data.get("id")
        if not photo_id or not isinstance(photo_id, str):
            return write_error(self, 400, "id required")
        hidden = bool(data.get("hidden"))

        try:
            resp = (
                db()
                .table("photos")
                .update({"is_hidden": hidden})
                .eq("id", photo_id)
                .execute()
            )
        except Exception as e:
            return write_error(self, 500, f"db update failed: {e}")

        if not resp.data:
            return write_error(self, 404, "photo not found")

        return write_json(self, 200, {"ok": True, "is_hidden": hidden})
