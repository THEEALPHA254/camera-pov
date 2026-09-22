"""Google Drive client authenticated with an OAuth refresh token.

Uses the drive.file scope, meaning the app can only touch files it creates.
On first use it creates two subfolders (photos/, thumbs/) inside
DRIVE_FOLDER_ID and caches their IDs in module state for the life of the
Lambda instance.
"""
from __future__ import annotations

import io
import os
import threading

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
_TOKEN_URI = "https://oauth2.googleapis.com/token"

_lock = threading.Lock()
_service = None
_folders: dict[str, str] = {}


def _require(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(
            f"required env var {name} is not set (fill it in .env.local for "
            "`vercel dev`, or in Project Settings → Environment Variables on Vercel)"
        )
    return val


def _client():
    global _service
    if _service is not None:
        return _service
    with _lock:
        if _service is None:
            creds = Credentials(
                token=None,
                refresh_token=_require("GOOGLE_REFRESH_TOKEN"),
                client_id=_require("GOOGLE_CLIENT_ID"),
                client_secret=_require("GOOGLE_CLIENT_SECRET"),
                token_uri=_TOKEN_URI,
                scopes=_SCOPES,
            )
            _service = build(
                "drive", "v3", credentials=creds, cache_discovery=False
            )
    return _service


def _ensure_subfolder(name: str) -> str:
    if name in _folders:
        return _folders[name]
    parent = _require("DRIVE_FOLDER_ID")
    svc = _client()
    escaped = name.replace("'", "\\'")
    q = (
        f"'{parent}' in parents and "
        "mimeType = 'application/vnd.google-apps.folder' and "
        f"name = '{escaped}' and trashed = false"
    )
    resp = svc.files().list(q=q, fields="files(id,name)", pageSize=1).execute()
    files = resp.get("files", [])
    if files:
        fid = files[0]["id"]
    else:
        meta = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent],
        }
        fid = svc.files().create(body=meta, fields="id").execute()["id"]
    _folders[name] = fid
    return fid


def upload(data: bytes, filename: str, mime: str, kind: str) -> str:
    """Upload bytes to Drive under the photos/ or thumbs/ subfolder."""
    folder_id = _ensure_subfolder(kind)
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime, resumable=False)
    meta = {"name": filename, "parents": [folder_id]}
    result = _client().files().create(
        body=meta, media_body=media, fields="id"
    ).execute()
    return result["id"]


def download(file_id: str) -> tuple[bytes, str]:
    """Return (bytes, mime) for a Drive file."""
    svc = _client()
    meta = svc.files().get(fileId=file_id, fields="mimeType").execute()
    req = svc.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, req, chunksize=1024 * 1024)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue(), meta.get("mimeType", "application/octet-stream")


def delete(file_id: str) -> None:
    try:
        _client().files().delete(fileId=file_id).execute()
    except Exception:
        # 404 => already gone; treat as success so admin delete stays idempotent
        pass
