"""POST /api/upload

Multipart form fields:
  photo:       required, binary (JPEG/PNG/WebP, <=4MB)
  thumb:       required, binary (JPEG/PNG/WebP, <=4MB)
  caption:     optional, text
  captured_by: optional, text (blank -> "Anonymous")

Query params:
  e:           event code (must match EVENT_CODE)
"""
from __future__ import annotations

import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _lib import drive, exif, multipart, validate  # noqa: E402
from _lib.auth import event_code_ok  # noqa: E402
from _lib.db import db  # noqa: E402
from _lib.http_util import (  # noqa: E402
    client_ip,
    get_query_one,
    write_error,
    write_json,
)
from _lib.ratelimit import ip_hash, over_limit  # noqa: E402


MAX_CAPTION = 280
MAX_NAME = 60


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) > limit:
        text = text[:limit].rstrip()
    return text


class handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        # Warmup ping. The frontend fires this on landing so the Python
        # runtime cold-starts (importing supabase + google-api-python-client
        # takes ~10-20s) while the guest is still framing their photo. By
        # the time they tap SHARE, this same Lambda is warm and the POST
        # returns in a couple of seconds instead of ~20.
        self.send_response(204)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_POST(self):  # noqa: N802 (BaseHTTPRequestHandler naming)
        if not event_code_ok(get_query_one(self, "e")):
            return write_error(self, 403, "invalid event code")

        ctype = self.headers.get("Content-Type", "")
        boundary = multipart.parse_boundary(ctype)
        if not boundary:
            return write_error(self, 400, "expected multipart/form-data")

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return write_error(self, 400, "invalid content-length")
        if length <= 0 or length > 9 * 1024 * 1024:
            return write_error(self, 413, "request too large")

        body = self.rfile.read(length)
        parts = multipart.parse(body, boundary)

        photo = parts.get("photo")
        thumb = parts.get("thumb")
        if not photo or not thumb:
            return write_error(self, 400, "photo and thumb are required")

        try:
            photo_mime = validate.validate(photo[1])
            thumb_mime = validate.validate(thumb[1])
        except ValueError as e:
            return write_error(self, 400, str(e))

        # rate limit (per hashed IP)
        hashed = ip_hash(client_ip(self))
        try:
            if over_limit(hashed):
                return write_error(self, 429, "upload limit reached, try later")
        except Exception:
            # if the rate-limit query fails, don't block uploads — log and continue
            pass

        caption = _clip(multipart.field(parts, "caption"), MAX_CAPTION)
        captured_by = _clip(multipart.field(parts, "captured_by"), MAX_NAME)
        if not captured_by:
            captured_by = "Anonymous"

        # strip EXIF (incl. GPS) from full-size; thumb is our own client render
        photo_bytes = exif.strip(photo[1], photo_mime)
        thumb_bytes = thumb[1]

        # upload to Drive — do both in parallel; each round trip is ~1.5-3s
        # so this halves the Drive time on warm requests.
        photo_ext = "jpg" if photo_mime == "image/jpeg" else photo_mime.split("/")[-1]
        thumb_ext = "jpg" if thumb_mime == "image/jpeg" else thumb_mime.split("/")[-1]
        base = uuid.uuid4().hex
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                photo_fut = pool.submit(
                    drive.upload,
                    photo_bytes, f"{base}.{photo_ext}", photo_mime, "photos",
                )
                thumb_fut = pool.submit(
                    drive.upload,
                    thumb_bytes, f"{base}.thumb.{thumb_ext}", thumb_mime, "thumbs",
                )
                photo_id = photo_fut.result()
                thumb_id = thumb_fut.result()
        except Exception as e:
            return write_error(self, 502, f"drive upload failed: {e}")

        row = {
            "drive_file_id": photo_id,
            "drive_thumb_id": thumb_id,
            "caption": caption,
            "captured_by": captured_by,
            "is_hidden": False,
            "ip_hash": hashed,
            "user_agent": (self.headers.get("User-Agent") or "")[:255],
        }
        try:
            resp = db().table("photos").insert(row).execute()
            record = resp.data[0]
        except Exception as e:
            # try to unwind Drive uploads to avoid orphans
            drive.delete(photo_id)
            drive.delete(thumb_id)
            return write_error(self, 500, f"db insert failed: {e}")

        return write_json(
            self,
            201,
            {
                "id": record["id"],
                "caption": record["caption"],
                "captured_by": record["captured_by"],
                "created_at": record["created_at"],
                "thumb_url": f"/api/image/{record['id']}?size=thumb",
                "full_url": f"/api/image/{record['id']}?size=full",
            },
        )
