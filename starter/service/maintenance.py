from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request

MAINTENANCE_HINTS = (
    "oil", "filter", "spark plug", "brake", "coolant", "fluid", "belt", "tire", "battery",
    "bearing", "grease", "blade", "fuel filter", "air filter", "service", "maintenance",
)
EQUIPMENT_HINTS = ("car", "truck", "vehicle", "mower", "tractor", "generator", "compressor", "motorcycle", "equipment", "engine")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_maintenance(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS asset_meters (
              meter_uuid TEXT PRIMARY KEY,
              asset_uuid TEXT NOT NULL,
              meter_type TEXT NOT NULL,
              unit TEXT NOT NULL,
              label TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(asset_uuid) REFERENCES assets(uuid)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_meter_unique ON asset_meters(asset_uuid,meter_type,unit);
            CREATE TABLE IF NOT EXISTS meter_readings (
              reading_uuid TEXT PRIMARY KEY,
              meter_uuid TEXT NOT NULL,
              value REAL NOT NULL,
              observed_at TEXT NOT NULL,
              source TEXT NOT NULL,
              evidence_uuid TEXT,
              created_at TEXT NOT NULL,
              FOREIGN KEY(meter_uuid) REFERENCES asset_meters(meter_uuid)
            );
            CREATE TABLE IF NOT EXISTS maintenance_events (
              maintenance_uuid TEXT PRIMARY KEY,
              asset_uuid TEXT NOT NULL,
              service_type TEXT NOT NULL,
              performed_at TEXT NOT NULL,
              meter_uuid TEXT,
              meter_value REAL,
              receipt_uuid TEXT,
              receipt_line_uuid TEXT,
              total_cost REAL,
              notes TEXT NOT NULL DEFAULT '',
              metadata_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(asset_uuid) REFERENCES assets(uuid),
              FOREIGN KEY(meter_uuid) REFERENCES asset_meters(meter_uuid)
            );
            CREATE INDEX IF NOT EXISTS idx_maintenance_asset ON maintenance_events(asset_uuid,performed_at DESC);
            """
        )
        db.commit()

    def asset_exists(db: sqlite3.Connection, asset_uuid: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM assets WHERE uuid=? AND status='active'", (asset_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "asset not found")
        return row

    def ensure_meter(db: sqlite3.Connection, asset_uuid: str, meter_type: str, unit: str, label: str = "") -> str:
        meter_type = meter_type.strip().lower()
        unit = unit.strip().lower()
        if meter_type not in {"odometer", "engine_hours", "runtime_hours", "cycles", "other"}:
            raise HTTPException(400, "unsupported meter type")
        row = db.execute("SELECT meter_uuid FROM asset_meters WHERE asset_uuid=? AND meter_type=? AND unit=?", (asset_uuid, meter_type, unit)).fetchone()
        if row:
            return row["meter_uuid"]
        meter_uuid = str(uuid.uuid4())
        now = _now()
        db.execute(
            "INSERT INTO asset_meters(meter_uuid,asset_uuid,meter_type,unit,label,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
            (meter_uuid, asset_uuid, meter_type, unit, label or f"{meter_type.replace('_',' ').title()} ({unit})", now, now),
        )
        return meter_uuid

    @app.get("/v1/assets/{asset_uuid}/maintenance")
    def maintenance_history(asset_uuid: str) -> dict[str, Any]:
        with connect() as db:
            asset = asset_exists(db, asset_uuid)
            meters = [dict(row) for row in db.execute("SELECT * FROM asset_meters WHERE asset_uuid=? ORDER BY label", (asset_uuid,))]
            for meter in meters:
                reading = db.execute("SELECT * FROM meter_readings WHERE meter_uuid=? ORDER BY observed_at DESC,created_at DESC LIMIT 1", (meter["meter_uuid"],)).fetchone()
                meter["latest_reading"] = dict(reading) if reading else None
            events = [dict(row) for row in db.execute("SELECT * FROM maintenance_events WHERE asset_uuid=? ORDER BY performed_at DESC,created_at DESC", (asset_uuid,))]
            for event in events:
                event["metadata"] = json.loads(event.pop("metadata_json") or "{}")
        return {"asset": {"uuid": asset["uuid"], "name": asset["name"]}, "meters": meters, "maintenance": events}

    @app.post("/v1/assets/{asset_uuid}/meters")
    async def create_meter(asset_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        with connect() as db:
            asset_exists(db, asset_uuid)
            meter_uuid = ensure_meter(db, asset_uuid, str(payload.get("meter_type") or "other"), str(payload.get("unit") or "count"), str(payload.get("label") or ""))
            db.commit()
            row = db.execute("SELECT * FROM asset_meters WHERE meter_uuid=?", (meter_uuid,)).fetchone()
        return {"readback_verified": True, "meter": dict(row)}

    @app.post("/v1/assets/{asset_uuid}/meter-readings")
    async def add_meter_reading(asset_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        value = float(payload.get("value"))
        with connect() as db:
            asset_exists(db, asset_uuid)
            meter_uuid = str(payload.get("meter_uuid") or "")
            if not meter_uuid:
                meter_uuid = ensure_meter(db, asset_uuid, str(payload.get("meter_type") or "odometer"), str(payload.get("unit") or "miles"), str(payload.get("label") or ""))
            meter = db.execute("SELECT * FROM asset_meters WHERE meter_uuid=? AND asset_uuid=?", (meter_uuid, asset_uuid)).fetchone()
            if not meter:
                raise HTTPException(404, "meter not found for asset")
            previous = db.execute("SELECT value FROM meter_readings WHERE meter_uuid=? ORDER BY observed_at DESC,created_at DESC LIMIT 1", (meter_uuid,)).fetchone()
            if previous and value < float(previous["value"]) and not bool(payload.get("allow_reset")):
                raise HTTPException(409, "meter value is lower than the prior reading; mark allow_reset only for a documented meter replacement/reset")
            reading_uuid = str(uuid.uuid4())
            observed = str(payload.get("observed_at") or _now())
            db.execute(
                "INSERT INTO meter_readings(reading_uuid,meter_uuid,value,observed_at,source,evidence_uuid,created_at) VALUES(?,?,?,?,?,?,?)",
                (reading_uuid, meter_uuid, value, observed, str(payload.get("source") or "user"), payload.get("evidence_uuid") or None, _now()),
            )
            db.commit()
            row = db.execute("SELECT * FROM meter_readings WHERE reading_uuid=?", (reading_uuid,)).fetchone()
        return {"readback_verified": True, "reading": dict(row)}

    @app.get("/v1/receipt-lines/{receipt_line_uuid}/maintenance-fitment")
    def maintenance_fitment(receipt_line_uuid: str) -> dict[str, Any]:
        with connect() as db:
            line = db.execute("SELECT * FROM receipt_lines WHERE receipt_line_uuid=?", (receipt_line_uuid,)).fetchone()
            if not line:
                raise HTTPException(404, "receipt line not found")
            description = str(line["description"] or "").lower()
            maintenance_candidate = any(hint in description for hint in MAINTENANCE_HINTS)
            candidates = []
            for asset in db.execute("SELECT uuid,name,description,metadata_json FROM assets WHERE status='active' ORDER BY name").fetchall():
                metadata = json.loads(asset["metadata_json"] or "{}")
                asset_type = str(metadata.get("asset_type") or metadata.get("kind") or "").lower()
                searchable = f"{asset['name']} {asset['description']} {asset_type}".lower()
                if any(hint in searchable for hint in EQUIPMENT_HINTS) or asset_type in {"vehicle", "mower", "equipment", "machine"}:
                    candidates.append({"asset_uuid": asset["uuid"], "name": asset["name"], "asset_type": asset_type or None})
        return {
            "receipt_line_uuid": receipt_line_uuid,
            "description": line["description"],
            "maintenance_candidate": maintenance_candidate,
            "prompt": "Is this purchase for a vehicle, mower, or other equipment?" if maintenance_candidate else None,
            "candidate_assets": candidates,
        }

    @app.post("/v1/maintenance")
    async def create_maintenance(request: Request) -> dict[str, Any]:
        payload = await request.json()
        asset_uuid = str(payload.get("asset_uuid") or "")
        if not asset_uuid:
            raise HTTPException(400, "asset_uuid is required")
        with connect() as db:
            asset_exists(db, asset_uuid)
            meter_uuid = None
            meter_value = payload.get("meter_value")
            if meter_value is not None:
                meter_uuid = str(payload.get("meter_uuid") or "") or ensure_meter(
                    db,
                    asset_uuid,
                    str(payload.get("meter_type") or "odometer"),
                    str(payload.get("meter_unit") or "miles"),
                    str(payload.get("meter_label") or ""),
                )
                reading_uuid = str(uuid.uuid4())
                db.execute(
                    "INSERT INTO meter_readings(reading_uuid,meter_uuid,value,observed_at,source,created_at) VALUES(?,?,?,?,?,?)",
                    (reading_uuid, meter_uuid, float(meter_value), str(payload.get("performed_at") or _now()), "maintenance_event", _now()),
                )
            maintenance_uuid = str(uuid.uuid4())
            now = _now()
            db.execute(
                "INSERT INTO maintenance_events(maintenance_uuid,asset_uuid,service_type,performed_at,meter_uuid,meter_value,receipt_uuid,receipt_line_uuid,total_cost,notes,metadata_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    maintenance_uuid,
                    asset_uuid,
                    str(payload.get("service_type") or "maintenance").strip()[:160],
                    str(payload.get("performed_at") or now),
                    meter_uuid,
                    float(meter_value) if meter_value is not None else None,
                    payload.get("receipt_uuid") or None,
                    payload.get("receipt_line_uuid") or None,
                    float(payload["total_cost"]) if payload.get("total_cost") is not None else None,
                    str(payload.get("notes") or ""),
                    json.dumps(payload.get("metadata") or {}, separators=(",", ":"), sort_keys=True),
                    now,
                    now,
                ),
            )
            if payload.get("receipt_line_uuid"):
                db.execute("UPDATE receipt_lines SET asset_uuid=?,updated_at=? WHERE receipt_line_uuid=?", (asset_uuid, now, payload["receipt_line_uuid"]))
            db.commit()
            event = db.execute("SELECT * FROM maintenance_events WHERE maintenance_uuid=?", (maintenance_uuid,)).fetchone()
        result = dict(event)
        result["metadata"] = json.loads(result.pop("metadata_json") or "{}")
        return {"readback_verified": True, "maintenance": result}
