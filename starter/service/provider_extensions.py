from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from cryptography.fernet import Fernet
from fastapi import File, Form, HTTPException, Request, UploadFile

DATA_DIR = Path(os.environ.get("MIRROR_DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "mirror.db"
EVIDENCE_DIR = DATA_DIR / "evidence"
DEFAULT_PROVIDER = os.environ.get("MIRROR_DEFAULT_PROVIDER", "google_workspace")
EVIDENCE_PROVIDER = os.environ.get("MIRROR_EVIDENCE_PROVIDER", "auto").strip().lower()
MAX_EVIDENCE_BYTES = int(os.environ.get("MIRROR_MAX_EVIDENCE_BYTES", str(100 * 1024 * 1024)))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def ensure_schema() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS evidence_replication (
              evidence_uuid TEXT NOT NULL,
              provider TEXT NOT NULL,
              provider_object_id TEXT NOT NULL,
              provider_locator TEXT NOT NULL,
              web_url TEXT,
              content_hash TEXT NOT NULL,
              readback_verified INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              PRIMARY KEY(evidence_uuid, provider)
            );
            """
        )


def _cipher() -> Fernet:
    key = os.environ.get("MIRROR_TOKEN_KEY", "").strip()
    if not key:
        raise HTTPException(503, "MIRROR_TOKEN_KEY is required before cloud provider tokens may be used")
    try:
        return Fernet(key.encode("ascii"))
    except Exception as exc:
        raise HTTPException(503, "MIRROR_TOKEN_KEY must be a valid Fernet key") from exc


def _load_token(provider: str) -> tuple[dict[str, Any], str]:
    with connect() as db:
        row = db.execute("SELECT encrypted_json,updated_at FROM oauth_tokens WHERE provider=?", (provider,)).fetchone()
    if not row:
        raise HTTPException(409, f"{provider} is not connected")
    try:
        token = json.loads(_cipher().decrypt(row["encrypted_json"].encode()).decode())
    except Exception as exc:
        raise HTTPException(503, f"stored {provider} token cannot be decrypted") from exc
    return token, row["updated_at"]


def _save_token(provider: str, token: dict[str, Any]) -> None:
    encrypted = _cipher().encrypt(json.dumps(token).encode()).decode()
    with connect() as db:
        db.execute(
            "INSERT INTO oauth_tokens(provider,encrypted_json,updated_at) VALUES(?,?,?) "
            "ON CONFLICT(provider) DO UPDATE SET encrypted_json=excluded.encrypted_json,updated_at=excluded.updated_at",
            (provider, encrypted, now_iso()),
        )
        db.commit()


def _token_expired(token: dict[str, Any], updated_at: str) -> bool:
    expires_in = int(token.get("expires_in") or 0)
    if expires_in <= 0:
        return False
    issued = datetime.fromisoformat(updated_at)
    return datetime.now(timezone.utc) >= issued + timedelta(seconds=max(1, expires_in - 90))


async def _google_access_token() -> str:
    token, updated_at = _load_token("google")
    if _token_expired(token, updated_at):
        refresh = token.get("refresh_token")
        if not refresh:
            raise HTTPException(409, "Google access expired and no refresh token is stored; reconnect Google Workspace")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
                    "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
                    "refresh_token": refresh,
                    "grant_type": "refresh_token",
                },
            )
        if response.status_code >= 400:
            raise HTTPException(502, "Google refresh-token exchange failed")
        refreshed = response.json()
        refreshed.setdefault("refresh_token", refresh)
        token.update(refreshed)
        _save_token("google", token)
    access = str(token.get("access_token") or "")
    if not access:
        raise HTTPException(409, "Google connection has no access token")
    return access


async def _microsoft_access_token() -> str:
    token, updated_at = _load_token("microsoft")
    if _token_expired(token, updated_at):
        refresh = token.get("refresh_token")
        if not refresh:
            raise HTTPException(409, "Microsoft access expired and no refresh token is stored; reconnect Microsoft 365")
        tenant = os.environ.get("MICROSOFT_TENANT", "common").strip() or "common"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
                data={
                    "client_id": os.environ.get("MICROSOFT_CLIENT_ID", ""),
                    "client_secret": os.environ.get("MICROSOFT_CLIENT_SECRET", ""),
                    "refresh_token": refresh,
                    "grant_type": "refresh_token",
                    "scope": token.get("scope") or "openid profile email offline_access User.Read Files.ReadWrite Calendars.ReadWrite Mail.Read",
                },
            )
        if response.status_code >= 400:
            raise HTTPException(502, "Microsoft refresh-token exchange failed")
        refreshed = response.json()
        refreshed.setdefault("refresh_token", refresh)
        token.update(refreshed)
        _save_token("microsoft", token)
    access = str(token.get("access_token") or "")
    if not access:
        raise HTTPException(409, "Microsoft connection has no access token")
    return access


def _has_token(provider: str) -> bool:
    with connect() as db:
        return bool(db.execute("SELECT 1 FROM oauth_tokens WHERE provider=?", (provider,)).fetchone())


def selected_evidence_provider() -> str:
    configured = EVIDENCE_PROVIDER.replace("-", "_")
    if configured in {"local", "google", "microsoft"}:
        return configured
    if DEFAULT_PROVIDER == "google_workspace" and _has_token("google"):
        return "google"
    if DEFAULT_PROVIDER == "microsoft_365" and _has_token("microsoft"):
        return "microsoft"
    if _has_token("google"):
        return "google"
    if _has_token("microsoft"):
        return "microsoft"
    return "local"


async def google_health() -> dict[str, Any]:
    if not _has_token("google"):
        return {"connected": False, "provider": "google_workspace", "capabilities": {}}
    access = await _google_access_token()
    headers = {"Authorization": f"Bearer {access}"}
    probes = {
        "identity": "https://openidconnect.googleapis.com/v1/userinfo",
        "drive": "https://www.googleapis.com/drive/v3/files/root?fields=id,name",
        "calendar": "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=1",
        "gmail_read": "https://gmail.googleapis.com/gmail/v1/users/me/profile",
    }
    capabilities: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for capability, url in probes.items():
            response = await client.get(url, headers=headers)
            capabilities[capability] = {"available": response.status_code < 400, "status_code": response.status_code}
    return {"connected": True, "provider": "google_workspace", "capabilities": capabilities}


async def microsoft_health() -> dict[str, Any]:
    if not _has_token("microsoft"):
        return {"connected": False, "provider": "microsoft_365", "capabilities": {}}
    access = await _microsoft_access_token()
    headers = {"Authorization": f"Bearer {access}"}
    probes = {
        "identity": "https://graph.microsoft.com/v1.0/me?$select=id,displayName,mail,userPrincipalName",
        "drive": "https://graph.microsoft.com/v1.0/me/drive?$select=id,driveType",
        "calendar": "https://graph.microsoft.com/v1.0/me/calendar?$select=id,name",
        "mail_read": "https://graph.microsoft.com/v1.0/me/mailFolders/inbox?$select=id,displayName",
    }
    capabilities: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for capability, url in probes.items():
            response = await client.get(url, headers=headers)
            capabilities[capability] = {"available": response.status_code < 400, "status_code": response.status_code}
    return {"connected": True, "provider": "microsoft_365", "capabilities": capabilities}


async def _google_upload(evidence_uuid: str, filename: str, mime_type: str, content: bytes, sha256: str) -> dict[str, Any]:
    access = await _google_access_token()
    metadata: dict[str, Any] = {
        "name": f"{evidence_uuid}-{filename}",
        "appProperties": {"mirrorEvidenceUuid": evidence_uuid, "sha256": sha256},
    }
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    if folder_id:
        metadata["parents"] = [folder_id]
    headers = {"Authorization": f"Bearer {access}"}
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        response = await client.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size,webViewLink,appProperties",
            headers=headers,
            files={
                "metadata": (None, json.dumps(metadata), "application/json; charset=UTF-8"),
                "file": (filename, content, mime_type),
            },
        )
        if response.status_code >= 400:
            raise HTTPException(502, f"Google Drive upload failed with HTTP {response.status_code}")
        created = response.json()
        object_id = str(created.get("id") or "")
        verify = await client.get(
            f"https://www.googleapis.com/drive/v3/files/{quote(object_id)}?fields=id,name,size,webViewLink,appProperties",
            headers=headers,
        )
        if verify.status_code >= 400:
            raise HTTPException(502, "Google Drive readback failed after upload")
        readback = verify.json()
    verified = (
        str(readback.get("id")) == object_id
        and str((readback.get("appProperties") or {}).get("mirrorEvidenceUuid")) == evidence_uuid
        and str((readback.get("appProperties") or {}).get("sha256")) == sha256
    )
    if not verified:
        raise HTTPException(502, "Google Drive upload did not pass mirror readback verification")
    return {
        "provider": "google_drive",
        "provider_object_id": object_id,
        "provider_locator": f"google-drive:{object_id}",
        "web_url": readback.get("webViewLink"),
        "readback_verified": True,
    }


async def _microsoft_upload(evidence_uuid: str, filename: str, mime_type: str, content: bytes, sha256: str) -> dict[str, Any]:
    access = await _microsoft_access_token()
    headers = {"Authorization": f"Bearer {access}"}
    remote_name = f"{evidence_uuid}-{filename}".replace("/", "_")
    base = f"https://graph.microsoft.com/v1.0/me/drive/special/approot:/MIRA/{quote(remote_name)}"
    async with httpx.AsyncClient(timeout=180, follow_redirects=True) as client:
        if len(content) <= 4 * 1024 * 1024:
            response = await client.put(base + ":/content", headers={**headers, "Content-Type": mime_type}, content=content)
            if response.status_code >= 400:
                raise HTTPException(502, f"OneDrive upload failed with HTTP {response.status_code}")
            created = response.json()
        else:
            session_response = await client.post(
                base + ":/createUploadSession",
                headers={**headers, "Content-Type": "application/json"},
                json={"item": {"@microsoft.graph.conflictBehavior": "replace", "name": remote_name}},
            )
            if session_response.status_code >= 400:
                raise HTTPException(502, f"OneDrive upload-session creation failed with HTTP {session_response.status_code}")
            upload_url = str(session_response.json().get("uploadUrl") or "")
            if not upload_url:
                raise HTTPException(502, "OneDrive upload session did not return an upload URL")
            chunk_size = 5 * 1024 * 1024
            created: dict[str, Any] = {}
            for start in range(0, len(content), chunk_size):
                chunk = content[start:start + chunk_size]
                end = start + len(chunk) - 1
                chunk_response = await client.put(
                    upload_url,
                    headers={"Content-Length": str(len(chunk)), "Content-Range": f"bytes {start}-{end}/{len(content)}"},
                    content=chunk,
                )
                if chunk_response.status_code >= 400:
                    raise HTTPException(502, f"OneDrive chunk upload failed with HTTP {chunk_response.status_code}")
                if chunk_response.status_code in {200, 201}:
                    created = chunk_response.json()
        object_id = str(created.get("id") or "")
        if not object_id:
            raise HTTPException(502, "OneDrive upload did not return an item ID")
        verify = await client.get(
            f"https://graph.microsoft.com/v1.0/me/drive/items/{quote(object_id)}?$select=id,name,size,webUrl",
            headers=headers,
        )
        if verify.status_code >= 400:
            raise HTTPException(502, "OneDrive readback failed after upload")
        readback = verify.json()
    verified = str(readback.get("id")) == object_id and int(readback.get("size") or -1) == len(content)
    if not verified:
        raise HTTPException(502, "OneDrive upload did not pass mirror readback verification")
    return {
        "provider": "onedrive",
        "provider_object_id": object_id,
        "provider_locator": f"onedrive:{object_id}",
        "web_url": readback.get("webUrl"),
        "readback_verified": True,
    }


def _store_replication(evidence_uuid: str, sha256: str, result: dict[str, Any]) -> None:
    ensure_schema()
    ts = now_iso()
    with connect() as db:
        db.execute(
            "INSERT INTO evidence_replication(evidence_uuid,provider,provider_object_id,provider_locator,web_url,content_hash,readback_verified,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(evidence_uuid,provider) DO UPDATE SET "
            "provider_object_id=excluded.provider_object_id,provider_locator=excluded.provider_locator,web_url=excluded.web_url,"
            "content_hash=excluded.content_hash,readback_verified=excluded.readback_verified,updated_at=excluded.updated_at",
            (
                evidence_uuid, result["provider"], result["provider_object_id"], result["provider_locator"],
                result.get("web_url"), sha256, 1 if result.get("readback_verified") else 0, ts, ts,
            ),
        )
        db.commit()


def _asset_exists(asset_uuid: str) -> bool:
    with connect() as db:
        return bool(db.execute("SELECT 1 FROM assets WHERE uuid=?", (asset_uuid,)).fetchone())


def _audit(event_type: str, target_uuid: str | None, payload: dict[str, Any]) -> None:
    with connect() as db:
        db.execute(
            "INSERT INTO audit_events(event_uuid,event_type,target_uuid,payload_json,created_at) VALUES(?,?,?,?,?)",
            (os.urandom(16).hex(), event_type, target_uuid, json.dumps(payload, sort_keys=True), now_iso()),
        )
        db.commit()


def register_provider_extensions(app: Any) -> None:
    ensure_schema()

    # Replace the starter local-only evidence POST route with provider-aware ingress.
    app.router.routes[:] = [
        route for route in app.router.routes
        if not (getattr(route, "path", None) == "/v1/evidence" and "POST" in (getattr(route, "methods", set()) or set()))
    ]

    @app.get("/v1/integrations/provider-health")
    async def provider_health() -> dict[str, Any]:
        return {
            "default_provider": DEFAULT_PROVIDER,
            "evidence_provider": selected_evidence_provider(),
            "google_workspace": await google_health(),
            "microsoft_365": await microsoft_health(),
            "apple": {
                "connected": False,
                "provider": "apple_manual",
                "note": "No general iCloud Drive server API is claimed. Apple interoperability remains explicit import/export or a separately verified adapter.",
            },
        }

    @app.get("/v1/evidence/{evidence_uuid}/replication")
    async def evidence_replication(evidence_uuid: str) -> dict[str, Any]:
        with connect() as db:
            rows = [dict(row) for row in db.execute(
                "SELECT provider,provider_object_id,provider_locator,web_url,content_hash,readback_verified,created_at,updated_at "
                "FROM evidence_replication WHERE evidence_uuid=? ORDER BY provider",
                (evidence_uuid,),
            )]
        return {"evidence_uuid": evidence_uuid, "replicas": rows}

    @app.post("/v1/evidence")
    async def provider_aware_evidence(
        request: Request,
        asset_uuid: str = Form(...),
        role: str = Form(default="attachment"),
        media_role: str = Form(default=""),
        file: UploadFile = File(...),
    ) -> dict[str, Any]:
        supplied_api = request.headers.get("X-Mirror-Api-Version", "")
        if supplied_api and supplied_api.split(".", 1)[0] != "1":
            raise HTTPException(426, "client API is incompatible with server API 1.1")
        if not _asset_exists(asset_uuid):
            raise HTTPException(404, "asset not found")
        safe_name = Path(file.filename or "attachment").name
        content = await file.read(MAX_EVIDENCE_BYTES + 1)
        if len(content) > MAX_EVIDENCE_BYTES:
            raise HTTPException(413, f"evidence exceeds configured {MAX_EVIDENCE_BYTES} byte limit")
        evidence_uuid = os.urandom(16).hex()
        digest = hashlib.sha256(content).hexdigest()
        chosen_role = media_role or role or "attachment"
        local_path = EVIDENCE_DIR / f"{evidence_uuid}-{safe_name}"
        local_path.write_bytes(content)
        provider = selected_evidence_provider()
        replication: dict[str, Any] = {
            "provider": "local",
            "provider_object_id": str(local_path),
            "provider_locator": f"local:{local_path.name}",
            "web_url": None,
            "readback_verified": local_path.read_bytes() == content,
        }
        if provider == "google":
            replication = await _google_upload(evidence_uuid, safe_name, file.content_type or "application/octet-stream", content, digest)
        elif provider == "microsoft":
            replication = await _microsoft_upload(evidence_uuid, safe_name, file.content_type or "application/octet-stream", content, digest)
        with connect() as db:
            db.execute(
                "INSERT INTO evidence(uuid,asset_uuid,filename,mime_type,sha256,storage_path,role,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (
                    evidence_uuid, asset_uuid, safe_name, file.content_type or "application/octet-stream",
                    digest, str(local_path), chosen_role, now_iso(),
                ),
            )
            db.commit()
        _store_replication(evidence_uuid, digest, replication)
        _audit(
            "evidence.upload",
            asset_uuid,
            {
                "evidence_uuid": evidence_uuid,
                "filename": safe_name,
                "role": chosen_role,
                "sha256": digest,
                "replication_provider": replication["provider"],
                "provider_readback_verified": replication["readback_verified"],
            },
        )
        return {
            "readback_verified": True,
            "evidence_uuid": evidence_uuid,
            "asset_uuid": asset_uuid,
            "filename": safe_name,
            "mime_type": file.content_type or "application/octet-stream",
            "content_hash": digest,
            "role": chosen_role,
            "replication": replication,
        }
