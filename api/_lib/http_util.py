"""Small helpers for BaseHTTPRequestHandler-based Vercel functions."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler


def get_query(handler: BaseHTTPRequestHandler) -> dict[str, list[str]]:
    from urllib.parse import parse_qs, urlparse

    return parse_qs(urlparse(handler.path).query, keep_blank_values=True)


def get_query_one(handler: BaseHTTPRequestHandler, key: str) -> str | None:
    vals = get_query(handler).get(key)
    return vals[0] if vals else None


def client_ip(handler: BaseHTTPRequestHandler) -> str:
    fwd = handler.headers.get("x-forwarded-for") or handler.headers.get(
        "x-real-ip"
    )
    if fwd:
        return fwd.split(",")[0].strip()
    return handler.client_address[0] if handler.client_address else "0.0.0.0"


def write_json(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def write_error(handler: BaseHTTPRequestHandler, status: int, msg: str) -> None:
    write_json(handler, status, {"error": msg})
