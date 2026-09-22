"""Supabase service-role client. Reused across Lambda invocations."""
import os

from supabase import Client, create_client

_client: Client | None = None


def db() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
    return _client
