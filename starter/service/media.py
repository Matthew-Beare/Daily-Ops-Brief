from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_media(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS media_items (
              media_uuid TEXT PRIMARY KEY,
              media_type TEXT NOT NULL,
              title TEXT NOT NULL,
              year INTEGER,
              metadata_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS media_identifiers (
              namespace TEXT NOT NULL,
              value TEXT NOT NULL,
              media_uuid TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY(namespace,value),
              FOREIGN KEY(media_uuid) REFERENCES media_items(media_uuid)
            );
            CREATE TABLE IF NOT EXISTS media_provider_bindings (
              media_uuid TEXT NOT NULL,
              integration_uuid TEXT NOT NULL,
              provider_item_id TEXT NOT NULL,
              provider_json TEXT NOT NULL DEFAULT '{}',
              last_verified_at TEXT,
              PRIMARY KEY(media_uuid,integration_uuid),
              FOREIGN KEY(media_uuid) REFERENCES media_items(media_uuid)
            );
            CREATE TABLE IF NOT EXISTS media_actions (
              action_uuid TEXT PRIMARY KEY,
              media_uuid TEXT,
              integration_uuid TEXT NOT NULL,
              capability TEXT NOT NULL,
              action_type TEXT NOT NULL,
              target TEXT,
              payload_json TEXT NOT NULL DEFAULT '{}',
              state TEXT NOT NULL DEFAULT 'pending',
              result_json TEXT NOT NULL DEFAULT '{}',
              readback_verified INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              completed_at TEXT,
              FOREIGN KEY(media_uuid) REFERENCES media_items(media_uuid)
            );
            """
        )
        db.commit()

    def read_media(db: sqlite3.Connection, media_uuid: str) -> dict[str, Any]:
        row = db.execute("SELECT * FROM media_items WHERE media_uuid=?", (media_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "media item not found")
        result = dict(row)
        result["metadata"] = json.loads(result.pop("metadata_json") or "{}")
        result["identifiers"] = [dict(item) for item in db.execute("SELECT namespace,value,created_at FROM media_identifiers WHERE media_uuid=? ORDER BY namespace,value", (media_uuid,))]
        result["provider_bindings"] = [dict(item) for item in db.execute("SELECT * FROM media_provider_bindings WHERE media_uuid=?", (media_uuid,))]
        return result

    @app.get("/v1/media")
    def list_media(q: str = "", media_type: str = "") -> dict[str, Any]:
        where = ["1=1"]
        values: list[Any] = []
        if q:
            where.append("title LIKE ?")
            values.append(f"%{q}%")
        if media_type:
            where.append("media_type=?")
            values.append(media_type)
        with connect() as db:
            rows = db.execute(f"SELECT media_uuid FROM media_items WHERE {' AND '.join(where)} ORDER BY title,year", values).fetchall()
            return {"media": [read_media(db, row["media_uuid"]) for row in rows]}

    @app.post("/v1/media")
    async def create_media(request: Request) -> dict[str, Any]:
        payload = await request.json()
        media_type = str(payload.get("media_type") or "").strip().lower()
        if media_type not in {"movie", "series", "episode", "music", "audiobook", "other"}:
            raise HTTPException(400, "unsupported media_type")
        title = str(payload.get("title") or "").strip()
        if not title:
            raise HTTPException(400, "title is required")
        media_uuid = str(payload.get("media_uuid") or uuid.uuid4())
        now = _now()
        with connect() as db:
            db.execute(
                "INSERT INTO media_items(media_uuid,media_type,title,year,metadata_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (media_uuid, media_type, title[:300], int(payload["year"]) if payload.get("year") else None, json.dumps(payload.get("metadata") or {}, sort_keys=True), now, now),
            )
            for identifier in payload.get("identifiers") or []:
                if not isinstance(identifier, dict):
                    continue
                namespace = str(identifier.get("namespace") or "").strip().lower()
                value = str(identifier.get("value") or "").strip()
                if namespace and value:
                    db.execute("INSERT INTO media_identifiers(namespace,value,media_uuid,created_at) VALUES(?,?,?,?)", (namespace, value, media_uuid, now))
            db.commit()
            result = read_media(db, media_uuid)
        return {"readback_verified": True, "media": result}

    @app.post("/v1/media/{media_uuid}/actions")
    async def queue_media_action(media_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        integration_uuid = str(payload.get("integration_uuid") or "").strip()
        action_type = str(payload.get("action_type") or "").strip().lower()
        if action_type not in {"play", "request", "refresh", "scan"}:
            raise HTTPException(400, "unsupported media action")
        capability = {
            "play": "media.playback.control",
            "request": "media.request",
            "refresh": "media.library.read",
            "scan": "media.library.read",
        }[action_type]
        with connect() as db:
            read_media(db, media_uuid)
            integration = db.execute("SELECT * FROM integration_instances WHERE integration_uuid=? AND connection_state!='disabled'", (integration_uuid,)).fetchone()
            if not integration:
                raise HTTPException(404, "integration not found")
            requested = set(json.loads(integration["requested_capabilities_json"] or "[]"))
            service_type = integration["service_type"]
            if action_type == "request":
                acceptable = {"media.series.request", "media.movies.request"}
                matched = requested & acceptable
                if not matched:
                    raise HTTPException(403, "this integration is not allowed to request media")
                capability = sorted(matched)[0]
            elif capability not in requested:
                raise HTTPException(403, f"integration does not have {capability} capability")
            action_uuid = str(uuid.uuid4())
            now = _now()
            db.execute(
                "INSERT INTO media_actions(action_uuid,media_uuid,integration_uuid,capability,action_type,target,payload_json,state,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (action_uuid, media_uuid, integration_uuid, capability, action_type, str(payload.get("target") or "") or None, json.dumps(payload.get("payload") or {}, sort_keys=True), "pending", now),
            )
            db.commit()
        return {
            "readback_verified": True,
            "action_uuid": action_uuid,
            "state": "pending",
            "service_type": service_type,
            "next_step": "Execute through the verified direct adapter or an enrolled local bridge, then record provider readback before marking complete.",
        }

    @app.get("/v1/media/actions")
    def list_media_actions(state: str = "pending") -> dict[str, Any]:
        with connect() as db:
            rows = db.execute("SELECT * FROM media_actions WHERE state=? ORDER BY created_at", (state,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json") or "{}")
            item["result"] = json.loads(item.pop("result_json") or "{}")
            item["readback_verified"] = bool(item["readback_verified"])
            result.append(item)
        return {"actions": result}

    @app.post("/v1/media/actions/{action_uuid}/complete")
    async def complete_media_action(action_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        verified = bool(payload.get("readback_verified"))
        if not verified:
            raise HTTPException(409, "media action cannot be marked complete without provider readback verification")
        with connect() as db:
            row = db.execute("SELECT * FROM media_actions WHERE action_uuid=?", (action_uuid,)).fetchone()
            if not row:
                raise HTTPException(404, "media action not found")
            db.execute(
                "UPDATE media_actions SET state='complete',result_json=?,readback_verified=1,completed_at=? WHERE action_uuid=?",
                (json.dumps(payload.get("result") or {}, sort_keys=True), _now(), action_uuid),
            )
            db.commit()
        return {"readback_verified": True, "action_uuid": action_uuid, "state": "complete"}
