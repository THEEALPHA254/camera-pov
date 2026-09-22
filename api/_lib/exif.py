"""Strip EXIF (including GPS) from image bytes.

Uses piexif for JPEG (in-place, no re-encode, no quality loss).
PNG / WebP are passed through: PNG has no standard EXIF chunk and iPhones
almost never emit WebP; the GPS threat model is JPEG-first.
"""
from __future__ import annotations

import piexif


def strip(data: bytes, mime: str) -> bytes:
    if mime != "image/jpeg":
        return data
    try:
        return piexif.remove(data)
    except Exception:
        return data
