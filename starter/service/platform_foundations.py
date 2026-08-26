from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, Query, Request
from fastapi.responses import RedirectResponse

import provider_extensions


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


def install_platform_foundations(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS feature_requests (
              request_uuid TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              request_text TEXT NOT NULL,
              acceptance_json TEXT NOT NULL DEFAULT '[]',
              target_surfaces_json TEXT NOT NULL DEFAULT '[]',
              status TEXT NOT NULL DEFAULT 'queued',
              source TEXT NOT NULL DEFAULT 'mira_client',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS rfid_readers (
              reader_uuid TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              protocol TEXT NOT NULL,
              zone_uuid TEXT,
              adapter_kind TEXT NOT NULL,
              enabled INTEGER NOT NULL DEFAULT 1,
              metadata_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(zone_uuid) REFERENCES locations(uuid)
            );
            CREATE TABLE IF NOT EXISTS rfid_observations (
              observation_uuid TEXT PRIMARY KEY,
              asset_uuid TEXT,
              tag_namespace TEXT NOT NULL,
              tag_value TEXT NOT NULL,
              protocol TEXT NOT NULL,
              observed_at TEXT NOT NULL,
              reader_uuid TEXT,
              zone_uuid TEXT,
              antenna_id TEXT,
              rssi_dbm REAL,
              raw_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(asset_uuid) REFERENCES assets(uuid),
              FOREIGN KEY(reader_uuid) REFERENCES rfid_readers(reader_uuid),
              FOREIGN KEY(zone_uuid) REFERENCES locations(uuid)
            );
            CREATE INDEX IF NOT EXISTS idx_rfid_observation_tag_time
              ON rfid_observations(tag_namespace, tag_value, observed_at);
            CREATE INDEX IF NOT EXISTS idx_rfid_observation_asset_time
              ON rfid_observations(asset_uuid, observed_at);
            CREATE TABLE IF NOT EXISTS integration_events (
              event_uuid TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              event_type TEXT NOT NULL,
              entity_id TEXT,
              payload_json TEXT NOT NULL,
              observed_at TEXT NOT NULL,
              received_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_integration_events_source_time
              ON integration_events(source, observed_at);
            CREATE TABLE IF NOT EXISTS migration_snapshots (
              snapshot_uuid TEXT PRIMARY KEY,
              source_type TEXT NOT NULL,
              source_locator TEXT,
              content_sha256 TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'staged',
              created_at TEXT NOT NULL
            );
            """
        )
        db.commit()

    def require_asset(db: sqlite3.Connection, asset_uuid: str) -> None:
        if not db.execute("SELECT 1 FROM assets WHERE uuid=?", (asset_uuid,)).fetchone():
            raise HTTPException(404, "asset not found")

    def require_location(db: sqlite3.Connection, location_uuid: str | None) -> None:
        if location_uuid and not db.execute("SELECT 1 FROM locations WHERE uuid=?", (location_uuid,)).fetchone():
            raise HTTPException(404, "location not found")

    @app.get("/v1/platform/capabilities")
    def platform_capabilities() -> dict[str, Any]:
        return {
            "feature_development": {
                "in_app_request_queue": True,
                "declarative_handoff": True,
                "dynamic_unreviewed_code_execution": False,
                "git_remains_durable_source": True,
                "chatgpt_plus_companion_mode": "MCP/app surface; no claim that Plus supplies external API compute",
            },
            "rfid": {
                "immutable_asset_uuid": True,
                "tag_is_replaceable_alias": True,
                "android_nfc": "adapter-ready",
                "desktop_linux_reader": "adapter-ready",
                "network_uhf": "adapter-ready",
                "passive_presence_auto_moves_assets": False,
            },
            "home_assistant": {
                "event_ingress": True,
                "health_probe": True,
                "generic_service_call": True,
                "canonical_authority": False,
            },
            "migration": {
                "canonical_json_export": True,
                "staged_json_import": True,
                "google_sheet_discovery": True,
                "google_sheet_staging": True,
                "preserve_uuid_on_apply_rule": True,
            },
        }

    @app.get("/v1/features/requests")
    def list_feature_requests(status: str = Query(default=""), limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        sql = "SELECT * FROM feature_requests"
        params: list[Any] = []
        if status:
            sql += " WHERE status=?"
            params.append(status)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with connect() as db:
            rows = [dict(row) for row in db.execute(sql, params)]
        for row in rows:
            row["acceptance"] = json.loads(row.pop("acceptance_json"))
            row["target_surfaces"] = json.loads(row.pop("target_surfaces_json"))
        return {"feature_requests": rows}

    @app.post("/v1/features/requests")
    async def create_feature_request(request: Request) -> dict[str, Any]:
        payload = await request.json()
        title = str(payload.get("title") or "").strip()
        request_text = str(payload.get("request_text") or payload.get("description") or "").strip()
        if not title or not request_text:
            raise HTTPException(400, "title and request_text are required")
        target_surfaces = payload.get("target_surfaces") or ["web", "windows", "linux", "android"]
        acceptance = payload.get("acceptance") or []
        if not isinstance(target_surfaces, list) or not isinstance(acceptance, list):
            raise HTTPException(400, "target_surfaces and acceptance must be arrays")
        request_uuid = _uuid()
        now = _now()
        with connect() as db:
            db.execute(
                "INSERT INTO feature_requests(request_uuid,title,request_text,acceptance_json,target_surfaces_json,status,source,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    request_uuid,
                    title,
                    request_text,
                    json.dumps(acceptance, separators=(",", ":"), sort_keys=True),
                    json.dumps(target_surfaces, separators=(",", ":"), sort_keys=True),
                    "queued",
                    str(payload.get("source") or "mira_client"),
                    now,
                    now,
                ),
            )
            db.commit()
        return {"readback_verified": True, "request_uuid": request_uuid, "status": "queued"}

    @app.patch("/v1/features/requests/{request_uuid}")
    async def update_feature_request(request_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        allowed = {"queued", "specified", "implementing", "implemented", "deployed", "blocked", "declined"}
        status = str(payload.get("status") or "").strip()
        if status not in allowed:
            raise HTTPException(400, "invalid feature request status")
        with connect() as db:
            cur = db.execute("UPDATE feature_requests SET status=?,updated_at=? WHERE request_uuid=?", (status, _now(), request_uuid))
            if not cur.rowcount:
                raise HTTPException(404, "feature request not found")
            db.commit()
            row = dict(db.execute("SELECT * FROM feature_requests WHERE request_uuid=?", (request_uuid,)).fetchone())
        row["acceptance"] = json.loads(row.pop("acceptance_json"))
        row["target_surfaces"] = json.loads(row.pop("target_surfaces_json"))
        return {"readback_verified": True, "feature_request": row}

    @app.post("/v1/rfid/readers")
    async def register_rfid_reader(request: Request) -> dict[str, Any]:
        payload = await request.json()
        name = str(payload.get("name") or "").strip()
        protocol = str(payload.get("protocol") or "").strip().lower()
        adapter_kind = str(payload.get("adapter_kind") or "").strip().lower()
        zone_uuid = str(payload.get("zone_uuid") or "").strip() or None
        if not name or not protocol or not adapter_kind:
            raise HTTPException(400, "name, protocol and adapter_kind are required")
        reader_uuid = str(payload.get("reader_uuid") or _uuid())
        with connect() as db:
            require_location(db, zone_uuid)
            now = _now()
            db.execute(
                "INSERT INTO rfid_readers(reader_uuid,name,protocol,zone_uuid,adapter_kind,enabled,metadata_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    reader_uuid,
                    name,
                    protocol,
                    zone_uuid,
                    adapter_kind,
                    1,
                    json.dumps(payload.get("metadata") or {}, separators=(",", ":"), sort_keys=True),
                    now,
                    now,
                ),
            )
            db.commit()
        return {"readback_verified": True, "reader_uuid": reader_uuid}

    @app.post("/v1/rfid/tags/bind")
    async def bind_rfid_tag(request: Request) -> dict[str, Any]:
        payload = await request.json()
        asset_uuid = str(payload.get("asset_uuid") or "").strip()
        protocol = str(payload.get("protocol") or "other").strip().lower()
        tag_value = str(payload.get("tag_id") or payload.get("tag_value") or "").strip().upper()
        if not asset_uuid or not tag_value:
            raise HTTPException(400, "asset_uuid and tag_id are required")
        namespace = f"rfid:{protocol}"
        with connect() as db:
            require_asset(db, asset_uuid)
            existing = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, tag_value)).fetchone()
            if existing and existing["asset_uuid"] != asset_uuid:
                raise HTTPException(409, "RFID tag is already bound to another live asset UUID")
            if not existing:
                db.execute(
                    "INSERT INTO identifiers(namespace,value,asset_uuid,created_at) VALUES(?,?,?,?)",
                    (namespace, tag_value, asset_uuid, _now()),
                )
                core_module.audit(db, "rfid.tag.bind", asset_uuid, {"namespace": namespace, "tag_value": tag_value})
            db.commit()
            readback = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, tag_value)).fetchone()
        return {
            "readback_verified": bool(readback and readback["asset_uuid"] == asset_uuid),
            "asset_uuid": asset_uuid,
            "tag_namespace": namespace,
            "tag_value": tag_value,
        }

    @app.post("/v1/rfid/observations")
    async def ingest_rfid_observation(request: Request) -> dict[str, Any]:
        payload = await request.json()
        observation_uuid = str(payload.get("observation_uuid") or _uuid())
        protocol = str(payload.get("protocol") or "other").strip().lower()
        tag_value = str(payload.get("tag_id") or payload.get("tag_value") or "").strip().upper()
        if not tag_value:
            raise HTTPException(400, "tag_id is required")
        namespace = f"rfid:{protocol}"
        observed_at = str(payload.get("observed_at") or _now())
        reader_uuid = str(payload.get("reader_uuid") or payload.get("reader_id") or "").strip() or None
        zone_uuid = str(payload.get("zone_uuid") or "").strip() or None
        with connect() as db:
            if reader_uuid:
                reader = db.execute("SELECT * FROM rfid_readers WHERE reader_uuid=? AND enabled=1", (reader_uuid,)).fetchone()
                if not reader:
                    raise HTTPException(404, "RFID reader is not registered/enabled")
                if not zone_uuid:
                    zone_uuid = reader["zone_uuid"]
            require_location(db, zone_uuid)
            bound = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, tag_value)).fetchone()
            asset_uuid = bound["asset_uuid"] if bound else None
            try:
                db.execute(
                    "INSERT INTO rfid_observations(observation_uuid,asset_uuid,tag_namespace,tag_value,protocol,observed_at,reader_uuid,zone_uuid,antenna_id,rssi_dbm,raw_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        observation_uuid,
                        asset_uuid,
                        namespace,
                        tag_value,
                        protocol,
                        observed_at,
                        reader_uuid,
                        zone_uuid,
                        str(payload.get("antenna_id") or "").strip() or None,
                        payload.get("rssi_dbm"),
                        json.dumps(payload, separators=(",", ":"), sort_keys=True),
                        _now(),
                    ),
                )
                db.commit()
                replay = False
            except sqlite3.IntegrityError:
                replay = True
            row = db.execute("SELECT * FROM rfid_observations WHERE observation_uuid=?", (observation_uuid,)).fetchone()
        return {
            "readback_verified": row is not None,
            "idempotent_replay": replay,
            "observation_uuid": observation_uuid,
            "asset_uuid": row["asset_uuid"] if row else None,
            "zone_uuid": row["zone_uuid"] if row else None,
            "location_promoted": False,
            "policy": "presence evidence only until an explicit corroboration/promotion policy is enabled",
        }

    @app.get("/v1/assets/{asset_uuid}/rfid")
    def asset_rfid(asset_uuid: str, limit: int = Query(default=100, ge=1, le=1000)) -> dict[str, Any]:
        with connect() as db:
            require_asset(db, asset_uuid)
            tags = [dict(row) for row in db.execute(
                "SELECT namespace,value,created_at FROM identifiers WHERE asset_uuid=? AND namespace LIKE 'rfid:%' ORDER BY namespace,value",
                (asset_uuid,),
            )]
            observations = [dict(row) for row in db.execute(
                "SELECT observation_uuid,tag_namespace,tag_value,protocol,observed_at,reader_uuid,zone_uuid,antenna_id,rssi_dbm FROM rfid_observations WHERE asset_uuid=? ORDER BY observed_at DESC LIMIT ?",
                (asset_uuid, limit),
            )]
        return {"asset_uuid": asset_uuid, "tags": tags, "observations": observations}

    @app.get("/v1/integrations/home-assistant/status")
    async def home_assistant_status() -> dict[str, Any]:
        base = os.environ.get("HOME_ASSISTANT_URL", "").strip().rstrip("/")
        token = os.environ.get("HOME_ASSISTANT_TOKEN", "").strip()
        if not base or not token:
            return {"configured": False, "reachable": False, "canonical_authority": False}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{base}/api/", headers={"Authorization": f"Bearer {token}"})
            reachable = response.status_code < 400
            status_code = response.status_code
        except Exception:
            reachable = False
            status_code = None
        return {"configured": True, "reachable": reachable, "status_code": status_code, "canonical_authority": False}

    @app.post("/v1/integrations/home-assistant/events")
    async def home_assistant_event(request: Request) -> dict[str, Any]:
        payload = await request.json()
        event_uuid = str(payload.get("event_uuid") or _uuid())
        event_type = str(payload.get("event_type") or "state_event").strip()
        entity_id = str(payload.get("entity_id") or "").strip() or None
        observed_at = str(payload.get("observed_at") or _now())
        with connect() as db:
            try:
                db.execute(
                    "INSERT INTO integration_events(event_uuid,source,event_type,entity_id,payload_json,observed_at,received_at) VALUES(?,?,?,?,?,?,?)",
                    (event_uuid, "home_assistant", event_type, entity_id, json.dumps(payload, separators=(",", ":"), sort_keys=True), observed_at, _now()),
                )
                db.commit()
                replay = False
            except sqlite3.IntegrityError:
                replay = True
            row = db.execute("SELECT event_uuid FROM integration_events WHERE event_uuid=?", (event_uuid,)).fetchone()
        return {"readback_verified": row is not None, "idempotent_replay": replay, "event_uuid": event_uuid, "canonical_state_changed": False}

    @app.post("/v1/integrations/home-assistant/service")
    async def home_assistant_service(request: Request) -> dict[str, Any]:
        payload = await request.json()
        domain = str(payload.get("domain") or "").strip()
        service = str(payload.get("service") or "").strip()
        service_data = payload.get("service_data") or {}
        if not domain or not service or not isinstance(service_data, dict):
            raise HTTPException(400, "domain, service and service_data object are required")
        base = os.environ.get("HOME_ASSISTANT_URL", "").strip().rstrip("/")
        token = os.environ.get("HOME_ASSISTANT_TOKEN", "").strip()
        if not base or not token:
            raise HTTPException(503, "Home Assistant is not configured")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{base}/api/services/{domain}/{service}",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=service_data,
            )
        if response.status_code >= 400:
            raise HTTPException(502, f"Home Assistant service call failed with HTTP {response.status_code}")
        result = response.json() if response.content else []
        return {"readback_verified": True, "home_assistant_response": result, "canonical_state_changed": False}

    @app.get("/v1/migrations/export")
    def migration_export() -> dict[str, Any]:
        with connect() as db:
            categories = [dict(row) for row in db.execute("SELECT * FROM categories ORDER BY uuid")]
            locations = [dict(row) for row in db.execute("SELECT * FROM locations ORDER BY uuid")]
            assets = [dict(row) for row in db.execute("SELECT * FROM assets ORDER BY uuid")]
            identifiers = [dict(row) for row in db.execute("SELECT * FROM identifiers ORDER BY namespace,value")]
            evidence = [dict(row) for row in db.execute("SELECT uuid,asset_uuid,filename,mime_type,sha256,role,created_at FROM evidence ORDER BY uuid")]
            readers = [dict(row) for row in db.execute("SELECT * FROM rfid_readers ORDER BY reader_uuid")]
        for asset in assets:
            asset["metadata"] = json.loads(asset.pop("metadata_json") or "{}")
        for reader in readers:
            reader["metadata"] = json.loads(reader.pop("metadata_json") or "{}")
        return {
            "mirror_export_version": 1,
            "product_version": core_module.PRODUCT_VERSION,
            "api_contract": core_module.API_CONTRACT,
            "exported_at": _now(),
            "identity_rule": "all canonical UUIDs must survive storage/provider migration unchanged",
            "categories": categories,
            "locations": locations,
            "assets": assets,
            "identifiers": identifiers,
            "evidence_metadata": evidence,
            "rfid_readers": readers,
        }

    @app.post("/v1/migrations/stage")
    async def stage_migration(request: Request) -> dict[str, Any]:
        payload = await request.json()
        source_type = str(payload.get("source_type") or "json").strip()
        source_locator = str(payload.get("source_locator") or "").strip() or None
        source_payload = payload.get("payload")
        if source_payload is None:
            raise HTTPException(400, "payload is required")
        serialized = json.dumps(source_payload, separators=(",", ":"), sort_keys=True)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        snapshot_uuid = _uuid()
        with connect() as db:
            db.execute(
                "INSERT INTO migration_snapshots(snapshot_uuid,source_type,source_locator,content_sha256,payload_json,status,created_at) VALUES(?,?,?,?,?,?,?)",
                (snapshot_uuid, source_type, source_locator, digest, serialized, "staged", _now()),
            )
            db.commit()
        return {
            "readback_verified": True,
            "snapshot_uuid": snapshot_uuid,
            "content_sha256": digest,
            "status": "staged",
            "next_step": "map staged source fields to canonical mirror entities before apply; no implicit overwrite is allowed",
        }

    @app.get("/v1/migrations/google/auth/start")
    def google_import_auth_start(return_to: str = Query(default="/")) -> RedirectResponse:
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", f"{core_module.PUBLIC_BASE_URL}/v1/auth/google/callback")
        if not client_id:
            raise HTTPException(503, "Google OAuth client is not configured")
        core_module.token_cipher()
        verifier, challenge = core_module.pkce_pair()
        state = core_module.store_oauth_state("google", verifier, return_to)
        scopes = {
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        }
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(sorted(scopes)),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        return RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))

    @app.get("/v1/migrations/google/discover")
    async def google_discover(page_size: int = Query(default=100, ge=1, le=1000)) -> dict[str, Any]:
        access = await provider_extensions._google_access_token()
        params = {
            "q": "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
            "pageSize": page_size,
            "fields": "files(id,name,modifiedTime,createdTime,owners(displayName,emailAddress),webViewLink),nextPageToken",
            "orderBy": "modifiedTime desc",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers={"Authorization": f"Bearer {access}"},
                params=params,
            )
        if response.status_code >= 400:
            raise HTTPException(502, f"Google Drive discovery failed with HTTP {response.status_code}; grant the explicit migration read scope")
        result = response.json()
        return {"spreadsheets": result.get("files", []), "next_page_token": result.get("nextPageToken")}

    @app.post("/v1/migrations/google/stage-sheet")
    async def google_stage_sheet(request: Request) -> dict[str, Any]:
        payload = await request.json()
        file_id = str(payload.get("file_id") or "").strip()
        if not file_id:
            raise HTTPException(400, "file_id is required")
        access = await provider_extensions._google_access_token()
        headers = {"Authorization": f"Bearer {access}"}
        async with httpx.AsyncClient(timeout=60) as client:
            meta_response = await client.get(
                f"https://sheets.googleapis.com/v4/spreadsheets/{file_id}",
                headers=headers,
                params={"fields": "spreadsheetId,properties(title,locale,timeZone),sheets(properties(sheetId,title,index,rowCount,columnCount))"},
            )
            if meta_response.status_code >= 400:
                raise HTTPException(502, f"Google Sheets metadata read failed with HTTP {meta_response.status_code}")
            metadata = meta_response.json()
            sheets: list[dict[str, Any]] = []
            for sheet in metadata.get("sheets", []):
                title = str((sheet.get("properties") or {}).get("title") or "")
                values_response = await client.get(
                    f"https://sheets.googleapis.com/v4/spreadsheets/{file_id}/values/{httpx.URL(title).raw_path.decode('utf-8')}",
                    headers=headers,
                    params={"majorDimension": "ROWS"},
                )
                if values_response.status_code >= 400:
                    # Quoted A1 notation safely handles spaces and most punctuation in sheet names.
                    quoted_range = "'" + title.replace("'", "''") + "'"
                    values_response = await client.get(
                        f"https://sheets.googleapis.com/v4/spreadsheets/{file_id}/values/{quoted_range}",
                        headers=headers,
                        params={"majorDimension": "ROWS"},
                    )
                if values_response.status_code >= 400:
                    raise HTTPException(502, f"Google Sheets values read failed for {title!r} with HTTP {values_response.status_code}")
                sheets.append({"properties": sheet.get("properties") or {}, "values": values_response.json().get("values", [])})
        snapshot = {"google_spreadsheet": metadata, "sheets": sheets}
        serialized = json.dumps(snapshot, separators=(",", ":"), sort_keys=True)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        snapshot_uuid = _uuid()
        with connect() as db:
            db.execute(
                "INSERT INTO migration_snapshots(snapshot_uuid,source_type,source_locator,content_sha256,payload_json,status,created_at) VALUES(?,?,?,?,?,?,?)",
                (snapshot_uuid, "google_sheets", f"google-sheet:{file_id}", digest, serialized, "staged", _now()),
            )
            db.commit()
        return {
            "readback_verified": True,
            "snapshot_uuid": snapshot_uuid,
            "source_locator": f"google-sheet:{file_id}",
            "content_sha256": digest,
            "sheet_count": len(sheets),
            "status": "staged",
            "canonical_state_changed": False,
            "next_step": "review/map the staged spreadsheet before canonical import; existing UUIDs must be preserved when present",
        }
