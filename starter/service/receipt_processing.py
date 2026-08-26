"""Durable receipt-processing queue shared by self-hosted MIRROR workers and MIRA.

Receipt capture is intentionally independent from model execution. Originals land in
MIRROR first, then deterministic OCR/text parsing and later MIRA reconciliation can
advance the same queue without requiring an OpenAI API key or a separate model bill.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request

from receipts import parse_receipt_text

PARSER_VERSION = "receipt-deterministic-v1"
ACTIVE_STATUSES = ("queued", "processing", "needs_review")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def install_receipt_processing(app: Any, core_module: Any) -> None:
    """Install queue schema and receipt-processing APIs after receipt tables exist."""

    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS receipt_processing (
              receipt_uuid TEXT PRIMARY KEY,
              evidence_uuid TEXT,
              evidence_sha256 TEXT,
              stage TEXT NOT NULL DEFAULT 'captured',
              status TEXT NOT NULL DEFAULT 'queued',
              source_kind TEXT NOT NULL DEFAULT 'unknown',
              extracted_text TEXT,
              extracted_text_sha256 TEXT,
              parser_version TEXT,
              attempts INTEGER NOT NULL DEFAULT 0,
              next_attempt_at TEXT,
              last_error TEXT,
              claimed_by TEXT,
              claimed_at TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              completed_at TEXT,
              FOREIGN KEY(receipt_uuid) REFERENCES receipts(receipt_uuid)
            );
            CREATE INDEX IF NOT EXISTS idx_receipt_processing_status
              ON receipt_processing(status, next_attempt_at, updated_at);

            CREATE TRIGGER IF NOT EXISTS queue_receipt_processing_insert
            AFTER INSERT ON receipts
            BEGIN
              INSERT OR IGNORE INTO receipt_processing(
                receipt_uuid, stage, status, created_at, updated_at
              ) VALUES(NEW.receipt_uuid, 'captured', 'queued', NEW.created_at, NEW.updated_at);
            END;

            CREATE TRIGGER IF NOT EXISTS queue_receipt_evidence_insert
            AFTER INSERT ON receipt_evidence
            BEGIN
              INSERT INTO receipt_processing(
                receipt_uuid, evidence_uuid, evidence_sha256, stage, status,
                source_kind, created_at, updated_at
              ) VALUES(
                NEW.receipt_uuid, NEW.evidence_uuid, NEW.sha256, 'captured', 'queued',
                CASE
                  WHEN lower(NEW.mime_type) LIKE 'image/%' THEN 'image'
                  WHEN lower(NEW.mime_type) = 'application/pdf' THEN 'pdf'
                  ELSE 'file'
                END,
                NEW.created_at, NEW.created_at
              )
              ON CONFLICT(receipt_uuid) DO UPDATE SET
                evidence_uuid=excluded.evidence_uuid,
                evidence_sha256=excluded.evidence_sha256,
                source_kind=excluded.source_kind,
                updated_at=excluded.updated_at;
            END;
            """
        )
        db.execute(
            "INSERT OR IGNORE INTO receipt_processing(receipt_uuid,stage,status,created_at,updated_at) "
            "SELECT receipt_uuid,'captured','queued',created_at,updated_at FROM receipts"
        )
        db.execute(
            "UPDATE receipt_processing SET evidence_uuid=(SELECT evidence_uuid FROM receipt_evidence e WHERE e.receipt_uuid=receipt_processing.receipt_uuid ORDER BY created_at LIMIT 1), "
            "evidence_sha256=(SELECT sha256 FROM receipt_evidence e WHERE e.receipt_uuid=receipt_processing.receipt_uuid ORDER BY created_at LIMIT 1) "
            "WHERE evidence_uuid IS NULL"
        )
        db.commit()

    def readback(db: sqlite3.Connection, receipt_uuid: str) -> dict[str, Any]:
        row = db.execute("SELECT * FROM receipt_processing WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "receipt processing row not found")
        result = dict(row)
        result["readback_verified"] = True
        return result

    def replace_deterministic_lines(db: sqlite3.Connection, receipt_uuid: str, parsed: dict[str, Any]) -> None:
        receipt = db.execute("SELECT status FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
        if not receipt:
            raise HTTPException(404, "receipt not found")
        if receipt["status"] in {"reconciled", "complete"}:
            raise HTTPException(409, "receipt is already reconciled; reopen it before replacing parsed lines")

        now = _now()
        db.execute("DELETE FROM receipt_lines WHERE receipt_uuid=?", (receipt_uuid,))
        for offset, item in enumerate(parsed.get("lines") or []):
            line_uuid = str(__import__("uuid").uuid4())
            db.execute(
                "INSERT INTO receipt_lines(receipt_line_uuid,receipt_uuid,line_index,description,retailer_sku,quantity,unit_price,amount,status,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    line_uuid,
                    receipt_uuid,
                    int(item.get("line_index", offset)),
                    str(item.get("description") or "").strip()[:500],
                    str(item.get("retailer_sku") or "").strip() or None,
                    float(item.get("quantity") or 1),
                    item.get("unit_price"),
                    item.get("amount"),
                    "unmatched",
                    now,
                    now,
                ),
            )
        db.execute(
            "UPDATE receipts SET merchant=CASE WHEN ?<>'' THEN ? ELSE merchant END, "
            "purchase_at=COALESCE(?,purchase_at), currency=COALESCE(?,currency), "
            "total=COALESCE(?,total), raw_extract_json=?, status='parsed', updated_at=? WHERE receipt_uuid=?",
            (
                str(parsed.get("merchant") or "").strip(),
                str(parsed.get("merchant") or "").strip(),
                parsed.get("purchase_at"),
                parsed.get("currency") or "USD",
                parsed.get("total"),
                json.dumps(parsed, separators=(",", ":"), sort_keys=True),
                now,
                receipt_uuid,
            ),
        )

    @app.get("/v1/receipt-processing/pending")
    def list_pending_receipt_processing(limit: int = 25) -> dict[str, Any]:
        safe_limit = min(max(int(limit), 1), 100)
        with connect() as db:
            rows = [dict(row) for row in db.execute(
                "SELECT * FROM receipt_processing WHERE status IN ('queued','processing','needs_review') "
                "ORDER BY COALESCE(next_attempt_at,created_at),updated_at LIMIT ?",
                (safe_limit,),
            )]
        return {"items": rows, "count": len(rows), "openai_api_required": False}

    @app.get("/v1/receipt-processing/{receipt_uuid}")
    def receipt_processing_status(receipt_uuid: str) -> dict[str, Any]:
        with connect() as db:
            return {"processing": readback(db, receipt_uuid)}

    @app.post("/v1/receipt-processing/{receipt_uuid}/claim")
    async def claim_receipt_processing(receipt_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        worker = str(payload.get("worker") or "mira").strip()[:120]
        with connect() as db:
            if not db.execute("SELECT 1 FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone():
                raise HTTPException(404, "receipt not found")
            now = _now()
            db.execute(
                "UPDATE receipt_processing SET status='processing',claimed_by=?,claimed_at=?,attempts=attempts+1,updated_at=?,last_error=NULL WHERE receipt_uuid=?",
                (worker, now, now, receipt_uuid),
            )
            db.commit()
            return {"processing": readback(db, receipt_uuid)}

    @app.post("/v1/receipt-processing/{receipt_uuid}/extracted-text")
    async def submit_extracted_receipt_text(receipt_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        raw_text = str(payload.get("raw_text") or "").strip()
        if not raw_text:
            raise HTTPException(400, "extracted receipt text is required")
        source = str(payload.get("source") or "local_ocr").strip()[:80]
        merchant_hint = str(payload.get("merchant_hint") or "").strip()[:120]
        parsed = parse_receipt_text(raw_text, merchant_hint)
        now = _now()
        with connect() as db:
            replace_deterministic_lines(db, receipt_uuid, parsed)
            db.execute(
                "UPDATE receipt_processing SET stage='parsed',status='needs_review',source_kind=?,extracted_text=?,extracted_text_sha256=?,parser_version=?,updated_at=?,last_error=NULL WHERE receipt_uuid=?",
                (source, raw_text, _sha256_text(raw_text), PARSER_VERSION, now, receipt_uuid),
            )
            db.commit()
            processing = readback(db, receipt_uuid)
            line_count = db.execute("SELECT COUNT(*) AS n FROM receipt_lines WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()["n"]
        return {
            "processing": processing,
            "parsed_line_count": line_count,
            "openai_api_required": False,
            "next_step": "MIRA may reconcile ambiguous line identities using the same MIRROR record; deterministic fields are already persisted.",
        }

    @app.post("/v1/receipt-processing/{receipt_uuid}/result")
    async def record_receipt_processing_result(receipt_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        outcome = str(payload.get("outcome") or "needs_review").strip().lower()
        if outcome not in {"needs_review", "complete", "failed"}:
            raise HTTPException(400, "outcome must be needs_review, complete, or failed")
        now = _now()
        status = outcome
        completed_at = now if outcome == "complete" else None
        last_error = str(payload.get("error") or "").strip() or None
        with connect() as db:
            db.execute(
                "UPDATE receipt_processing SET stage=?,status=?,last_error=?,next_attempt_at=?,updated_at=?,completed_at=? WHERE receipt_uuid=?",
                (
                    "complete" if outcome == "complete" else "reconcile",
                    status,
                    last_error,
                    payload.get("next_attempt_at"),
                    now,
                    completed_at,
                    receipt_uuid,
                ),
            )
            if db.total_changes == 0:
                raise HTTPException(404, "receipt processing row not found")
            if outcome == "complete":
                db.execute("UPDATE receipts SET status='complete',updated_at=? WHERE receipt_uuid=?", (now, receipt_uuid))
            db.commit()
            return {"processing": readback(db, receipt_uuid)}
