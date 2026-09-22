"""Supabase service-role client. Reused across Lambda invocations."""
import os

from supabase import Client, create_client

_client: Client | None = None


def _require(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(
            f"required env var {name} is not set (fill it in .env.local for "
            "`vercel dev`, or in Project Settings → Environment Variables on Vercel)"
        )
    return val


def db() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            _require("SUPABASE_URL"),
            _require("SUPABASE_SERVICE_ROLE_KEY"),
        )
    return _client
