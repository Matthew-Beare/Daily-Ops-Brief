from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request


UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)

HEADER_ALIASES = {
    "uuid": "uuid",
    "id": "legacy_id",
    "asset uuid": "asset_uuid",
    "asset_uuid": "asset_uuid",
    "name": "name",
    "item": "name",
    "item name": "name",
    "description": "description",
    "notes": "description",
    "category": "category",
    "location": "location",
    "serial": "serial",
    "serial number": "serial",
    "serial_number": "serial",
    "model": "model",
    "mpn": "mpn",
    "part number": "mpn",
    "manufacturer part number": "mpn",
    "upc": "gtin",
    "ean": "gtin",
    "gtin": "gtin",
    "sku": "retailer_sku",
    "retailer sku": "retailer_sku",
    "quantity": "quantity",
    "parent": "parent",
    "parent location": "parent",
    "type": "location_type",
    "location type": "location_type",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid(value: Any = None) -> str:
    text = str(value or "").strip()
    return text if UUID_RE.match(text) else str(uuid.uuid4())


def _norm_header(value: Any) -> str:
    text = re.sub(r"[_\-]+", " ", str(value or "").strip().lower())
    text = re.sub(r"\s+", " ", text)
    return HEADER_ALIASES.get(text, text)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _sheet_rows(sheet: dict[str, Any]) -> list[dict[str, Any]]:
    values = sheet.get("values") or []
    if not isinstance(values, list) or len(values) < 2 or not isinstance(values[0], list):
        return []
    headers = [_norm_header(item) for item in values[0]]
    rows = []
    for index, raw in enumerate(values[1:], start=2):
        if not isinstance(raw, list) or not any(_clean(item) for item in raw):
            continue
        row = {headers[i]: raw[i] if i < len(raw) else "" for i in range(len(headers)) if headers[i]}
        row["_sheet_row"] = index
        rows.append(row)
    return rows


def _sheet_title(sheet: dict[str, Any]) -> str:
    return _clean((sheet.get("properties") or {}).get("title"))


def _classify_sheet(sheet: dict[str, Any]) -> str:
    title = _sheet_title(sheet).lower()
    rows = _sheet_rows(sheet)
    keys = set(rows[0]) if rows else set()
    if "location" in title or {"location_type", "parent"} & keys:
        return "locations"
    if "categor" in title:
        return "categories"
    if "setting" in title:
        return "settings"
    if "asset" in title or "inventory" in title or "serial" in keys or "gtin" in keys or "retailer_sku" in keys:
        return "assets"
    return "unknown"


def _canonical_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("mirror_export_version"):
        return {
            "source_kind": "mirror_export",
            "categories": snapshot.get("categories") or [],
            "locations": snapshot.get("locations") or [],
            "assets": snapshot.get("assets") or [],
            "identifiers": snapshot.get("identifiers") or [],
            "settings": snapshot.get("settings") or {},
            "unknown_sheets": [],
        }
    sheets = snapshot.get("sheets") or []
    result: dict[str, Any] = {"source_kind": "google_sheets", "categories": [], "locations": [], "assets": [], "identifiers": [], "settings": {}, "unknown_sheets": []}
    for sheet in sheets:
        kind = _classify_sheet(sheet)
        rows = _sheet_rows(sheet)
        if kind == "unknown":
            result["unknown_sheets"].append({"title": _sheet_title(sheet), "row_count": len(rows)})
        elif kind == "settings":
            for row in rows:
                key = _clean(row.get("setting_key") or row.get("key") or row.get("name"))
                if key:
                    result["settings"][key] = row.get("value")
        else:
            result[kind].extend(rows)
    return result


def install_migration_apply(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_apply_runs (
              apply_uuid TEXT PRIMARY KEY,
              snapshot_uuid TEXT NOT NULL,
              status TEXT NOT NULL,
              plan_json TEXT NOT NULL,
              result_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        db.commit()

    def snapshot_payload(db: sqlite3.Connection, snapshot_uuid: str) -> tuple[sqlite3.Row, dict[str, Any]]:
        row = db.execute("SELECT * FROM migration_snapshots WHERE snapshot_uuid=?", (snapshot_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "migration snapshot not found")
        return row, json.loads(row["payload_json"])

    def existing_uuid(db: sqlite3.Connection, table: str, uuid_value: str) -> bool:
        return bool(db.execute(f"SELECT 1 FROM {table} WHERE uuid=?", (uuid_value,)).fetchone())

    def unique_identifier_match(db: sqlite3.Connection, row: dict[str, Any], merchant: str = "legacy") -> tuple[str | None, list[str]]:
        probes = []
        for namespace, key in (("serial", "serial"), ("gtin", "gtin"), ("mpn", "mpn"), ("model", "model"), (f"retailer:{merchant}:sku", "retailer_sku")):
            value = _clean(row.get(key))
            if value:
                probes.append((namespace, re.sub(r"\D", "", value) if namespace == "gtin" else value))
        matches: set[str] = set()
        evidence: list[str] = []
        for namespace, value in probes:
            rows = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, value)).fetchall()
            for found in rows:
                matches.add(found["asset_uuid"])
                evidence.append(f"{namespace}:{value}")
        if len(matches) == 1:
            return next(iter(matches)), evidence
        if len(matches) > 1:
            return None, ["conflicting identifiers resolved to multiple assets", *evidence]
        return None, evidence

    def build_plan(db: sqlite3.Connection, snapshot_uuid: str) -> dict[str, Any]:
        snapshot_row, snapshot = snapshot_payload(db, snapshot_uuid)
        normalized = _canonical_payload(snapshot)
        plan: dict[str, Any] = {
            "snapshot_uuid": snapshot_uuid,
            "source_type": snapshot_row["source_type"],
            "source_kind": normalized["source_kind"],
            "content_sha256": snapshot_row["content_sha256"],
            "categories": [], "locations": [], "assets": [], "identifiers": [], "settings": [],
            "needs_review": [], "unknown_sheets": normalized["unknown_sheets"],
        }

        for row in normalized["categories"]:
            name = _clean(row.get("name"))
            if not name:
                plan["needs_review"].append({"kind": "category", "row": row, "reason": "missing name"}); continue
            uuid_value = _clean(row.get("uuid") or row.get("category_uuid"))
            existing = db.execute("SELECT uuid FROM categories WHERE lower(name)=lower(?)", (name,)).fetchone()
            plan["categories"].append({"action": "reuse" if existing else "create", "uuid": existing["uuid"] if existing else _uuid(uuid_value), "name": name, "parent": _clean(row.get("parent_uuid") or row.get("parent")) or None})

        for row in normalized["locations"]:
            name = _clean(row.get("name") or row.get("location"))
            if not name:
                plan["needs_review"].append({"kind": "location", "row": row, "reason": "missing name"}); continue
            uuid_value = _clean(row.get("uuid") or row.get("location_uuid"))
            existing = db.execute("SELECT uuid FROM locations WHERE lower(name)=lower(?) AND COALESCE(location_type,'')=COALESCE(?, '')", (name, _clean(row.get("location_type") or row.get("type")) or "storage")).fetchone()
            plan["locations"].append({"action": "reuse" if existing else "create", "uuid": existing["uuid"] if existing else _uuid(uuid_value), "name": name, "location_type": _clean(row.get("location_type") or row.get("type")) or "storage", "parent": _clean(row.get("parent_uuid") or row.get("parent")) or None})

        for row in normalized["assets"]:
            name = _clean(row.get("name") or row.get("item"))
            if not name:
                plan["needs_review"].append({"kind": "asset", "row": row, "reason": "missing name"}); continue
            supplied_uuid = _clean(row.get("uuid") or row.get("asset_uuid"))
            if supplied_uuid and UUID_RE.match(supplied_uuid) and existing_uuid(db, "assets", supplied_uuid):
                action, asset_uuid, basis = "reuse", supplied_uuid, ["existing immutable UUID"]
            else:
                matched, basis = unique_identifier_match(db, row)
                if basis and matched is None and basis[0].startswith("conflicting"):
                    plan["needs_review"].append({"kind": "asset", "row": row, "reason": "identifier conflict", "evidence": basis}); continue
                action, asset_uuid = ("reuse", matched) if matched else ("create", _uuid(supplied_uuid))
            plan["assets"].append({"action": action, "asset_uuid": asset_uuid, "name": name, "description": _clean(row.get("description")), "category": _clean(row.get("category")) or None, "location": _clean(row.get("location")) or None, "row": row, "identity_basis": basis})

        for row in normalized["identifiers"]:
            namespace = _clean(row.get("namespace")); value = _clean(row.get("value")); asset_uuid = _clean(row.get("asset_uuid"))
            if namespace and value and asset_uuid:
                plan["identifiers"].append({"namespace": namespace, "value": value, "asset_uuid": asset_uuid})
            else:
                plan["needs_review"].append({"kind": "identifier", "row": row, "reason": "identifier requires namespace, value and asset_uuid"})

        for key, value in (normalized.get("settings") or {}).items():
            plan["settings"].append({"setting_key": str(key), "value": value})
        plan["safe_to_apply"] = bool(plan["categories"] or plan["locations"] or plan["assets"] or plan["identifiers"] or plan["settings"])
        plan["fully_automatic"] = plan["safe_to_apply"] and not plan["needs_review"] and not plan["unknown_sheets"]
        return plan

    def ensure_named_category(db: sqlite3.Connection, name: str | None) -> str | None:
        if not name:
            return None
        row = db.execute("SELECT uuid FROM categories WHERE lower(name)=lower(?)", (name,)).fetchone()
        if row: return row["uuid"]
        new_uuid = _uuid(); now = _now()
        db.execute("INSERT INTO categories(uuid,name,parent_uuid,created_at,updated_at) VALUES(?,?,?,?,?)", (new_uuid, name, None, now, now))
        return new_uuid

    def ensure_named_location(db: sqlite3.Connection, name: str | None) -> str | None:
        if not name:
            return None
        row = db.execute("SELECT uuid FROM locations WHERE lower(name)=lower(?)", (name,)).fetchone()
        if row: return row["uuid"]
        new_uuid = _uuid(); now = _now()
        db.execute("INSERT INTO locations(uuid,name,parent_uuid,location_type,created_at,updated_at) VALUES(?,?,?,?,?,?)", (new_uuid, name, None, "storage", now, now))
        return new_uuid

    def apply_plan(db: sqlite3.Connection, plan: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {"created": {"categories": 0, "locations": 0, "assets": 0, "identifiers": 0}, "reused": {"categories": 0, "locations": 0, "assets": 0}, "settings": 0, "needs_review": plan["needs_review"], "unknown_sheets": plan["unknown_sheets"]}
        now = _now()
        for item in plan["categories"]:
            if item["action"] == "create" and not existing_uuid(db, "categories", item["uuid"]):
                db.execute("INSERT INTO categories(uuid,name,parent_uuid,created_at,updated_at) VALUES(?,?,?,?,?)", (item["uuid"], item["name"], None, now, now)); result["created"]["categories"] += 1
            else: result["reused"]["categories"] += 1
        for item in plan["locations"]:
            if item["action"] == "create" and not existing_uuid(db, "locations", item["uuid"]):
                db.execute("INSERT INTO locations(uuid,name,parent_uuid,location_type,created_at,updated_at) VALUES(?,?,?,?,?,?)", (item["uuid"], item["name"], None, item["location_type"], now, now)); result["created"]["locations"] += 1
            else: result["reused"]["locations"] += 1
        for item in plan["assets"]:
            row = item["row"]
            asset_uuid = item["asset_uuid"]
            if item["action"] == "create" and not existing_uuid(db, "assets", asset_uuid):
                category_uuid = ensure_named_category(db, item["category"])
                location_uuid = ensure_named_location(db, item["location"])
                metadata = {"migration_source": plan["snapshot_uuid"], "legacy_row": {key: value for key, value in row.items() if not str(key).startswith("_")}}
                db.execute("INSERT INTO assets(uuid,name,description,category_uuid,location_uuid,status,metadata_json,created_at,updated_at) VALUES(?,?,?,?,?,'active',?,?,?)", (asset_uuid, item["name"], item["description"], category_uuid, location_uuid, json.dumps(metadata, separators=(",", ":"), sort_keys=True), now, now))
                result["created"]["assets"] += 1
            else: result["reused"]["assets"] += 1
            aliases = (("serial", row.get("serial")), ("gtin", re.sub(r"\D", "", _clean(row.get("gtin")))), ("model", row.get("model")), ("mpn", row.get("mpn")), ("retailer:legacy:sku", row.get("retailer_sku")))
            for namespace, value in aliases:
                value = _clean(value)
                if not value: continue
                existing = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, value)).fetchone()
                if existing and existing["asset_uuid"] != asset_uuid:
                    result["needs_review"].append({"kind": "identifier", "reason": "identity collision during apply", "namespace": namespace, "value": value, "wanted_asset_uuid": asset_uuid, "existing_asset_uuid": existing["asset_uuid"]}); continue
                if not existing:
                    db.execute("INSERT INTO identifiers(namespace,value,asset_uuid,created_at) VALUES(?,?,?,?)", (namespace, value, asset_uuid, now)); result["created"]["identifiers"] += 1
        for item in plan["identifiers"]:
            if not existing_uuid(db, "assets", item["asset_uuid"]):
                result["needs_review"].append({"kind": "identifier", "reason": "referenced asset UUID does not exist", **item}); continue
            existing = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (item["namespace"], item["value"])).fetchone()
            if existing and existing["asset_uuid"] != item["asset_uuid"]:
                result["needs_review"].append({"kind": "identifier", "reason": "identity collision during apply", **item}); continue
            if not existing:
                db.execute("INSERT INTO identifiers(namespace,value,asset_uuid,created_at) VALUES(?,?,?,?)", (item["namespace"], item["value"], item["asset_uuid"], now)); result["created"]["identifiers"] += 1
        if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_settings'").fetchone():
            for item in plan["settings"]:
                db.execute("INSERT INTO user_settings(setting_key,value_json,updated_at) VALUES(?,?,?) ON CONFLICT(setting_key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at", (item["setting_key"], json.dumps(item["value"], separators=(",", ":"), sort_keys=True), now)); result["settings"] += 1
        return result

    @app.get("/v1/migrations/{snapshot_uuid}/plan")
    def migration_plan(snapshot_uuid: str) -> dict[str, Any]:
        with connect() as db:
            plan = build_plan(db, snapshot_uuid)
        return {"plan": plan, "rule": "UUID/strong-identifier identity is preserved; names alone never merge assets"}

    @app.post("/v1/migrations/{snapshot_uuid}/apply-safe")
    async def migration_apply_safe(snapshot_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        confirm = bool(payload.get("confirm", False))
        if not confirm:
            raise HTTPException(400, "confirm=true is required after showing the migration plan")
        apply_uuid = str(uuid.uuid4())
        with connect() as db:
            plan = build_plan(db, snapshot_uuid)
            if not plan["safe_to_apply"]:
                raise HTTPException(409, "snapshot contains no recognized safe migration rows")
            db.execute("BEGIN IMMEDIATE")
            try:
                result = apply_plan(db, plan)
                status = "applied_with_review" if result["needs_review"] or result["unknown_sheets"] else "applied"
                now = _now()
                db.execute("INSERT INTO migration_apply_runs(apply_uuid,snapshot_uuid,status,plan_json,result_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", (apply_uuid, snapshot_uuid, status, json.dumps(plan, separators=(",", ":"), sort_keys=True), json.dumps(result, separators=(",", ":"), sort_keys=True), now, now))
                db.execute("UPDATE migration_snapshots SET status=? WHERE snapshot_uuid=?", (status, snapshot_uuid))
                if hasattr(core_module, "audit"):
                    core_module.audit(db, "migration.apply_safe", snapshot_uuid, {"apply_uuid": apply_uuid, "status": status, "created": result["created"], "review_count": len(result["needs_review"])})
                db.commit()
            except Exception:
                db.rollback(); raise
            readback = db.execute("SELECT status,result_json FROM migration_apply_runs WHERE apply_uuid=?", (apply_uuid,)).fetchone()
        return {"readback_verified": bool(readback), "apply_uuid": apply_uuid, "status": readback["status"] if readback else None, "result": json.loads(readback["result_json"]) if readback else None, "human_required": bool(readback and (json.loads(readback["result_json"])["needs_review"] or json.loads(readback["result_json"])["unknown_sheets"]))}

    @app.post("/v1/migrations/{snapshot_uuid}/magic")
    async def migration_magic(snapshot_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        with connect() as db:
            plan = build_plan(db, snapshot_uuid)
        if not payload.get("apply", False):
            return {"mode": "preview", "plan": plan, "next_step": "show this human-readable plan; call again with apply=true to apply every unambiguous row in one transaction"}
        class _Request:
            async def json(self) -> dict[str, bool]: return {"confirm": True}
        return await migration_apply_safe(snapshot_uuid, _Request())
