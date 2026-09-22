"""Minimal multipart/form-data parser.

Only handles the shape produced by our own frontend: a handful of small
fields plus 1-2 binary parts. Not general-purpose (no nested multipart, no
chunked transfer). Keeping this tiny avoids pinning a third-party package
that has changed APIs several times.
"""
from __future__ import annotations

import re


def parse_boundary(content_type: str) -> str | None:
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type, re.I)
    if not m:
        return None
    return (m.group(1) or m.group(2)).strip()


def _parse_disposition(raw: bytes) -> tuple[str | None, str | None]:
    """Return (name, filename) from a Content-Disposition header line."""
    name = None
    filename = None
    for kv in raw.split(b";"):
        kv = kv.strip()
        low = kv.lower()
        if low.startswith(b"name="):
            name = kv[5:].strip(b'"').decode(errors="replace")
        elif low.startswith(b"filename="):
            filename = kv[9:].strip(b'"').decode(errors="replace")
    return name, filename


def parse(body: bytes, boundary: str) -> dict[str, tuple[str | None, bytes]]:
    """Return {field_name: (filename_or_None, raw_bytes)}."""
    delim = ("--" + boundary).encode()
    result: dict[str, tuple[str | None, bytes]] = {}
    segments = body.split(delim)
    # segments[0] is preamble, segments[-1] starts with '--' (closing marker).
    for seg in segments[1:-1]:
        seg = seg.lstrip(b"\r\n")
        if not seg:
            continue
        head, sep, content = seg.partition(b"\r\n\r\n")
        if not sep:
            continue
        content = content[:-2] if content.endswith(b"\r\n") else content
        name = None
        filename = None
        for line in head.split(b"\r\n"):
            low = line.lower()
            if low.startswith(b"content-disposition"):
                _, _, rest = line.partition(b":")
                name, filename = _parse_disposition(rest)
                break
        if name:
            result[name] = (filename, content)
    return result


def field(
    parts: dict[str, tuple[str | None, bytes]], key: str, default: str = ""
) -> str:
    hit = parts.get(key)
    if not hit:
        return default
    _, data = hit
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return default
