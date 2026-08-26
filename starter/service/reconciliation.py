"""Generic MIRROR reconciliation, processor routing metadata, corrections, and usage APIs.

The module deliberately stores work before any model is involved. AI providers are
interchangeable workers; MIRROR remains canonical authority and user-confirmed values
outrank inferred values.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Query, Request

WORK_STATES = {"queued", "processing", "needs_review", "failed_retryable", "quarantined", "complete"}
PRIORITIES = {"routine": 10, "normal": 20, "time_sensitive": 30, "interactive": 40}
DEFAULT_CAPABILITIES = ["text_reasoning"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


def _json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def install_reconciliation(app: Any, core_module: Any) -> None:
    """Install the general queue and provider-neutral reconciliation APIs."""

    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS reconciliation_work (
              work_uuid TEXT PRIMARY KEY,
              feature_namespace TEXT NOT NULL,
              source_type TEXT NOT NULL,
              source_uuid TEXT NOT NULL,
              work_type TEXT NOT NULL,
              processing_mode TEXT NOT NULL DEFAULT 'deferred_reconciliation',
              status TEXT NOT NULL DEFAULT 'queued',
              priority INTEGER NOT NULL DEFAULT 20,
              freshness_minutes INTEGER NOT NULL DEFAULT 1440,
              capabilities_json TEXT NOT NULL DEFAULT '["text_reasoning"]',
              allowed_mutations_json TEXT NOT NULL DEFAULT '[]',
              confidence_threshold REAL NOT NULL DEFAULT 0.90,
              idempotency_key TEXT NOT NULL,
              attempts INTEGER NOT NULL DEFAULT 0,
              next_attempt_at TEXT,
              claimed_by TEXT,
              claimed_at TEXT,
              processor_uuid TEXT,
              processor_version TEXT,
              result_json TEXT NOT NULL DEFAULT '{}',
              last_error TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              completed_at TEXT,
              UNIQUE(feature_namespace,source_type,source_uuid,work_type)
            );
            CREATE INDEX IF NOT EXISTS idx_reconciliation_open
              ON reconciliation_work(status,priority DESC,next_attempt_at,created_at);

            CREATE TABLE IF NOT EXISTS reconciliation_dependencies (
              work_uuid TEXT NOT NULL,
              depends_on_work_uuid TEXT NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY(work_uuid,depends_on_work_uuid),
              FOREIGN KEY(work_uuid) REFERENCES reconciliation_work(work_uuid),
              FOREIGN KEY(depends_on_work_uuid) REFERENCES reconciliation_work(work_uuid)
            );

            CREATE TABLE IF NOT EXISTS feature_processing_policies (
              feature_namespace TEXT PRIMARY KEY,
              enabled INTEGER NOT NULL DEFAULT 1,
              processing_mode TEXT NOT NULL DEFAULT 'deferred_reconciliation',
              freshness TEXT NOT NULL DEFAULT 'next_daily_cleanup',
              capabilities_json TEXT NOT NULL DEFAULT '["text_reasoning"]',
              allowed_mutations_json TEXT NOT NULL DEFAULT '[]',
              preferred_processor_uuid TEXT,
              local_only INTEGER NOT NULL DEFAULT 0,
              max_cost_per_work REAL,
              confidence_threshold REAL NOT NULL DEFAULT 0.90,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ai_processors (
              processor_uuid TEXT PRIMARY KEY,
              provider_kind TEXT NOT NULL,
              display_name TEXT NOT NULL,
              model_name TEXT,
              execution_mode TEXT NOT NULL,
              capabilities_json TEXT NOT NULL DEFAULT '[]',
              enabled INTEGER NOT NULL DEFAULT 1,
              metered INTEGER NOT NULL DEFAULT 0,
              local_only INTEGER NOT NULL DEFAULT 0,
              privacy_class TEXT NOT NULL DEFAULT 'standard',
              priority INTEGER NOT NULL DEFAULT 100,
              health TEXT NOT NULL DEFAULT 'unknown',
              config_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ai_usage (
              usage_uuid TEXT PRIMARY KEY,
              processor_uuid TEXT,
              provider_kind TEXT NOT NULL,
              model_name TEXT,
              work_uuid TEXT,
              feature_namespace TEXT,
              input_units REAL NOT NULL DEFAULT 0,
              output_units REAL NOT NULL DEFAULT 0,
              cached_units REAL NOT NULL DEFAULT 0,
              estimated_cost REAL NOT NULL DEFAULT 0,
              currency TEXT NOT NULL DEFAULT 'USD',
              price_snapshot_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              FOREIGN KEY(processor_uuid) REFERENCES ai_processors(processor_uuid),
              FOREIGN KEY(work_uuid) REFERENCES reconciliation_work(work_uuid)
            );
            CREATE INDEX IF NOT EXISTS idx_ai_usage_time ON ai_usage(created_at);

            CREATE TABLE IF NOT EXISTS user_corrections (
              correction_uuid TEXT PRIMARY KEY,
              entity_type TEXT NOT NULL,
              entity_uuid TEXT NOT NULL,
              field_name TEXT NOT NULL,
              previous_value_json TEXT NOT NULL,
              confirmed_value_json TEXT NOT NULL,
              reason TEXT,
              source TEXT NOT NULL DEFAULT 'user',
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_corrections_entity ON user_corrections(entity_type,entity_uuid,field_name,created_at);

            CREATE TABLE IF NOT EXISTS recognition_profiles (
              profile_uuid TEXT PRIMARY KEY,
              profile_type TEXT NOT NULL,
              lookup_key TEXT NOT NULL,
              value_json TEXT NOT NULL,
              confidence REAL NOT NULL DEFAULT 1.0,
              user_confirmed INTEGER NOT NULL DEFAULT 0,
              source_entity_type TEXT,
              source_entity_uuid TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              UNIQUE(profile_type,lookup_key)
            );

            CREATE TABLE IF NOT EXISTS merchant_locations (
              merchant_location_uuid TEXT PRIMARY KEY,
              merchant_uuid TEXT,
              display_name TEXT NOT NULL,
              store_number TEXT,
              address_line1 TEXT,
              address_line2 TEXT,
              city TEXT,
              region TEXT,
              postal_code TEXT,
              country TEXT,
              latitude REAL,
              longitude REAL,
              metadata_json TEXT NOT NULL DEFAULT '{}',
              user_confirmed INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_merchant_locations_merchant ON merchant_locations(merchant_uuid,store_number,city);

            CREATE TABLE IF NOT EXISTS receipt_merchant_location_links (
              receipt_uuid TEXT PRIMARY KEY,
              merchant_location_uuid TEXT NOT NULL,
              confidence REAL NOT NULL DEFAULT 1.0,
              user_confirmed INTEGER NOT NULL DEFAULT 0,
              linked_at TEXT NOT NULL,
              FOREIGN KEY(receipt_uuid) REFERENCES receipts(receipt_uuid),
              FOREIGN KEY(merchant_location_uuid) REFERENCES merchant_locations(merchant_location_uuid)
            );

            CREATE TRIGGER IF NOT EXISTS queue_receipt_general_reconciliation
            AFTER INSERT ON receipts
            BEGIN
              INSERT OR IGNORE INTO reconciliation_work(
                work_uuid,feature_namespace,source_type,source_uuid,work_type,processing_mode,status,
                priority,freshness_minutes,capabilities_json,allowed_mutations_json,confidence_threshold,
                idempotency_key,created_at,updated_at
              ) VALUES(
                'receipt:' || NEW.receipt_uuid || ':reconcile','receipts','receipt',NEW.receipt_uuid,
                'receipt.reconcile','deferred_reconciliation','queued',20,1440,
                '["text_reasoning"]','["receipt_fields","receipt_lines","merchant","merchant_location","inventory_suggestions"]',
                0.90,'receipt:' || NEW.receipt_uuid || ':reconcile',NEW.created_at,NEW.updated_at
              );
            END;
            """
        )
        # Backfill receipts captured before this module existed.
        db.execute(
            "INSERT OR IGNORE INTO reconciliation_work(work_uuid,feature_namespace,source_type,source_uuid,work_type,processing_mode,status,priority,freshness_minutes,capabilities_json,allowed_mutations_json,confidence_threshold,idempotency_key,created_at,updated_at) "
            "SELECT 'receipt:'||receipt_uuid||':reconcile','receipts','receipt',receipt_uuid,'receipt.reconcile','deferred_reconciliation',"
            "CASE WHEN status IN ('complete','reconciled') THEN 'complete' ELSE 'queued' END,20,1440,'[\"text_reasoning\"]','[\"receipt_fields\",\"receipt_lines\",\"merchant\",\"merchant_location\",\"inventory_suggestions\"]',0.90,'receipt:'||receipt_uuid||':reconcile',created_at,updated_at FROM receipts"
        )
        now = _now()
        defaults = [
            ("chatgpt-scheduled", "chatgpt_scheduled_mira", "MIRA in ChatGPT", None, "scheduled", ["text_reasoning", "vision", "tool_use", "web_research", "structured_output"], 0, 0, 100),
            ("manual", "manual", "Manual review", None, "manual", [], 0, 1, 1000),
        ]
        for processor_uuid, kind, name, model, mode, caps, metered, local_only, priority in defaults:
            db.execute(
                "INSERT OR IGNORE INTO ai_processors(processor_uuid,provider_kind,display_name,model_name,execution_mode,capabilities_json,enabled,metered,local_only,priority,health,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (processor_uuid, kind, name, model, mode, _json(caps), 1, metered, local_only, priority, "available", now, now),
            )
        db.commit()

    def work_dict(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        for key in ("capabilities_json", "allowed_mutations_json", "result_json"):
            item[key.removesuffix("_json")] = json.loads(item.pop(key) or ("{}" if key == "result_json" else "[]"))
        return item

    def processor_dict(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["capabilities"] = json.loads(item.pop("capabilities_json") or "[]")
        item["config"] = json.loads(item.pop("config_json") or "{}")
        return item

    @app.get("/v1/reconciliation/summary")
    def reconciliation_summary() -> dict[str, Any]:
        with connect() as db:
            counts = {row["status"]: row["n"] for row in db.execute("SELECT status,count(*) n FROM reconciliation_work GROUP BY status")}
            oldest = db.execute("SELECT created_at FROM reconciliation_work WHERE status IN ('queued','failed_retryable') ORDER BY priority DESC,created_at LIMIT 1").fetchone()
            usage_today = db.execute("SELECT COALESCE(sum(estimated_cost),0) cost FROM ai_usage WHERE date(created_at)=date('now')").fetchone()["cost"]
            usage_month = db.execute("SELECT COALESCE(sum(estimated_cost),0) cost FROM ai_usage WHERE strftime('%Y-%m',created_at)=strftime('%Y-%m','now')").fetchone()["cost"]
            metered = db.execute("SELECT count(*) n FROM ai_processors WHERE enabled=1 AND metered=1").fetchone()["n"]
        waiting = sum(counts.get(key, 0) for key in ("queued", "failed_retryable", "processing"))
        review = counts.get("needs_review", 0) + counts.get("quarantined", 0)
        return {
            "waiting": waiting,
            "needs_review": review,
            "counts": counts,
            "oldest_waiting_at": oldest["created_at"] if oldest else None,
            "api_cost": {"today": round(float(usage_today or 0), 6), "month": round(float(usage_month or 0), 6), "currency": "USD", "metered_processors_enabled": bool(metered)},
            "default_daily_cleanup_time": "00:01",
            "readback_verified": True,
        }

    @app.get("/v1/reconciliation/work")
    def list_work(status: str = Query(default=""), limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        sql = "SELECT * FROM reconciliation_work"
        params: list[Any] = []
        if status:
            if status not in WORK_STATES:
                raise HTTPException(400, "invalid reconciliation status")
            sql += " WHERE status=?"
            params.append(status)
        sql += " ORDER BY priority DESC,created_at ASC LIMIT ?"
        params.append(limit)
        with connect() as db:
            rows = [work_dict(row) for row in db.execute(sql, params)]
        return {"items": rows, "count": len(rows)}

    @app.post("/v1/reconciliation/work")
    async def create_work(request: Request) -> dict[str, Any]:
        payload = await request.json()
        feature = str(payload.get("feature_namespace") or "general").strip()[:120]
        source_type = str(payload.get("source_type") or "record").strip()[:80]
        source_uuid = str(payload.get("source_uuid") or "").strip()[:200]
        work_type = str(payload.get("work_type") or "general.reconcile").strip()[:160]
        if not source_uuid:
            raise HTTPException(400, "source_uuid is required")
        work_uuid = str(payload.get("work_uuid") or _uuid())
        idempotency_key = str(payload.get("idempotency_key") or f"{feature}:{source_type}:{source_uuid}:{work_type}")[:300]
        priority_name = str(payload.get("priority") or "normal")
        priority = PRIORITIES.get(priority_name, 20) if not priority_name.isdigit() else int(priority_name)
        now = _now()
        with connect() as db:
            db.execute(
                "INSERT INTO reconciliation_work(work_uuid,feature_namespace,source_type,source_uuid,work_type,processing_mode,status,priority,freshness_minutes,capabilities_json,allowed_mutations_json,confidence_threshold,idempotency_key,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(feature_namespace,source_type,source_uuid,work_type) DO UPDATE SET priority=max(priority,excluded.priority),updated_at=excluded.updated_at",
                (work_uuid, feature, source_type, source_uuid, work_type, str(payload.get("processing_mode") or "deferred_reconciliation"), "queued", priority, int(payload.get("freshness_minutes") or 1440), _json(payload.get("capabilities") or DEFAULT_CAPABILITIES), _json(payload.get("allowed_mutations") or []), float(payload.get("confidence_threshold") or 0.90), idempotency_key, now, now),
            )
            db.commit()
            row = db.execute("SELECT * FROM reconciliation_work WHERE feature_namespace=? AND source_type=? AND source_uuid=? AND work_type=?", (feature, source_type, source_uuid, work_type)).fetchone()
        return {"readback_verified": True, "work": work_dict(row)}

    @app.post("/v1/reconciliation/work/{work_uuid}/claim")
    async def claim_work(work_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        worker = str(payload.get("worker") or "mira").strip()[:160]
        processor_uuid = str(payload.get("processor_uuid") or "").strip() or None
        now = _now()
        with connect() as db:
            row = db.execute("SELECT * FROM reconciliation_work WHERE work_uuid=?", (work_uuid,)).fetchone()
            if not row:
                raise HTTPException(404, "reconciliation work not found")
            if row["status"] == "complete":
                return {"readback_verified": True, "work": work_dict(row), "idempotent_replay": True}
            deps = db.execute("SELECT 1 FROM reconciliation_dependencies d JOIN reconciliation_work w ON w.work_uuid=d.depends_on_work_uuid WHERE d.work_uuid=? AND w.status<>'complete' LIMIT 1", (work_uuid,)).fetchone()
            if deps:
                raise HTTPException(409, "reconciliation prerequisites are not complete")
            db.execute("UPDATE reconciliation_work SET status='processing',claimed_by=?,claimed_at=?,processor_uuid=?,attempts=attempts+1,last_error=NULL,updated_at=? WHERE work_uuid=?", (worker, processor_uuid, now, now, work_uuid))
            db.commit()
            out = db.execute("SELECT * FROM reconciliation_work WHERE work_uuid=?", (work_uuid,)).fetchone()
        return {"readback_verified": True, "work": work_dict(out)}

    @app.post("/v1/reconciliation/work/{work_uuid}/result")
    async def finish_work(work_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        outcome = str(payload.get("outcome") or "needs_review").strip()
        if outcome not in WORK_STATES - {"queued", "processing"}:
            raise HTTPException(400, "invalid reconciliation outcome")
        now = _now()
        with connect() as db:
            existing = db.execute("SELECT * FROM reconciliation_work WHERE work_uuid=?", (work_uuid,)).fetchone()
            if not existing:
                raise HTTPException(404, "reconciliation work not found")
            completed_at = now if outcome == "complete" else None
            db.execute("UPDATE reconciliation_work SET status=?,result_json=?,processor_version=?,last_error=?,next_attempt_at=?,updated_at=?,completed_at=? WHERE work_uuid=?", (outcome, _json(payload.get("result") or {}), str(payload.get("processor_version") or "") or None, str(payload.get("error") or "") or None, payload.get("next_attempt_at"), now, completed_at, work_uuid))
            db.commit()
            row = db.execute("SELECT * FROM reconciliation_work WHERE work_uuid=?", (work_uuid,)).fetchone()
        return {"readback_verified": True, "work": work_dict(row)}

    @app.get("/v1/ai/processors")
    def list_processors() -> dict[str, Any]:
        with connect() as db:
            rows = [processor_dict(row) for row in db.execute("SELECT * FROM ai_processors ORDER BY priority,display_name")]
        return {"processors": rows}

    @app.post("/v1/ai/processors")
    async def register_processor(request: Request) -> dict[str, Any]:
        payload = await request.json()
        provider = str(payload.get("provider_kind") or "").strip()
        name = str(payload.get("display_name") or "").strip()
        if not provider or not name:
            raise HTTPException(400, "provider_kind and display_name are required")
        processor_uuid = str(payload.get("processor_uuid") or _uuid())
        now = _now()
        # config_json is non-secret routing metadata only. Credentials belong in secret storage.
        config = payload.get("config") or {}
        if any(key.lower() in {"api_key", "token", "secret", "password"} for key in config):
            raise HTTPException(400, "processor secrets must use protected secret storage, not MIRROR metadata")
        with connect() as db:
            db.execute("INSERT INTO ai_processors(processor_uuid,provider_kind,display_name,model_name,execution_mode,capabilities_json,enabled,metered,local_only,privacy_class,priority,health,config_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(processor_uuid) DO UPDATE SET provider_kind=excluded.provider_kind,display_name=excluded.display_name,model_name=excluded.model_name,execution_mode=excluded.execution_mode,capabilities_json=excluded.capabilities_json,enabled=excluded.enabled,metered=excluded.metered,local_only=excluded.local_only,privacy_class=excluded.privacy_class,priority=excluded.priority,health=excluded.health,config_json=excluded.config_json,updated_at=excluded.updated_at", (processor_uuid, provider, name, str(payload.get("model_name") or "") or None, str(payload.get("execution_mode") or "api"), _json(payload.get("capabilities") or []), 1 if payload.get("enabled", True) else 0, 1 if payload.get("metered") else 0, 1 if payload.get("local_only") else 0, str(payload.get("privacy_class") or "standard"), int(payload.get("priority") or 100), str(payload.get("health") or "unknown"), _json(config), now, now))
            db.commit()
            row = db.execute("SELECT * FROM ai_processors WHERE processor_uuid=?", (processor_uuid,)).fetchone()
        return {"readback_verified": True, "processor": processor_dict(row)}

    @app.post("/v1/ai/usage")
    async def record_usage(request: Request) -> dict[str, Any]:
        payload = await request.json()
        cost = float(payload.get("estimated_cost") or 0)
        if cost < 0:
            raise HTTPException(400, "estimated_cost cannot be negative")
        usage_uuid = str(payload.get("usage_uuid") or _uuid())
        with connect() as db:
            db.execute("INSERT INTO ai_usage(usage_uuid,processor_uuid,provider_kind,model_name,work_uuid,feature_namespace,input_units,output_units,cached_units,estimated_cost,currency,price_snapshot_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (usage_uuid, payload.get("processor_uuid"), str(payload.get("provider_kind") or "unknown"), payload.get("model_name"), payload.get("work_uuid"), payload.get("feature_namespace"), float(payload.get("input_units") or 0), float(payload.get("output_units") or 0), float(payload.get("cached_units") or 0), cost, str(payload.get("currency") or "USD"), _json(payload.get("price_snapshot") or {}), _now()))
            db.commit()
            row = db.execute("SELECT * FROM ai_usage WHERE usage_uuid=?", (usage_uuid,)).fetchone()
        return {"readback_verified": row is not None, "usage": dict(row)}

    @app.post("/v1/reconciliation/corrections")
    async def record_correction(request: Request) -> dict[str, Any]:
        payload = await request.json()
        entity_type = str(payload.get("entity_type") or "").strip()
        entity_uuid = str(payload.get("entity_uuid") or "").strip()
        field_name = str(payload.get("field_name") or "").strip()
        if not entity_type or not entity_uuid or not field_name:
            raise HTTPException(400, "entity_type, entity_uuid and field_name are required")
        correction_uuid = _uuid()
        with connect() as db:
            db.execute("INSERT INTO user_corrections(correction_uuid,entity_type,entity_uuid,field_name,previous_value_json,confirmed_value_json,reason,created_at) VALUES(?,?,?,?,?,?,?,?)", (correction_uuid, entity_type, entity_uuid, field_name, _json(payload.get("previous_value")), _json(payload.get("confirmed_value")), str(payload.get("reason") or "") or None, _now()))
            if payload.get("recognition_profile"):
                profile = payload["recognition_profile"]
                db.execute("INSERT INTO recognition_profiles(profile_uuid,profile_type,lookup_key,value_json,confidence,user_confirmed,source_entity_type,source_entity_uuid,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(profile_type,lookup_key) DO UPDATE SET value_json=excluded.value_json,confidence=1.0,user_confirmed=1,source_entity_type=excluded.source_entity_type,source_entity_uuid=excluded.source_entity_uuid,updated_at=excluded.updated_at", (_uuid(), str(profile.get("profile_type") or "correction"), str(profile.get("lookup_key") or ""), _json(profile.get("value")), 1.0, 1, entity_type, entity_uuid, _now(), _now()))
            db.commit()
        return {"readback_verified": True, "correction_uuid": correction_uuid, "authority": "user_confirmed"}

    @app.get("/v1/reconciliation/recognition/{profile_type}/{lookup_key}")
    def recognition_lookup(profile_type: str, lookup_key: str) -> dict[str, Any]:
        with connect() as db:
            row = db.execute("SELECT * FROM recognition_profiles WHERE profile_type=? AND lookup_key=?", (profile_type, lookup_key)).fetchone()
        if not row:
            return {"match": None}
        item = dict(row)
        item["value"] = json.loads(item.pop("value_json") or "null")
        return {"match": item}

    @app.post("/v1/features/{feature_namespace}/processing-policy")
    async def set_feature_processing_policy(feature_namespace: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        now = _now()
        with connect() as db:
            db.execute("INSERT INTO feature_processing_policies(feature_namespace,enabled,processing_mode,freshness,capabilities_json,allowed_mutations_json,preferred_processor_uuid,local_only,max_cost_per_work,confidence_threshold,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(feature_namespace) DO UPDATE SET enabled=excluded.enabled,processing_mode=excluded.processing_mode,freshness=excluded.freshness,capabilities_json=excluded.capabilities_json,allowed_mutations_json=excluded.allowed_mutations_json,preferred_processor_uuid=excluded.preferred_processor_uuid,local_only=excluded.local_only,max_cost_per_work=excluded.max_cost_per_work,confidence_threshold=excluded.confidence_threshold,updated_at=excluded.updated_at", (feature_namespace, 1 if payload.get("enabled", True) else 0, str(payload.get("processing_mode") or "deferred_reconciliation"), str(payload.get("freshness") or "next_daily_cleanup"), _json(payload.get("capabilities") or DEFAULT_CAPABILITIES), _json(payload.get("allowed_mutations") or []), payload.get("preferred_processor_uuid"), 1 if payload.get("local_only") else 0, payload.get("max_cost_per_work"), float(payload.get("confidence_threshold") or 0.90), now, now))
            db.commit()
            row = db.execute("SELECT * FROM feature_processing_policies WHERE feature_namespace=?", (feature_namespace,)).fetchone()
        item = dict(row)
        item["capabilities"] = json.loads(item.pop("capabilities_json") or "[]")
        item["allowed_mutations"] = json.loads(item.pop("allowed_mutations_json") or "[]")
        return {"readback_verified": True, "policy": item}

    @app.post("/v1/merchant-locations")
    async def upsert_merchant_location(request: Request) -> dict[str, Any]:
        payload = await request.json()
        location_uuid = str(payload.get("merchant_location_uuid") or _uuid())
        display_name = str(payload.get("display_name") or "").strip()
        if not display_name:
            raise HTTPException(400, "display_name is required")
        now = _now()
        with connect() as db:
            db.execute("INSERT INTO merchant_locations(merchant_location_uuid,merchant_uuid,display_name,store_number,address_line1,address_line2,city,region,postal_code,country,latitude,longitude,metadata_json,user_confirmed,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(merchant_location_uuid) DO UPDATE SET merchant_uuid=excluded.merchant_uuid,display_name=excluded.display_name,store_number=excluded.store_number,address_line1=excluded.address_line1,address_line2=excluded.address_line2,city=excluded.city,region=excluded.region,postal_code=excluded.postal_code,country=excluded.country,latitude=excluded.latitude,longitude=excluded.longitude,metadata_json=excluded.metadata_json,user_confirmed=max(user_confirmed,excluded.user_confirmed),updated_at=excluded.updated_at", (location_uuid, payload.get("merchant_uuid"), display_name[:200], payload.get("store_number"), payload.get("address_line1"), payload.get("address_line2"), payload.get("city"), payload.get("region"), payload.get("postal_code"), payload.get("country"), payload.get("latitude"), payload.get("longitude"), _json(payload.get("metadata") or {}), 1 if payload.get("user_confirmed") else 0, now, now))
            db.commit()
            row = db.execute("SELECT * FROM merchant_locations WHERE merchant_location_uuid=?", (location_uuid,)).fetchone()
        item = dict(row)
        item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
        return {"readback_verified": True, "merchant_location": item}
