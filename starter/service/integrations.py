from __future__ import annotations

import ipaddress
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from cryptography.fernet import Fernet
from fastapi import HTTPException, Request


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _catalog() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "integration-catalog.json"
    if not path.is_file():
        path = Path(__file__).resolve().parent.parent / "integration-catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _cipher() -> Fernet:
    raw = os.environ.get("MIRROR_TOKEN_KEY", "").strip()
    if not raw:
        raise HTTPException(503, "MIRROR_TOKEN_KEY is required before integration credentials can be stored")
    try:
        return Fernet(raw.encode("ascii"))
    except Exception as exc:
        raise HTTPException(503, "MIRROR_TOKEN_KEY must be a valid Fernet key") from exc


def _validate_base_url(value: str, mode: str) -> str:
    raw = str(value or "").strip().rstrip("/")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(400, "service URL must be an http(s) URL")
    if parsed.username or parsed.password:
        raise HTTPException(400, "credentials must not be embedded in the service URL")
    if mode == "direct_https" and parsed.scheme != "https":
        raise HTTPException(400, "direct HTTPS enrollment requires https://")
    try:
        address = ipaddress.ip_address(parsed.hostname)
        if address.is_link_local or address.is_multicast or address.is_unspecified:
            raise HTTPException(400, "link-local, multicast, and unspecified service addresses are not allowed")
    except ValueError:
        pass
    if parsed.hostname in {"169.254.169.254", "metadata.google.internal"}:
        raise HTTPException(400, "cloud metadata endpoints cannot be enrolled as integrations")
    return raw


def install_integrations(app: Any, core_module: Any) -> None:
    catalog = _catalog()

    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS integration_instances (
              integration_uuid TEXT PRIMARY KEY,
              service_type TEXT NOT NULL,
              display_name TEXT NOT NULL,
              base_url TEXT,
              connection_mode TEXT NOT NULL,
              encrypted_credentials TEXT,
              requested_capabilities_json TEXT NOT NULL,
              verified_capabilities_json TEXT NOT NULL DEFAULT '[]',
              connection_state TEXT NOT NULL DEFAULT 'configured',
              last_health_json TEXT NOT NULL DEFAULT '{}',
              last_verified_at TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_integrations_service_type ON integration_instances(service_type, connection_state);
            """
        )
        db.commit()

    def read_instance(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result.pop("encrypted_credentials", None)
        for key in ("requested_capabilities_json", "verified_capabilities_json", "last_health_json"):
            result[key.removesuffix("_json")] = json.loads(result.pop(key) or ("{}" if key == "last_health_json" else "[]"))
        return result

    def service_spec(service_type: str) -> dict[str, Any]:
        spec = (catalog.get("services") or {}).get(service_type)
        if not isinstance(spec, dict):
            raise HTTPException(400, f"unsupported integration type: {service_type}")
        if spec.get("status") == "reserved_contract_only":
            raise HTTPException(409, f"{service_type} is reserved for a future adapter and cannot be enrolled yet")
        return spec

    @app.get("/v1/integrations/catalog")
    def get_catalog() -> dict[str, Any]:
        return catalog

    @app.get("/v1/integrations")
    def list_integrations() -> dict[str, Any]:
        with connect() as db:
            rows = db.execute("SELECT * FROM integration_instances ORDER BY display_name, integration_uuid").fetchall()
        return {"integrations": [read_instance(row) for row in rows]}

    @app.post("/v1/integrations/enroll")
    async def enroll(request: Request) -> dict[str, Any]:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(400, "integration enrollment object is required")
        service_type = str(payload.get("service_type") or "").strip()
        spec = service_spec(service_type)
        mode = str(payload.get("connection_mode") or spec.get("default_connection_mode") or "local_bridge").strip()
        if mode not in (catalog.get("connection_modes") or {}):
            raise HTTPException(400, "unsupported connection mode")
        base_url = str(payload.get("base_url") or "").strip()
        if mode != "local_bridge" or base_url:
            base_url = _validate_base_url(base_url, mode)
        requested = payload.get("capabilities") or spec.get("default_enabled_capabilities") or []
        if not isinstance(requested, list):
            raise HTTPException(400, "capabilities must be a list")
        allowed = set(spec.get("capabilities") or [])
        requested = sorted({str(value) for value in requested if str(value) in allowed})
        credentials = payload.get("credentials")
        encrypted = None
        if credentials:
            if not isinstance(credentials, dict):
                raise HTTPException(400, "credentials must be an object")
            encrypted = _cipher().encrypt(json.dumps(credentials, separators=(",", ":"), sort_keys=True).encode()).decode()
        integration_uuid = str(uuid.uuid4())
        now = _now()
        display_name = str(payload.get("display_name") or spec.get("display_name") or service_type).strip()[:160]
        state = "bridge_pairing_required" if mode == "local_bridge" else "configured"
        with connect() as db:
            db.execute(
                "INSERT INTO integration_instances(integration_uuid,service_type,display_name,base_url,connection_mode,encrypted_credentials,requested_capabilities_json,connection_state,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (integration_uuid, service_type, display_name, base_url or None, mode, encrypted, json.dumps(requested), state, now, now),
            )
            db.commit()
            row = db.execute("SELECT * FROM integration_instances WHERE integration_uuid=?", (integration_uuid,)).fetchone()
        return {
            "readback_verified": True,
            "integration": read_instance(row),
            "next_step": "Pair a local MIRA bridge on the same network." if mode == "local_bridge" else "Verify the connection before enabling write capabilities.",
            "credential_storage": "encrypted; secret values are never returned by the API",
        }

    @app.post("/v1/integrations/{integration_uuid}/verify")
    async def verify(integration_uuid: str) -> dict[str, Any]:
        with connect() as db:
            row = db.execute("SELECT * FROM integration_instances WHERE integration_uuid=?", (integration_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "integration not found")
        instance = dict(row)
        spec = service_spec(instance["service_type"])
        if instance["connection_mode"] == "local_bridge":
            return {
                "readback_verified": False,
                "integration_uuid": integration_uuid,
                "connection_state": "bridge_pairing_required",
                "next_step": "Use a paired Windows, Linux, or Android MIRA client on the service network to run the health probe.",
            }
        base_url = _validate_base_url(instance.get("base_url") or "", instance["connection_mode"])
        health_path = str(spec.get("health_path") or "/")
        credentials: dict[str, Any] = {}
        if instance.get("encrypted_credentials"):
            try:
                credentials = json.loads(_cipher().decrypt(instance["encrypted_credentials"].encode()).decode())
            except Exception as exc:
                raise HTTPException(503, "stored integration credentials cannot be decrypted") from exc
        headers = {"Accept": "application/json", "User-Agent": "MIRA-MIRROR-integration-probe"}
        token = credentials.get("token") or credentials.get("api_token")
        api_key = credentials.get("api_key")
        if instance["service_type"] == "paperless_ngx" and token:
            headers["Authorization"] = f"Token {token}"
            headers["Accept"] = "application/json; version=10"
        elif instance["service_type"] == "plex" and token:
            headers["X-Plex-Token"] = str(token)
            headers["Accept"] = "application/json"
        elif token:
            headers["Authorization"] = f"Bearer {token}"
        if api_key:
            headers["X-Api-Key"] = str(api_key)
        url = urljoin(base_url + "/", health_path.lstrip("/"))
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
                response = await client.get(url, headers=headers)
            healthy = 200 <= response.status_code < 400
            health = {"status_code": response.status_code, "url_path": urlparse(url).path, "healthy": healthy}
            verified = list(json.loads(instance["requested_capabilities_json"])) if healthy else []
        except Exception as exc:
            healthy = False
            verified = []
            health = {"healthy": False, "error": type(exc).__name__}
        now = _now()
        with connect() as db:
            db.execute(
                "UPDATE integration_instances SET verified_capabilities_json=?,connection_state=?,last_health_json=?,last_verified_at=?,updated_at=? WHERE integration_uuid=?",
                (json.dumps(verified), "verified" if healthy else "unavailable", json.dumps(health), now, now, integration_uuid),
            )
            db.commit()
            updated = db.execute("SELECT * FROM integration_instances WHERE integration_uuid=?", (integration_uuid,)).fetchone()
        return {"readback_verified": healthy, "integration": read_instance(updated), "health": health}

    @app.patch("/v1/integrations/{integration_uuid}")
    async def update_integration(integration_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        with connect() as db:
            row = db.execute("SELECT * FROM integration_instances WHERE integration_uuid=?", (integration_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "integration not found")
        spec = service_spec(row["service_type"])
        capabilities = payload.get("capabilities")
        requested = json.loads(row["requested_capabilities_json"])
        if capabilities is not None:
            if not isinstance(capabilities, list):
                raise HTTPException(400, "capabilities must be a list")
            allowed = set(spec.get("capabilities") or [])
            requested = sorted({str(value) for value in capabilities if str(value) in allowed})
        state = str(payload.get("connection_state") or row["connection_state"])
        if state not in {"configured", "verified", "disabled", "unavailable", "bridge_pairing_required"}:
            raise HTTPException(400, "unsupported connection state")
        now = _now()
        with connect() as db:
            db.execute(
                "UPDATE integration_instances SET requested_capabilities_json=?,connection_state=?,updated_at=? WHERE integration_uuid=?",
                (json.dumps(requested), state, now, integration_uuid),
            )
            db.commit()
            updated = db.execute("SELECT * FROM integration_instances WHERE integration_uuid=?", (integration_uuid,)).fetchone()
        return {"readback_verified": True, "integration": read_instance(updated)}

    @app.delete("/v1/integrations/{integration_uuid}")
    def disable_integration(integration_uuid: str) -> dict[str, Any]:
        with connect() as db:
            row = db.execute("SELECT 1 FROM integration_instances WHERE integration_uuid=?", (integration_uuid,)).fetchone()
            if not row:
                raise HTTPException(404, "integration not found")
            db.execute("UPDATE integration_instances SET connection_state='disabled',updated_at=? WHERE integration_uuid=?", (_now(), integration_uuid))
            db.commit()
        return {
            "readback_verified": True,
            "integration_uuid": integration_uuid,
            "connection_state": "disabled",
            "external_data_deleted": False,
            "note": "Disabling an integration never deletes the external service or its data.",
        }
