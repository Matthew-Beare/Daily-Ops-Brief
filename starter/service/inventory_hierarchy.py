from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Query, Request


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")


def install_inventory_hierarchy(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS container_location_links (
              container_asset_uuid TEXT PRIMARY KEY,
              container_location_uuid TEXT NOT NULL UNIQUE,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(container_asset_uuid) REFERENCES assets(uuid),
              FOREIGN KEY(container_location_uuid) REFERENCES locations(uuid)
            );
            CREATE TRIGGER IF NOT EXISTS prevent_container_self_location
            BEFORE UPDATE OF location_uuid ON assets
            WHEN NEW.location_uuid = (
              SELECT container_location_uuid
                FROM container_location_links
               WHERE container_asset_uuid=NEW.uuid
            )
            BEGIN
              SELECT RAISE(ABORT, 'container asset cannot be located inside its own container location');
            END;
            CREATE TRIGGER IF NOT EXISTS container_location_follows_asset
            AFTER UPDATE OF location_uuid ON assets
            WHEN EXISTS (
              SELECT 1 FROM container_location_links WHERE container_asset_uuid=NEW.uuid
            )
            BEGIN
              UPDATE locations
                 SET parent_uuid=NEW.location_uuid,
                     updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
               WHERE uuid=(
                 SELECT container_location_uuid
                   FROM container_location_links
                  WHERE container_asset_uuid=NEW.uuid
               );
              UPDATE container_location_links
                 SET updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
               WHERE container_asset_uuid=NEW.uuid;
            END;
            """
        )
        db.commit()

    def require_asset(db: sqlite3.Connection, asset_uuid: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM assets WHERE uuid=?", (asset_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "asset not found")
        return row

    def require_location(db: sqlite3.Connection, location_uuid: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM locations WHERE uuid=?", (location_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "location not found")
        return row

    def location_path(db: sqlite3.Connection, location_uuid: str | None) -> list[dict[str, Any]]:
        if not location_uuid:
            return []
        chain: list[dict[str, Any]] = []
        visited: set[str] = set()
        current = location_uuid
        while current:
            if current in visited:
                raise HTTPException(409, "location hierarchy contains a cycle")
            visited.add(current)
            row = db.execute("SELECT uuid,name,parent_uuid,location_type FROM locations WHERE uuid=?", (current,)).fetchone()
            if not row:
                break
            item = dict(row)
            holder = db.execute(
                "SELECT container_asset_uuid FROM container_location_links WHERE container_location_uuid=?",
                (current,),
            ).fetchone()
            item["container_asset_uuid"] = holder["container_asset_uuid"] if holder else None
            chain.append(item)
            current = row["parent_uuid"]
        chain.reverse()
        return chain

    def bind_identifier(db: sqlite3.Connection, asset_uuid: str, namespace: str, value: str, source: str) -> dict[str, Any]:
        namespace = namespace.strip().lower()
        value = value.strip()
        if not namespace or not value:
            raise HTTPException(400, "namespace and value are required")
        existing = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, value)).fetchone()
        if existing and existing["asset_uuid"] != asset_uuid:
            raise HTTPException(409, f"{namespace} value is already bound to another live asset")
        if not existing:
            db.execute("INSERT INTO identifiers(namespace,value,asset_uuid,created_at) VALUES(?,?,?,?)", (namespace, value, asset_uuid, _now()))
            if hasattr(core_module, "audit"):
                core_module.audit(db, "inventory.identifier.assign", asset_uuid, {"namespace": namespace, "value": value, "source": source})
        return {"asset_uuid": asset_uuid, "namespace": namespace, "value": value}

    @app.post("/v1/assets/{asset_uuid}/serials")
    async def bind_serial(asset_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        serial = str(payload.get("serial") or payload.get("value") or "").strip()
        manufacturer = str(payload.get("manufacturer") or "").strip()
        if not serial:
            raise HTTPException(400, "serial is required")
        namespace = f"serial:{_slug(manufacturer)}" if manufacturer else "serial"
        with connect() as db:
            require_asset(db, asset_uuid)
            result = bind_identifier(db, asset_uuid, namespace, serial, "serial_entry")
            db.commit()
            readback = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, serial)).fetchone()
        return {"readback_verified": bool(readback and readback["asset_uuid"] == asset_uuid), **result}

    @app.post("/v1/assets/{asset_uuid}/identifiers")
    async def bind_any_identifier(asset_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        namespace = str(payload.get("namespace") or "").strip()
        value = str(payload.get("value") or "").strip()
        with connect() as db:
            require_asset(db, asset_uuid)
            result = bind_identifier(db, asset_uuid, namespace, value, str(payload.get("source") or "manual"))
            db.commit()
            readback = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace.lower(), value)).fetchone()
        return {"readback_verified": bool(readback and readback["asset_uuid"] == asset_uuid), **result}

    @app.get("/v1/identifiers/resolve")
    def resolve_identifier(value: str = Query(..., min_length=1), namespace: str = Query(default="")) -> dict[str, Any]:
        with connect() as db:
            if namespace:
                rows = db.execute("SELECT namespace,value,asset_uuid,created_at FROM identifiers WHERE namespace=? AND value=?", (namespace.lower(), value)).fetchall()
            else:
                rows = db.execute("SELECT namespace,value,asset_uuid,created_at FROM identifiers WHERE value=? ORDER BY namespace", (value,)).fetchall()
        if not rows:
            raise HTTPException(404, "identifier not found")
        return {"matches": [dict(row) for row in rows], "ambiguous": len(rows) > 1}

    @app.post("/v1/assets/{asset_uuid}/container-location")
    async def create_container_location(asset_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        with connect() as db:
            asset = require_asset(db, asset_uuid)
            existing = db.execute("SELECT container_location_uuid FROM container_location_links WHERE container_asset_uuid=?", (asset_uuid,)).fetchone()
            if existing:
                location = require_location(db, existing["container_location_uuid"])
                return {"readback_verified": True, "created": False, "container_asset_uuid": asset_uuid, "location": dict(location), "path": location_path(db, location["uuid"])}

            parent_uuid = str(payload.get("parent_location_uuid") or asset["location_uuid"] or "").strip() or None
            if parent_uuid:
                require_location(db, parent_uuid)
            location_uuid = _uuid()
            name = str(payload.get("name") or asset["name"] or "Container").strip()[:160]
            now = _now()
            db.execute(
                "INSERT INTO locations(uuid,name,parent_uuid,location_type,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                (location_uuid, name, parent_uuid, "container", now, now),
            )
            db.execute(
                "INSERT INTO container_location_links(container_asset_uuid,container_location_uuid,created_at,updated_at) VALUES(?,?,?,?)",
                (asset_uuid, location_uuid, now, now),
            )
            if hasattr(core_module, "audit"):
                core_module.audit(db, "inventory.container_location.create", asset_uuid, {"container_location_uuid": location_uuid, "parent_location_uuid": parent_uuid})
            db.commit()
            location = require_location(db, location_uuid)
        return {"readback_verified": True, "created": True, "container_asset_uuid": asset_uuid, "location": dict(location), "path": location_path(db, location_uuid)}

    @app.get("/v1/locations/{location_uuid}/path")
    def read_location_path(location_uuid: str) -> dict[str, Any]:
        with connect() as db:
            require_location(db, location_uuid)
            path = location_path(db, location_uuid)
        return {"location_uuid": location_uuid, "path": path, "display_path": " > ".join(item["name"] for item in path)}

    @app.get("/v1/assets/{asset_uuid}/where")
    def asset_where(asset_uuid: str) -> dict[str, Any]:
        with connect() as db:
            asset = require_asset(db, asset_uuid)
            direct_path = location_path(db, asset["location_uuid"])
            container = db.execute("SELECT container_location_uuid FROM container_location_links WHERE container_asset_uuid=?", (asset_uuid,)).fetchone()
            container_path = location_path(db, container["container_location_uuid"]) if container else []
        return {
            "asset_uuid": asset_uuid,
            "asset_name": asset["name"],
            "direct_location_uuid": asset["location_uuid"],
            "path": direct_path,
            "display_path": " > ".join(item["name"] for item in direct_path),
            "is_physical_container": bool(container),
            "container_location_uuid": container["container_location_uuid"] if container else None,
            "container_path": container_path,
            "rule": "assets inside a physical container point to the container location; moving the container changes the container location parent so child paths follow automatically",
        }
