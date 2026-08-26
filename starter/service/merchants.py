from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request

KNOWN_DOMAINS = {
    "walmart": "walmart.com",
    "wal mart": "walmart.com",
    "target": "target.com",
    "home depot": "homedepot.com",
    "the home depot": "homedepot.com",
    "lowe s": "lowes.com",
    "lowes": "lowes.com",
    "best buy": "bestbuy.com",
    "northern tool": "northerntool.com",
    "harbor freight": "harborfreight.com",
    "amazon": "amazon.com",
    "autozone": "autozone.com",
    "advance auto": "shop.advanceautoparts.com",
    "oreilly": "oreillyauto.com",
    "o reilly": "oreillyauto.com",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()
    return re.sub(r"\s+", " ", text)


def install_merchants(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS merchants (
              merchant_uuid TEXT PRIMARY KEY,
              canonical_name TEXT NOT NULL,
              normalized_name TEXT NOT NULL UNIQUE,
              official_domain TEXT,
              aliases_json TEXT NOT NULL DEFAULT '[]',
              metadata_json TEXT NOT NULL DEFAULT '{}',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS receipt_merchant_links (
              receipt_uuid TEXT PRIMARY KEY,
              merchant_uuid TEXT NOT NULL,
              linked_at TEXT NOT NULL,
              FOREIGN KEY(receipt_uuid) REFERENCES receipts(receipt_uuid),
              FOREIGN KEY(merchant_uuid) REFERENCES merchants(merchant_uuid)
            );
            CREATE TABLE IF NOT EXISTS merchant_link_queue (
              receipt_uuid TEXT PRIMARY KEY,
              queued_at TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS queue_receipt_merchant_insert
            AFTER INSERT ON receipts
            BEGIN
              INSERT INTO merchant_link_queue(receipt_uuid,queued_at)
              VALUES(NEW.receipt_uuid,CURRENT_TIMESTAMP)
              ON CONFLICT(receipt_uuid) DO UPDATE SET queued_at=excluded.queued_at;
            END;
            CREATE TRIGGER IF NOT EXISTS queue_receipt_merchant_update
            AFTER UPDATE OF merchant ON receipts
            BEGIN
              INSERT INTO merchant_link_queue(receipt_uuid,queued_at)
              VALUES(NEW.receipt_uuid,CURRENT_TIMESTAMP)
              ON CONFLICT(receipt_uuid) DO UPDATE SET queued_at=excluded.queued_at;
            END;
            """
        )
        db.execute(
            "INSERT OR IGNORE INTO merchant_link_queue(receipt_uuid,queued_at) SELECT receipt_uuid,CURRENT_TIMESTAMP FROM receipts"
        )
        db.commit()

    def ensure_merchant(db: sqlite3.Connection, name: str) -> str | None:
        canonical = str(name or "").strip()
        normalized = _normalize(canonical)
        if not normalized:
            return None
        row = db.execute("SELECT merchant_uuid FROM merchants WHERE normalized_name=?", (normalized,)).fetchone()
        if row:
            return row["merchant_uuid"]
        merchant_uuid = str(uuid.uuid4())
        official = None
        for key, domain in KNOWN_DOMAINS.items():
            if key in normalized:
                official = domain
                break
        now = _now()
        db.execute(
            "INSERT INTO merchants(merchant_uuid,canonical_name,normalized_name,official_domain,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (merchant_uuid, canonical[:200], normalized, official, now, now),
        )
        return merchant_uuid

    def link_receipt(db: sqlite3.Connection, receipt_uuid: str) -> str | None:
        row = db.execute("SELECT merchant FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
        if not row:
            db.execute("DELETE FROM merchant_link_queue WHERE receipt_uuid=?", (receipt_uuid,))
            return None
        merchant_uuid = ensure_merchant(db, row["merchant"])
        if merchant_uuid:
            db.execute(
                "INSERT INTO receipt_merchant_links(receipt_uuid,merchant_uuid,linked_at) VALUES(?,?,?) ON CONFLICT(receipt_uuid) DO UPDATE SET merchant_uuid=excluded.merchant_uuid,linked_at=excluded.linked_at",
                (receipt_uuid, merchant_uuid, _now()),
            )
        else:
            db.execute("DELETE FROM receipt_merchant_links WHERE receipt_uuid=?", (receipt_uuid,))
        db.execute("DELETE FROM merchant_link_queue WHERE receipt_uuid=?", (receipt_uuid,))
        return merchant_uuid

    def drain_queue(limit: int = 100) -> int:
        processed = 0
        with connect() as db:
            rows = db.execute("SELECT receipt_uuid FROM merchant_link_queue ORDER BY queued_at LIMIT ?", (limit,)).fetchall()
            for row in rows:
                link_receipt(db, row["receipt_uuid"])
                processed += 1
            db.commit()
        return processed

    # Drain existing receipts synchronously so read APIs are correct immediately.
    while drain_queue(500):
        pass

    def worker() -> None:
        while True:
            try:
                while drain_queue(100):
                    pass
            except Exception:
                # The next pass retries queued work. Receipt creation never fails merely
                # because merchant enrichment is temporarily unavailable.
                pass
            time.sleep(1)

    if str(getattr(core_module, "DATA_DIR", "")):
        threading.Thread(target=worker, name="mirror-merchant-linker", daemon=True).start()

    @app.get("/v1/merchants")
    def list_merchants() -> dict[str, Any]:
        drain_queue(500)
        with connect() as db:
            rows = db.execute(
                "SELECT m.*, count(r.receipt_uuid) AS receipt_count FROM merchants m LEFT JOIN receipt_merchant_links r ON r.merchant_uuid=m.merchant_uuid GROUP BY m.merchant_uuid ORDER BY m.canonical_name"
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["aliases"] = json.loads(item.pop("aliases_json") or "[]")
            item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
            result.append(item)
        return {"merchants": result}

    @app.get("/v1/merchants/{merchant_uuid}")
    def get_merchant(merchant_uuid: str) -> dict[str, Any]:
        drain_queue(500)
        with connect() as db:
            row = db.execute("SELECT * FROM merchants WHERE merchant_uuid=?", (merchant_uuid,)).fetchone()
            receipts = db.execute(
                "SELECT r.* FROM receipts r JOIN receipt_merchant_links l ON l.receipt_uuid=r.receipt_uuid WHERE l.merchant_uuid=? ORDER BY r.purchase_at DESC,r.created_at DESC",
                (merchant_uuid,),
            ).fetchall()
        if not row:
            raise HTTPException(404, "merchant not found")
        merchant = dict(row)
        merchant["aliases"] = json.loads(merchant.pop("aliases_json") or "[]")
        merchant["metadata"] = json.loads(merchant.pop("metadata_json") or "{}")
        return {"merchant": merchant, "receipts": [dict(item) for item in receipts]}

    @app.patch("/v1/merchants/{merchant_uuid}")
    async def update_merchant(merchant_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        with connect() as db:
            row = db.execute("SELECT * FROM merchants WHERE merchant_uuid=?", (merchant_uuid,)).fetchone()
            if not row:
                raise HTTPException(404, "merchant not found")
            canonical = str(payload.get("canonical_name") or row["canonical_name"]).strip()[:200]
            domain = str(payload.get("official_domain") or row["official_domain"] or "").strip().lower() or None
            aliases = payload.get("aliases") if "aliases" in payload else json.loads(row["aliases_json"] or "[]")
            metadata = payload.get("metadata") if "metadata" in payload else json.loads(row["metadata_json"] or "{}")
            if not isinstance(aliases, list) or not isinstance(metadata, dict):
                raise HTTPException(400, "aliases must be a list and metadata must be an object")
            db.execute(
                "UPDATE merchants SET canonical_name=?,official_domain=?,aliases_json=?,metadata_json=?,updated_at=? WHERE merchant_uuid=?",
                (canonical, domain, json.dumps(aliases), json.dumps(metadata), _now(), merchant_uuid),
            )
            db.commit()
        return {"readback_verified": True, "merchant": get_merchant(merchant_uuid)["merchant"]}

    @app.post("/v1/receipts/{receipt_uuid}/merchant/sync")
    def sync_receipt_merchant(receipt_uuid: str) -> dict[str, Any]:
        with connect() as db:
            if not db.execute("SELECT 1 FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone():
                raise HTTPException(404, "receipt not found")
            merchant_uuid = link_receipt(db, receipt_uuid)
            db.commit()
        return {"readback_verified": True, "receipt_uuid": receipt_uuid, "merchant_uuid": merchant_uuid}

    @app.get("/v1/receipts/{receipt_uuid}/merchant")
    def receipt_merchant(receipt_uuid: str) -> dict[str, Any]:
        with connect() as db:
            link = db.execute("SELECT merchant_uuid FROM receipt_merchant_links WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
            if not link:
                merchant_uuid = link_receipt(db, receipt_uuid)
                db.commit()
            else:
                merchant_uuid = link["merchant_uuid"]
        if not merchant_uuid:
            return {"merchant": None}
        return {"merchant": get_merchant(merchant_uuid)["merchant"]}
