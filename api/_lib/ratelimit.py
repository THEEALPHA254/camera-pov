"""Per-IP rate limit backed by the photos table."""
from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from .db import db

LIMIT_PER_HOUR = 20


def ip_hash(ip: str) -> str:
    salt = (os.environ.get("IP_HASH_SALT") or "").encode("utf-8")
    return hmac.new(salt, ip.encode("utf-8"), hashlib.sha256).hexdigest()


def over_limit(hashed_ip: str) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    resp = (
        db()
        .table("photos")
        .select("id", count="exact")
        .eq("ip_hash", hashed_ip)
        .gte("created_at", cutoff)
        .execute()
    )
    return (resp.count or 0) >= LIMIT_PER_HOUR
