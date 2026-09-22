"""One-time helper: obtain a Google Drive refresh token for your own account.

Usage:
    pip install google-auth-oauthlib
    export GOOGLE_CLIENT_ID=...
    export GOOGLE_CLIENT_SECRET=...
    python scripts/get_refresh_token.py

Opens a browser, has you sign in as the Google account that will own the
uploaded photos, and prints the refresh token. Copy it into your .env.local
and into the Vercel environment as GOOGLE_REFRESH_TOKEN.

Notes:
- The token is for the `drive.file` scope: the app can only see files it
  creates. Existing files in your Drive stay private to the app.
- Your Google Cloud OAuth consent screen must include your account as a
  test user (or be published) for this to work.
"""
from __future__ import annotations

import json
import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print(
        "Missing dependency. Run: pip install google-auth-oauthlib",
        file=sys.stderr,
    )
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main() -> int:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET first.",
            file=sys.stderr,
        )
        return 1

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    # `access_type=offline` + `prompt=consent` guarantees we get a refresh token
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        authorization_prompt_message="Opening browser to authenticate...",
        success_message="Authenticated. You can close this tab.",
    )
    if not creds.refresh_token:
        print("No refresh_token returned. Try again.", file=sys.stderr)
        return 1

    print()
    print("=" * 60)
    print("GOOGLE_REFRESH_TOKEN=" + creds.refresh_token)
    print("=" * 60)
    print("Copy the line above into .env.local and Vercel env vars.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
