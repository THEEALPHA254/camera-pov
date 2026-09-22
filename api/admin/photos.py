"""GET /api/admin/photos?limit=50&before=<created_at>

Admin listing: includes hidden photos. Requires admin cookie.
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
from _lib.http_util import get_query_one, write_error  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if not admin_ok(self.headers.get("Cookie")):
            return write_error(self, 401, "auth required")

        try:
            limit = int(get_query_one(self, "limit") or 50)
        except ValueError:
            return write_error(self, 400, "invalid limit")
        limit = max(1, min(limit, 200))
        before = get_query_one(self, "before")

        q = (
            db()
            .table("photos")
            .select(
                "id,caption,captured_by,created_at,is_hidden,"
                "drive_file_id,drive_thumb_id"
            )
            .order("created_at", desc=True)
            .limit(limit + 1)
        )
        if before:
            q = q.lt("created_at", before)

        try:
            resp = q.execute()
        except Exception as e:
            return write_error(self, 500, f"db query failed: {e}")

        rows = resp.data or []
        has_more = len(rows) > limit
        page = rows[:limit]

        out = [
            {
                "id": r["id"],
                "caption": r.get("caption", ""),
                "captured_by": r.get("captured_by", "") or "Anonymous",
                "created_at": r["created_at"],
                "is_hidden": bool(r.get("is_hidden")),
                "thumb_url": f"/api/image/{r['id']}?size=thumb",
                "full_url": f"/api/image/{r['id']}?size=full",
            }
            for r in page
        ]

        body = json.dumps(
            {"photos": out, "next_cursor": page[-1]["created_at"] if has_more else None}
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
