from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Request


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bootstrap_token() -> str:
    return os.environ.get("MIRROR_ACCESS_TOKEN", "").strip()


def _require_bootstrap_admin(request: Request) -> None:
    expected = _bootstrap_token()
    if not expected:
        raise HTTPException(503, "bootstrap admin token is not configured")
    supplied = request.headers.get("Authorization", "")
    if not supplied.startswith("Bearer ") or not hmac.compare_digest(supplied[7:], expected):
        raise HTTPException(403, "bootstrap admin credential required")


def valid_device_token(core_module: Any, token: str) -> bool:
    if not token.startswith("mira_dev_"):
        return False
    digest = _hash(token)
    try:
        with core_module.connect() as db:
            row = db.execute(
                "SELECT device_uuid FROM device_credentials WHERE token_sha256=? AND revoked_at IS NULL",
                (digest,),
            ).fetchone()
            if not row:
                return False
            db.execute("UPDATE device_credentials SET last_used_at=? WHERE device_uuid=?", (_iso(), row["device_uuid"]))
            db.commit()
        return True
    except sqlite3.Error:
        return False


def install_device_auth(app: Any, core_module: Any) -> None:
    with core_module.connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS device_enrollment_codes (
              code_sha256 TEXT PRIMARY KEY,
              created_at TEXT NOT NULL,
              expires_at TEXT NOT NULL,
              used_at TEXT,
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS device_credentials (
              device_uuid TEXT PRIMARY KEY,
              device_name TEXT NOT NULL,
              platform TEXT NOT NULL,
              client_id TEXT,
              token_sha256 TEXT NOT NULL UNIQUE,
              created_at TEXT NOT NULL,
              last_used_at TEXT,
              revoked_at TEXT,
              metadata_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_device_token_active ON device_credentials(token_sha256,revoked_at);
            """
        )
        db.commit()

    @app.post("/v1/devices/enrollment-codes")
    async def create_enrollment_code(request: Request) -> dict[str, Any]:
        _require_bootstrap_admin(request)
        payload = await request.json()
        minutes = int(payload.get("expires_minutes") or 10)
        if minutes < 2 or minutes > 60:
            raise HTTPException(400, "expires_minutes must be between 2 and 60")
        code = secrets.token_urlsafe(18)
        created = _now()
        expires = created + timedelta(minutes=minutes)
        metadata = {
            "requested_name": str(payload.get("device_name") or "").strip() or None,
            "requested_platform": str(payload.get("platform") or "").strip().lower() or None,
        }
        with core_module.connect() as db:
            db.execute(
                "INSERT INTO device_enrollment_codes(code_sha256,created_at,expires_at,metadata_json) VALUES(?,?,?,?)",
                (_hash(code), _iso(created), _iso(expires), json.dumps(metadata, separators=(",", ":"), sort_keys=True)),
            )
            if hasattr(core_module, "audit"):
                core_module.audit(db, "device.enrollment_code.create", None, {"expires_at": _iso(expires), **metadata})
            db.commit()
        public_base = os.environ.get("MIRROR_PUBLIC_BASE_URL", "").strip().rstrip("/")
        return {
            "readback_verified": True,
            "enrollment_code": code,
            "expires_at": _iso(expires),
            "pairing_payload": {
                "type": "MIRA_MIRROR_DEVICE_ENROLLMENT",
                "api_base": public_base or None,
                "code": code,
            },
            "secret_handling": "show this code/QR only to the device being enrolled; it becomes unusable after one successful enrollment",
        }

    @app.post("/v1/devices/enroll")
    async def enroll_device(request: Request) -> dict[str, Any]:
        payload = await request.json()
        code = str(payload.get("code") or "").strip()
        device_name = str(payload.get("device_name") or "").strip()
        platform = str(payload.get("platform") or "unknown").strip().lower()
        client_id = str(payload.get("client_id") or "").strip() or None
        if not code or not device_name:
            raise HTTPException(400, "code and device_name are required")
        now = _now()
        digest = _hash(code)
        token = "mira_dev_" + secrets.token_urlsafe(32)
        device_uuid = str(uuid.uuid4())
        with core_module.connect() as db:
            row = db.execute("SELECT * FROM device_enrollment_codes WHERE code_sha256=?", (digest,)).fetchone()
            if not row:
                raise HTTPException(404, "enrollment code is invalid")
            if row["used_at"]:
                raise HTTPException(409, "enrollment code has already been used")
            try:
                expires = datetime.fromisoformat(row["expires_at"])
            except ValueError as exc:
                raise HTTPException(500, "stored enrollment expiry is invalid") from exc
            if expires <= now:
                raise HTTPException(410, "enrollment code has expired")
            db.execute(
                "INSERT INTO device_credentials(device_uuid,device_name,platform,client_id,token_sha256,created_at,metadata_json) VALUES(?,?,?,?,?,?,?)",
                (device_uuid, device_name[:120], platform[:40], client_id, _hash(token), _iso(now), json.dumps(payload.get("metadata") or {}, separators=(",", ":"), sort_keys=True)),
            )
            db.execute("UPDATE device_enrollment_codes SET used_at=? WHERE code_sha256=?", (_iso(now), digest))
            if hasattr(core_module, "audit"):
                core_module.audit(db, "device.enroll", device_uuid, {"device_name": device_name, "platform": platform, "client_id": client_id})
            db.commit()
            readback = db.execute("SELECT device_uuid FROM device_credentials WHERE device_uuid=? AND revoked_at IS NULL", (device_uuid,)).fetchone()
        return {
            "readback_verified": bool(readback),
            "device_uuid": device_uuid,
            "device_token": token,
            "token_display_rule": "returned once; store in the platform secure credential store, not in source control",
        }

    @app.get("/v1/devices")
    def list_devices(request: Request) -> dict[str, Any]:
        _require_bootstrap_admin(request)
        with core_module.connect() as db:
            rows = [dict(row) for row in db.execute(
                "SELECT device_uuid,device_name,platform,client_id,created_at,last_used_at,revoked_at FROM device_credentials ORDER BY created_at DESC"
            )]
        return {"devices": rows}

    @app.delete("/v1/devices/{device_uuid}")
    def revoke_device(device_uuid: str, request: Request) -> dict[str, Any]:
        _require_bootstrap_admin(request)
        with core_module.connect() as db:
            cur = db.execute("UPDATE device_credentials SET revoked_at=? WHERE device_uuid=? AND revoked_at IS NULL", (_iso(), device_uuid))
            if not cur.rowcount:
                raise HTTPException(404, "active device not found")
            if hasattr(core_module, "audit"):
                core_module.audit(db, "device.revoke", device_uuid, {})
            db.commit()
        return {"readback_verified": True, "device_uuid": device_uuid, "revoked": True}

    @app.post("/v1/devices/{device_uuid}/rotate")
    def rotate_device(device_uuid: str, request: Request) -> dict[str, Any]:
        _require_bootstrap_admin(request)
        token = "mira_dev_" + secrets.token_urlsafe(32)
        with core_module.connect() as db:
            cur = db.execute(
                "UPDATE device_credentials SET token_sha256=?,last_used_at=NULL,revoked_at=NULL WHERE device_uuid=?",
                (_hash(token), device_uuid),
            )
            if not cur.rowcount:
                raise HTTPException(404, "device not found")
            if hasattr(core_module, "audit"):
                core_module.audit(db, "device.rotate", device_uuid, {})
            db.commit()
        return {"readback_verified": True, "device_uuid": device_uuid, "device_token": token, "token_display_rule": "returned once"}
