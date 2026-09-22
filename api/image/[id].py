"""GET /api/image/[id]?size=thumb|full

Streams a photo from Google Drive with a long CDN cache so Drive is hit at
most once per photo. Hidden photos return 404 (cache: no-store) so newly
hidden URLs go dead on the next fetch — but note that already-cached copies
in Vercel's edge may persist up to `s-maxage`.
"""
from __future__ import annotations

import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# api/image/[id].py -> add api/ to path so `_lib` imports resolve
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from _lib import drive  # noqa: E402
from _lib.db import db  # noqa: E402
from _lib.http_util import get_query_one, write_error  # noqa: E402

# 24h at the CDN, 1h in browsers. Long enough that Drive is hit ~once per
# photo per day; short enough that admin-hide takes effect the next day.
CACHE_HEADER = "public, s-maxage=86400, max-age=3600, stale-while-revalidate=60"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        photo_id = parsed.path.rstrip("/").split("/")[-1]
        if not photo_id:
            return write_error(self, 400, "missing id")

        size = (get_query_one(self, "size") or "full").lower()
        if size not in ("thumb", "full"):
            return write_error(self, 400, "size must be thumb or full")

        try:
            resp = (
                db()
                .table("photos")
                .select("drive_file_id,drive_thumb_id,is_hidden")
                .eq("id", photo_id)
                .maybe_single()
                .execute()
            )
        except Exception as e:
            return write_error(self, 500, f"db lookup failed: {e}")

        row = resp.data
        if not row or row.get("is_hidden"):
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')
            return

        fid = row["drive_thumb_id"] if size == "thumb" else row["drive_file_id"]
        try:
            data, mime = drive.download(fid)
        except Exception as e:
            return write_error(self, 502, f"drive fetch failed: {e}")

        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", CACHE_HEADER)
        self.end_headers()
        self.wfile.write(data)
