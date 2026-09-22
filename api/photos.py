"""GET /api/photos?limit=24&before=<ISO_created_at>

Paginated newest-first list of non-hidden photos. Cursor is the `created_at`
of the last row from the previous page (use `?before=...` to fetch older).
"""
from __future__ import annotations

import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _lib.db import db  # noqa: E402
from _lib.http_util import get_query_one, write_error, write_json  # noqa: E402


DEFAULT_LIMIT = 24
MAX_LIMIT = 60


def _serialize(row: dict) -> dict:
    return {
        "id": row["id"],
        "caption": row.get("caption", ""),
        "captured_by": row.get("captured_by", "") or "Anonymous",
        "created_at": row["created_at"],
        "thumb_url": f"/api/image/{row['id']}?size=thumb",
        "full_url": f"/api/image/{row['id']}?size=full",
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        raw_limit = get_query_one(self, "limit")
        try:
            limit = min(int(raw_limit), MAX_LIMIT) if raw_limit else DEFAULT_LIMIT
        except ValueError:
            return write_error(self, 400, "invalid limit")
        limit = max(1, limit)

        before = get_query_one(self, "before")

        q = (
            db()
            .table("photos")
            .select("id,caption,captured_by,created_at")
            .eq("is_hidden", False)
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
        next_cursor = page[-1]["created_at"] if has_more and page else None

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        import json

        self.wfile.write(
            json.dumps(
                {
                    "photos": [_serialize(r) for r in page],
                    "next_cursor": next_cursor,
                }
            ).encode("utf-8")
        )
