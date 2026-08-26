from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse


MONEY_RE = re.compile(r"(?<!\d)(-?\$?\d{1,7}(?:,\d{3})*\.\d{2})(?!\d)")
DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-](?:\d{2}|\d{4}))\b")
SKU_RE = re.compile(r"\b(?:SKU|ITEM|ITEM#|ITEM NO|UPC|ID)\s*[:#-]?\s*([A-Z0-9-]{4,24})\b", re.I)
TOTAL_WORDS = ("GRAND TOTAL", "AMOUNT DUE", "BALANCE DUE", "TOTAL")
NON_ITEM_WORDS = ("SUBTOTAL", "TAX", "CHANGE", "CASH", "VISA", "MASTERCARD", "DEBIT", "CREDIT", "TENDER", "SAVINGS")

KNOWN_RETAILERS = {
    "walmart": "walmart.com",
    "wal-mart": "walmart.com",
    "target": "target.com",
    "home depot": "homedepot.com",
    "the home depot": "homedepot.com",
    "lowe's": "lowes.com",
    "lowes": "lowes.com",
    "best buy": "bestbuy.com",
    "northern tool": "northerntool.com",
    "harbor freight": "harborfreight.com",
    "amazon": "amazon.com",
    "autozone": "autozone.com",
    "advance auto": "shop.advanceautoparts.com",
    "oreilly": "oreillyauto.com",
    "o'reilly": "oreillyauto.com",
}

CATEGORY_RULES = {
    "Tools": ("wrench", "socket", "ratchet", "hammer", "drill", "saw", "bit", "plier", "clamp", "tool"),
    "Automotive": ("tire", "wheel", "brake", "filter", "motor oil", "spark plug", "automotive", "car part", "lug", "bearing"),
    "Electronics": ("usb", "charger", "cable", "adapter", "router", "switch", "keyboard", "mouse", "tablet", "monitor", "electronics"),
    "Household": ("tote", "storage", "bin", "kitchen", "bath", "cleaner", "vacuum", "furniture", "appliance", "household"),
    "Lawn & Garden": ("mower", "trimmer", "garden", "lawn", "hose", "fertilizer", "seed", "shovel"),
    "Consumables": ("food", "drink", "snack", "paper towel", "detergent", "soap", "shampoo", "cleaning supply"),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


def _money(value: str | float | int | None) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def _slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return text or "retailer"


def _domain_for_merchant(merchant: str) -> str | None:
    low = merchant.lower().strip()
    for key, domain in KNOWN_RETAILERS.items():
        if key in low:
            return domain
    return None


def _guess_category(*values: Any) -> str | None:
    text = " ".join(str(value or "") for value in values).lower()
    for category, words in CATEGORY_RULES.items():
        if any(word in text for word in words):
            return category
    return None


def parse_receipt_text(raw_text: str, merchant_hint: str = "") -> dict[str, Any]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in str(raw_text or "").splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        raise HTTPException(400, "receipt text is empty")

    merchant = merchant_hint.strip() or lines[0][:120]
    date_value = None
    for line in lines[:12]:
        match = DATE_RE.search(line)
        if match:
            date_value = match.group(1)
            break

    total = None
    for line in reversed(lines):
        upper = line.upper()
        if any(word in upper for word in TOTAL_WORDS):
            values = MONEY_RE.findall(line)
            if values:
                total = _money(values[-1])
                break

    parsed_lines: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        upper = line.upper()
        if any(word in upper for word in NON_ITEM_WORDS) or any(word in upper for word in TOTAL_WORDS):
            continue
        values = MONEY_RE.findall(line)
        if not values:
            continue
        amount_token = values[-1]
        amount = _money(amount_token)
        if amount is None:
            continue
        description = line[: line.rfind(amount_token)].strip(" -.:$")
        if len(description) < 2:
            continue
        sku_match = SKU_RE.search(line)
        retailer_sku = sku_match.group(1).upper() if sku_match else None
        if not retailer_sku:
            leading = re.match(r"^([A-Z0-9-]{6,18})\s+(.+)$", description, re.I)
            if leading and any(ch.isdigit() for ch in leading.group(1)):
                retailer_sku = leading.group(1).upper()
                description = leading.group(2).strip()
        parsed_lines.append(
            {
                "line_index": index,
                "description": description[:240],
                "retailer_sku": retailer_sku,
                "quantity": 1.0,
                "unit_price": amount,
                "amount": amount,
            }
        )

    return {
        "merchant": merchant,
        "purchase_at": date_value,
        "currency": "USD",
        "total": total,
        "lines": parsed_lines,
        "raw_text": raw_text,
    }


def install_receipts(app: Any, core_module: Any) -> None:
    receipt_dir = Path(core_module.EVIDENCE_DIR) / "receipts"

    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS receipts (
              receipt_uuid TEXT PRIMARY KEY,
              merchant TEXT NOT NULL DEFAULT '',
              purchase_at TEXT,
              currency TEXT NOT NULL DEFAULT 'USD',
              subtotal REAL,
              tax REAL,
              total REAL,
              raw_extract_json TEXT NOT NULL DEFAULT '{}',
              status TEXT NOT NULL DEFAULT 'captured',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS receipt_lines (
              receipt_line_uuid TEXT PRIMARY KEY,
              receipt_uuid TEXT NOT NULL,
              line_index INTEGER NOT NULL,
              description TEXT NOT NULL,
              retailer_sku TEXT,
              quantity REAL NOT NULL DEFAULT 1,
              unit_price REAL,
              amount REAL,
              asset_uuid TEXT,
              status TEXT NOT NULL DEFAULT 'unmatched',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(receipt_uuid) REFERENCES receipts(receipt_uuid),
              FOREIGN KEY(asset_uuid) REFERENCES assets(uuid)
            );
            CREATE INDEX IF NOT EXISTS idx_receipt_lines_receipt ON receipt_lines(receipt_uuid,line_index);
            CREATE TABLE IF NOT EXISTS receipt_line_candidates (
              candidate_uuid TEXT PRIMARY KEY,
              receipt_line_uuid TEXT NOT NULL,
              source_url TEXT NOT NULL,
              source_domain TEXT NOT NULL,
              official_source INTEGER NOT NULL DEFAULT 0,
              title TEXT,
              brand TEXT,
              model TEXT,
              manufacturer_part_number TEXT,
              gtin TEXT,
              retailer_sku TEXT,
              category TEXT,
              confidence REAL NOT NULL,
              match_basis TEXT NOT NULL,
              candidate_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(receipt_line_uuid) REFERENCES receipt_lines(receipt_line_uuid)
            );
            CREATE INDEX IF NOT EXISTS idx_receipt_candidates_line ON receipt_line_candidates(receipt_line_uuid,confidence DESC);
            CREATE TABLE IF NOT EXISTS receipt_evidence (
              evidence_uuid TEXT PRIMARY KEY,
              receipt_uuid TEXT NOT NULL,
              filename TEXT NOT NULL,
              mime_type TEXT NOT NULL,
              sha256 TEXT NOT NULL,
              storage_path TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(receipt_uuid) REFERENCES receipts(receipt_uuid)
            );
            """
        )
        db.commit()

    def _receipt_readback(db: sqlite3.Connection, receipt_uuid: str) -> dict[str, Any]:
        row = db.execute("SELECT * FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "receipt not found")
        result = dict(row)
        result["raw_extract"] = json.loads(result.pop("raw_extract_json") or "{}")
        lines = [dict(item) for item in db.execute("SELECT * FROM receipt_lines WHERE receipt_uuid=? ORDER BY line_index,receipt_line_uuid", (receipt_uuid,))]
        for line in lines:
            line["candidates"] = [dict(candidate) for candidate in db.execute(
                "SELECT candidate_uuid,source_url,source_domain,official_source,title,brand,model,manufacturer_part_number,gtin,retailer_sku,category,confidence,match_basis,created_at FROM receipt_line_candidates WHERE receipt_line_uuid=? ORDER BY confidence DESC,created_at",
                (line["receipt_line_uuid"],),
            )]
        result["lines"] = lines
        result["evidence"] = [dict(item) for item in db.execute(
            "SELECT evidence_uuid,filename,mime_type,sha256,created_at FROM receipt_evidence WHERE receipt_uuid=? ORDER BY created_at",
            (receipt_uuid,),
        )]
        return result

    def _write_draft(db: sqlite3.Connection, payload: dict[str, Any], receipt_uuid: str | None = None) -> str:
        receipt_uuid = receipt_uuid or str(payload.get("receipt_uuid") or _uuid())
        now = _now()
        merchant = str(payload.get("merchant") or "").strip()
        raw_extract = payload.get("raw_extract") or {key: value for key, value in payload.items() if key != "lines"}
        db.execute(
            "INSERT INTO receipts(receipt_uuid,merchant,purchase_at,currency,subtotal,tax,total,raw_extract_json,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(receipt_uuid) DO UPDATE SET merchant=excluded.merchant,purchase_at=excluded.purchase_at,currency=excluded.currency,subtotal=excluded.subtotal,tax=excluded.tax,total=excluded.total,raw_extract_json=excluded.raw_extract_json,updated_at=excluded.updated_at",
            (
                receipt_uuid,
                merchant,
                str(payload.get("purchase_at") or "").strip() or None,
                str(payload.get("currency") or "USD").upper(),
                _money(payload.get("subtotal")),
                _money(payload.get("tax")),
                _money(payload.get("total")),
                json.dumps(raw_extract, separators=(",", ":"), sort_keys=True),
                str(payload.get("status") or "captured"),
                now,
                now,
            ),
        )
        for offset, item in enumerate(payload.get("lines") or []):
            if not isinstance(item, dict):
                continue
            line_uuid = str(item.get("receipt_line_uuid") or _uuid())
            db.execute(
                "INSERT INTO receipt_lines(receipt_line_uuid,receipt_uuid,line_index,description,retailer_sku,quantity,unit_price,amount,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    line_uuid,
                    receipt_uuid,
                    int(item.get("line_index", offset)),
                    str(item.get("description") or "").strip()[:500],
                    str(item.get("retailer_sku") or "").strip() or None,
                    float(item.get("quantity") or 1),
                    _money(item.get("unit_price")),
                    _money(item.get("amount")),
                    "unmatched",
                    now,
                    now,
                ),
            )
        return receipt_uuid

    def _add_candidate(db: sqlite3.Connection, line_uuid: str, candidate: dict[str, Any]) -> str:
        if not db.execute("SELECT 1 FROM receipt_lines WHERE receipt_line_uuid=?", (line_uuid,)).fetchone():
            raise HTTPException(404, "receipt line not found")
        source_url = str(candidate.get("source_url") or "").strip()
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise HTTPException(400, "candidate source_url must be an http(s) URL")
        confidence = float(candidate.get("confidence") or 0)
        if confidence < 0 or confidence > 1:
            raise HTTPException(400, "candidate confidence must be between 0 and 1")
        candidate_uuid = _uuid()
        db.execute(
            "INSERT INTO receipt_line_candidates(candidate_uuid,receipt_line_uuid,source_url,source_domain,official_source,title,brand,model,manufacturer_part_number,gtin,retailer_sku,category,confidence,match_basis,candidate_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                candidate_uuid,
                line_uuid,
                source_url,
                parsed.netloc.lower(),
                1 if candidate.get("official_source") else 0,
                str(candidate.get("title") or "").strip() or None,
                str(candidate.get("brand") or "").strip() or None,
                str(candidate.get("model") or "").strip() or None,
                str(candidate.get("manufacturer_part_number") or candidate.get("mpn") or "").strip() or None,
                re.sub(r"\D", "", str(candidate.get("gtin") or "")) or None,
                str(candidate.get("retailer_sku") or "").strip() or None,
                str(candidate.get("category") or "").strip() or None,
                confidence,
                str(candidate.get("match_basis") or "model_supplied_candidate").strip(),
                json.dumps(candidate, separators=(",", ":"), sort_keys=True),
                _now(),
            ),
        )
        return candidate_uuid

    def _ensure_category(db: sqlite3.Connection, name: str | None) -> str | None:
        if not name:
            return None
        row = db.execute("SELECT uuid FROM categories WHERE lower(name)=lower(?) LIMIT 1", (name,)).fetchone()
        if row:
            return row["uuid"]
        category_uuid = _uuid()
        now = _now()
        db.execute("INSERT INTO categories(uuid,name,parent_uuid,created_at,updated_at) VALUES(?,?,?,?,?)", (category_uuid, name[:120], None, now, now))
        return category_uuid

    def _assign_identifier(db: sqlite3.Connection, asset_uuid: str, namespace: str, value: str | None) -> tuple[bool, str | None]:
        value = str(value or "").strip()
        if not value:
            return True, None
        existing = db.execute("SELECT asset_uuid FROM identifiers WHERE namespace=? AND value=?", (namespace, value)).fetchone()
        if existing and existing["asset_uuid"] != asset_uuid:
            return False, f"{namespace}:{value} already belongs to another live asset"
        if not existing:
            db.execute("INSERT INTO identifiers(namespace,value,asset_uuid,created_at) VALUES(?,?,?,?)", (namespace, value, asset_uuid, _now()))
        return True, None

    def _apply_candidate(db: sqlite3.Connection, receipt: sqlite3.Row, line: sqlite3.Row, candidate: sqlite3.Row) -> dict[str, Any]:
        title = str(candidate["title"] or line["description"] or "Receipt item").strip()
        category = candidate["category"] or _guess_category(title, candidate["brand"], candidate["model"], line["description"])
        category_uuid = _ensure_category(db, category)
        asset_uuid = line["asset_uuid"] or _uuid()
        if not line["asset_uuid"]:
            metadata = {
                "brand": candidate["brand"],
                "model": candidate["model"],
                "manufacturer_part_number": candidate["manufacturer_part_number"],
                "receipt_uuid": receipt["receipt_uuid"],
                "receipt_line_uuid": line["receipt_line_uuid"],
                "enrichment_source_url": candidate["source_url"],
                "enrichment_confidence": candidate["confidence"],
                "enrichment_verified": True,
            }
            now = _now()
            db.execute(
                "INSERT INTO assets(uuid,name,description,category_uuid,location_uuid,status,metadata_json,created_at,updated_at) VALUES(?,?,?,?,?,'active',?,?,?)",
                (asset_uuid, title[:240], line["description"] or "", category_uuid, None, json.dumps(metadata, separators=(",", ":"), sort_keys=True), now, now),
            )
        retailer_namespace = f"retailer:{_slug(receipt['merchant'])}:sku"
        identifiers = [
            (retailer_namespace, candidate["retailer_sku"] or line["retailer_sku"]),
            ("gtin", candidate["gtin"]),
            ("model", candidate["model"]),
            ("mpn", candidate["manufacturer_part_number"]),
        ]
        conflicts = []
        for namespace, value in identifiers:
            ok, message = _assign_identifier(db, asset_uuid, namespace, value)
            if not ok and message:
                conflicts.append(message)
        if conflicts:
            return {"applied": False, "reason": "identifier_conflict", "conflicts": conflicts}
        db.execute("UPDATE receipt_lines SET asset_uuid=?,status='matched',updated_at=? WHERE receipt_line_uuid=?", (asset_uuid, _now(), line["receipt_line_uuid"]))
        return {"applied": True, "asset_uuid": asset_uuid, "category": category, "source_url": candidate["source_url"]}

    @app.post("/v1/receipts/parse-text")
    async def receipt_parse_text(request: Request) -> dict[str, Any]:
        payload = await request.json()
        parsed = parse_receipt_text(str(payload.get("raw_text") or ""), str(payload.get("merchant_hint") or ""))
        with connect() as db:
            receipt_uuid = _write_draft(db, parsed)
            db.commit()
            result = _receipt_readback(db, receipt_uuid)
        return {"readback_verified": True, "receipt": result, "next_step": "research receipt lines against official retailer/manufacturer sources, then call reconcile"}

    @app.post("/v1/receipts/draft")
    async def receipt_draft(request: Request) -> dict[str, Any]:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(400, "receipt object is required")
        with connect() as db:
            receipt_uuid = _write_draft(db, payload)
            db.commit()
            result = _receipt_readback(db, receipt_uuid)
        return {"readback_verified": True, "receipt": result}

    @app.post("/v1/receipts/upload")
    async def receipt_upload(file: UploadFile = File(...)) -> dict[str, Any]:
        raw = await file.read()
        if not raw:
            raise HTTPException(400, "receipt file is empty")
        if len(raw) > 25 * 1024 * 1024:
            raise HTTPException(413, "receipt file exceeds 25 MiB")
        receipt_uuid = _uuid()
        evidence_uuid = _uuid()
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", file.filename or "receipt")[:180]
        receipt_dir.mkdir(parents=True, exist_ok=True)
        target = receipt_dir / f"{evidence_uuid}-{safe_name}"
        target.write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        now = _now()
        with connect() as db:
            db.execute("INSERT INTO receipts(receipt_uuid,status,created_at,updated_at) VALUES(?,'captured',?,?)", (receipt_uuid, now, now))
            db.execute(
                "INSERT INTO receipt_evidence(evidence_uuid,receipt_uuid,filename,mime_type,sha256,storage_path,created_at) VALUES(?,?,?,?,?,?,?)",
                (evidence_uuid, receipt_uuid, safe_name, file.content_type or "application/octet-stream", digest, str(target), now),
            )
            db.commit()
            result = _receipt_readback(db, receipt_uuid)
        return {
            "readback_verified": True,
            "receipt": result,
            "ocr_status": "not_run",
            "next_step": "In ChatGPT-native mode, ask MIRA to reconcile this receipt using the image; hosted deployments may submit extracted text/structure to the receipt draft endpoints.",
        }

    @app.get("/v1/receipts/{receipt_uuid}")
    def receipt_get(receipt_uuid: str) -> dict[str, Any]:
        with connect() as db:
            return {"receipt": _receipt_readback(db, receipt_uuid)}

    @app.get("/v1/receipts/{receipt_uuid}/evidence/{evidence_uuid}")
    def receipt_file(receipt_uuid: str, evidence_uuid: str) -> FileResponse:
        with connect() as db:
            row = db.execute("SELECT * FROM receipt_evidence WHERE receipt_uuid=? AND evidence_uuid=?", (receipt_uuid, evidence_uuid)).fetchone()
        if not row:
            raise HTTPException(404, "receipt evidence not found")
        path = Path(row["storage_path"])
        if not path.is_file():
            raise HTTPException(410, "receipt evidence storage is unavailable")
        return FileResponse(path, media_type=row["mime_type"], filename=row["filename"])

    @app.post("/v1/receipts/{receipt_uuid}/lines/{line_uuid}/candidates")
    async def receipt_candidate(receipt_uuid: str, line_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        with connect() as db:
            if not db.execute("SELECT 1 FROM receipt_lines WHERE receipt_uuid=? AND receipt_line_uuid=?", (receipt_uuid, line_uuid)).fetchone():
                raise HTTPException(404, "receipt line not found")
            candidate_uuid = _add_candidate(db, line_uuid, payload)
            db.commit()
        return {"readback_verified": True, "candidate_uuid": candidate_uuid}

    @app.get("/v1/receipts/{receipt_uuid}/retailer-search-plan")
    def retailer_search_plan(receipt_uuid: str) -> dict[str, Any]:
        with connect() as db:
            receipt = db.execute("SELECT * FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
            if not receipt:
                raise HTTPException(404, "receipt not found")
            lines = db.execute("SELECT * FROM receipt_lines WHERE receipt_uuid=? ORDER BY line_index", (receipt_uuid,)).fetchall()
        domain = _domain_for_merchant(receipt["merchant"])
        plans = []
        for line in lines:
            parts = [line["retailer_sku"], line["description"]]
            query = " ".join(str(value) for value in parts if value).strip()
            plans.append(
                {
                    "receipt_line_uuid": line["receipt_line_uuid"],
                    "official_domain": domain,
                    "official_query": f"site:{domain} {query}" if domain else query,
                    "fallback_query": f"{receipt['merchant']} {query}".strip(),
                    "rule": "official retailer first, then manufacturer/other web evidence; record provenance and confidence",
                }
            )
        return {"merchant": receipt["merchant"], "official_domain": domain, "search_plan": plans}

    @app.post("/v1/receipts/{receipt_uuid}/reconcile")
    async def receipt_reconcile(receipt_uuid: str, request: Request) -> dict[str, Any]:
        payload = await request.json()
        candidates_by_line = payload.get("candidates_by_line") or {}
        auto_apply = bool(payload.get("auto_apply_high_confidence", True))
        threshold = float(payload.get("confidence_threshold", 0.92))
        margin = float(payload.get("minimum_margin", 0.08))
        if threshold < 0.5 or threshold > 1 or margin < 0 or margin > 1:
            raise HTTPException(400, "invalid reconciliation threshold")

        with connect() as db:
            receipt = db.execute("SELECT * FROM receipts WHERE receipt_uuid=?", (receipt_uuid,)).fetchone()
            if not receipt:
                raise HTTPException(404, "receipt not found")
            line_rows = db.execute("SELECT * FROM receipt_lines WHERE receipt_uuid=? ORDER BY line_index", (receipt_uuid,)).fetchall()
            for line in line_rows:
                incoming = candidates_by_line.get(line["receipt_line_uuid"], []) if isinstance(candidates_by_line, dict) else []
                for candidate in incoming if isinstance(incoming, list) else []:
                    if isinstance(candidate, dict):
                        _add_candidate(db, line["receipt_line_uuid"], candidate)
            db.commit()

            applied: list[dict[str, Any]] = []
            review: list[dict[str, Any]] = []
            line_rows = db.execute("SELECT * FROM receipt_lines WHERE receipt_uuid=? ORDER BY line_index", (receipt_uuid,)).fetchall()
            for line in line_rows:
                candidates = db.execute(
                    "SELECT * FROM receipt_line_candidates WHERE receipt_line_uuid=? ORDER BY confidence DESC,official_source DESC,created_at",
                    (line["receipt_line_uuid"],),
                ).fetchall()
                if not candidates:
                    review.append({"receipt_line_uuid": line["receipt_line_uuid"], "description": line["description"], "reason": "no_candidate"})
                    continue
                best = candidates[0]
                second_confidence = float(candidates[1]["confidence"]) if len(candidates) > 1 else -1.0
                unique = float(best["confidence"]) - second_confidence >= margin
                safe = bool(best["official_source"]) and float(best["confidence"]) >= threshold and unique
                if auto_apply and safe:
                    result = _apply_candidate(db, receipt, line, best)
                    if result.get("applied"):
                        applied.append({"receipt_line_uuid": line["receipt_line_uuid"], **result})
                    else:
                        review.append({"receipt_line_uuid": line["receipt_line_uuid"], "description": line["description"], **result})
                else:
                    review.append(
                        {
                            "receipt_line_uuid": line["receipt_line_uuid"],
                            "description": line["description"],
                            "reason": "ambiguous_or_unverified",
                            "best_candidate": {"title": best["title"], "source_url": best["source_url"], "confidence": best["confidence"], "official_source": bool(best["official_source"])},
                        }
                    )

            amounts = [float(row["amount"]) for row in line_rows if row["amount"] is not None]
            lines_total = round(sum(amounts), 2) if amounts else None
            receipt_total = float(receipt["total"]) if receipt["total"] is not None else None
            variance = round(receipt_total - lines_total, 2) if receipt_total is not None and lines_total is not None else None
            balanced = variance is not None and abs(variance) <= 0.02
            status = "reconciled" if not review and (balanced or receipt_total is None) else "needs_review"
            db.execute("UPDATE receipts SET status=?,updated_at=? WHERE receipt_uuid=?", (status, _now(), receipt_uuid))
            db.commit()
            readback = _receipt_readback(db, receipt_uuid)

        return {
            "readback_verified": True,
            "receipt": readback,
            "applied": applied,
            "needs_review": review,
            "allocation": {"receipt_total": receipt_total, "line_total": lines_total, "variance": variance, "balanced": balanced},
            "policy": "unique high-confidence official matches may auto-apply; ambiguity, identity collisions and receipt-total mismatches remain open",
        }
