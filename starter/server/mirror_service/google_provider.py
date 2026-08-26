from __future__ import annotations

from dataclasses import dataclass
import io
import json
from typing import Any
from urllib.parse import urlencode

from cryptography.fernet import Fernet
import httpx

from .config import Settings
from .meta import MetaStore

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets"
DRIVE = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"

BASE_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
ENTITY_HEADERS = ["entity_type", "entity_uuid", "parent_uuid", "name", "payload_json", "updated_at", "revision"]


@dataclass
class GoogleSession:
    access_token: str
    refresh_token: str
    expires_in: int
    subject: str
    email: str


class GoogleWorkspace:
    def __init__(self, settings: Settings, meta: MetaStore):
        self.settings = settings
        self.meta = meta
        self._fernet = Fernet(settings.token_encryption_key.encode()) if settings.token_encryption_key else None

    def authorization_url(self, state: str) -> str:
        if not self.settings.google_oauth_ready:
            raise RuntimeError("Google OAuth is not configured")
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": f"{self.settings.public_base_url}/auth/google/callback",
            "response_type": "code",
            "scope": " ".join(BASE_SCOPES),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
            "state": state,
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    def exchange_code(self, code: str) -> GoogleSession:
        response = httpx.post(TOKEN_URL, data={
            "code": code,
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "redirect_uri": f"{self.settings.public_base_url}/auth/google/callback",
            "grant_type": "authorization_code",
        }, timeout=20)
        response.raise_for_status()
        token = response.json()
        access = token["access_token"]
        info = httpx.get(USERINFO_URL, headers={"Authorization": f"Bearer {access}"}, timeout=20)
        info.raise_for_status()
        profile = info.json()
        prior = self._load_tokens()
        refresh = token.get("refresh_token") or prior.get("refresh_token", "")
        session = GoogleSession(
            access_token=access,
            refresh_token=refresh,
            expires_in=int(token.get("expires_in", 3600)),
            subject=str(profile["sub"]),
            email=str(profile.get("email", "")),
        )
        self._save_tokens(session)
        self.meta.put_json("google.profile", {"subject": session.subject, "email": session.email})
        return session

    def _save_tokens(self, session: GoogleSession) -> None:
        if self._fernet is None:
            raise RuntimeError("MIRROR_TOKEN_ENCRYPTION_KEY is required")
        raw = json.dumps({
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_in": session.expires_in,
            "subject": session.subject,
            "email": session.email,
        }).encode()
        self.meta.put_json("google.tokens", {"ciphertext": self._fernet.encrypt(raw).decode()})

    def _load_tokens(self) -> dict[str, Any]:
        row = self.meta.get_json("google.tokens", {})
        if not row:
            return {}
        if self._fernet is None:
            raise RuntimeError("MIRROR_TOKEN_ENCRYPTION_KEY is required")
        return json.loads(self._fernet.decrypt(row["ciphertext"].encode()).decode())

    def access_token(self) -> str:
        token = self._load_tokens()
        refresh = token.get("refresh_token")
        if not refresh:
            raise RuntimeError("Google is not connected")
        response = httpx.post(TOKEN_URL, data={
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "refresh_token": refresh,
            "grant_type": "refresh_token",
        }, timeout=20)
        response.raise_for_status()
        payload = response.json()
        access = payload["access_token"]
        self._save_tokens(GoogleSession(
            access_token=access,
            refresh_token=refresh,
            expires_in=int(payload.get("expires_in", 3600)),
            subject=str(token.get("subject", "")),
            email=str(token.get("email", "")),
        ))
        return access

    def provider_status(self) -> dict[str, Any]:
        profile = self.meta.get_json("google.profile")
        resources = self.meta.get_json("google.resources")
        return {
            "provider": "google",
            "configured": self.settings.google_oauth_ready,
            "connected": bool(profile),
            "profile": profile,
            "provisioned": bool(resources and resources.get("spreadsheet_id") and resources.get("drive_folder_id")),
            "resources": resources or {},
        }

    def provision(self) -> dict[str, str]:
        token = self.access_token()
        headers = {"Authorization": f"Bearer {token}"}
        existing = self.meta.get_json("google.resources", {})
        spreadsheet_id = existing.get("spreadsheet_id")
        folder_id = existing.get("drive_folder_id")
        if not spreadsheet_id:
            response = httpx.post(SHEETS, headers=headers, json={
                "properties": {"title": "mirror Data"},
                "sheets": [{"properties": {"title": "Entities"}}],
            }, timeout=30)
            response.raise_for_status()
            spreadsheet_id = response.json()["spreadsheetId"]
            self._write_values(spreadsheet_id, "Entities!A1:G1", [ENTITY_HEADERS])
        if not folder_id:
            response = httpx.post(DRIVE, headers=headers, params={"fields": "id,name"}, json={
                "name": "mirror Evidence",
                "mimeType": "application/vnd.google-apps.folder",
            }, timeout=30)
            response.raise_for_status()
            folder_id = response.json()["id"]
        resources = {"spreadsheet_id": spreadsheet_id, "drive_folder_id": folder_id}
        self.meta.put_json("google.resources", resources)
        return resources

    def _write_values(self, spreadsheet_id: str, range_name: str, values: list[list[Any]]) -> None:
        token = self.access_token()
        response = httpx.put(
            f"{SHEETS}/{spreadsheet_id}/values/{range_name}",
            params={"valueInputOption": "RAW"},
            headers={"Authorization": f"Bearer {token}"},
            json={"values": values},
            timeout=30,
        )
        response.raise_for_status()

    def list_entities(self) -> list[dict[str, Any]]:
        resources = self.meta.get_json("google.resources", {})
        spreadsheet_id = resources.get("spreadsheet_id")
        if not spreadsheet_id:
            return []
        token = self.access_token()
        response = httpx.get(
            f"{SHEETS}/{spreadsheet_id}/values/Entities!A2:G",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        response.raise_for_status()
        rows = response.json().get("values", [])
        entities = []
        for row in rows:
            padded = list(row) + [""] * (7 - len(row))
            try:
                payload = json.loads(padded[4]) if padded[4] else {}
            except json.JSONDecodeError:
                payload = {}
            entities.append({
                "entity_type": padded[0], "entity_uuid": padded[1], "parent_uuid": padded[2] or None,
                "name": padded[3], "payload": payload, "updated_at": padded[5],
                "revision": int(padded[6] or 0),
            })
        return entities

    def upsert_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        resources = self.meta.get_json("google.resources", {})
        spreadsheet_id = resources.get("spreadsheet_id")
        if not spreadsheet_id:
            raise RuntimeError("Google workspace is not provisioned")
        rows = self.list_entities()
        target = None
        current_revision = 0
        for index, row in enumerate(rows, start=2):
            if row["entity_uuid"] == entity["entity_uuid"]:
                target = index
                current_revision = int(row.get("revision", 0))
                break
        next_revision = current_revision + 1
        values = [[
            entity["entity_type"], entity["entity_uuid"], entity.get("parent_uuid") or "", entity.get("name", ""),
            json.dumps(entity.get("payload", {}), sort_keys=True, separators=(",", ":")),
            entity["updated_at"], next_revision,
        ]]
        if target:
            self._write_values(spreadsheet_id, f"Entities!A{target}:G{target}", values)
        else:
            token = self.access_token()
            response = httpx.post(
                f"{SHEETS}/{spreadsheet_id}/values/Entities!A:G:append",
                params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
                headers={"Authorization": f"Bearer {token}"},
                json={"values": values},
                timeout=30,
            )
            response.raise_for_status()
        result = dict(entity)
        result["revision"] = next_revision
        return result

    def upload_evidence(self, content: bytes, filename: str, mime_type: str) -> dict[str, str]:
        resources = self.meta.get_json("google.resources", {})
        folder_id = resources.get("drive_folder_id")
        if not folder_id:
            raise RuntimeError("Google workspace is not provisioned")
        token = self.access_token()
        metadata = {"name": filename, "parents": [folder_id]}
        files = {
            "metadata": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
            "file": (filename, io.BytesIO(content), mime_type),
        }
        response = httpx.post(
            f"{DRIVE_UPLOAD}?uploadType=multipart&fields=id,name,webViewLink",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def download_evidence(self, provider_id: str) -> tuple[bytes, str]:
        token = self.access_token()
        meta = httpx.get(
            f"{DRIVE}/{provider_id}",
            params={"fields": "mimeType,name"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        meta.raise_for_status()
        payload = meta.json()
        response = httpx.get(
            f"{DRIVE}/{provider_id}",
            params={"alt": "media"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        response.raise_for_status()
        return response.content, str(payload.get("mimeType") or "application/octet-stream")
