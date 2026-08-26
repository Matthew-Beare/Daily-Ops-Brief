from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import HTTPException, Request


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_gtin(value: str) -> str:
    gtin = re.sub(r"\D", "", str(value or ""))
    if len(gtin) not in {8, 12, 13, 14}:
        raise HTTPException(400, "GTIN/UPC/EAN must contain 8, 12, 13, or 14 digits")
    return gtin


def _normalize_identifier(namespace: str, value: str) -> tuple[str, str]:
    ns = str(namespace or "").strip().lower()
    raw = str(value or "").strip()
    if not ns or not raw:
        raise HTTPException(400, "namespace and value are required")
    if ns in {"gtin", "upc", "ean", "upc_a", "ean_13", "ean_8"}:
        raw = _normalize_gtin(raw)
        ns = "gtin"
    return ns, raw.upper() if ns in {"model", "mpn", "retailer_sku"} or ns.startswith("retailer:") else raw


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _candidate_from_payload(payload: Any) -> dict[str, Any]:
    root = payload if isinstance(payload, dict) else {}
    candidates: list[dict[str, Any]] = [root]
    for key in ("product", "item", "data", "result"):
        value = root.get(key)
        if isinstance(value, dict):
            candidates.insert(0, value)
    for key in ("products", "items", "results"):
        value = root.get(key)
        if isinstance(value, list) and value and isinstance(value[0], dict):
            candidates.insert(0, value[0])
    item = candidates[0] if candidates else {}
    images = _first(item, "images", "image_urls")
    image = _first(item, "image_url", "image", "image_front_url", "thumbnail")
    if not image and isinstance(images, list) and images:
        image = images[0]
    return {
        "name": _first(item, "name", "title", "product_name", "description"),
        "brand": _first(item, "brand", "brands", "manufacturer"),
        "model": _first(item, "model", "model_number"),
        "manufacturer_part_number": _first(item, "manufacturer_part_number", "mpn", "part_number"),
        "category": _first(item, "category", "categories", "category_name"),
        "image_url": image,
    }


def install_enrichment(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS product_enrichment_cache (
              gtin TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              candidate_json TEXT NOT NULL,
              raw_json TEXT NOT NULL,
              fetched_at TEXT NOT NULL
            )
            """
        )
        db.commit()

    def mirror_mapping(db: sqlite3.Connection, namespace: str, value: str) -> dict[str, Any] | None:
        table = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='recognition_profiles'").fetchone()
        if not table:
            return None
        key = f"{namespace}:{value}"
        row = db.execute("SELECT * FROM recognition_profiles WHERE profile_type='product_identifier' AND lookup_key=?", (key,)).fetchone()
        if not row:
            return None
        candidate = json.loads(row["value_json"] or "{}")
        if not isinstance(candidate, dict):
            return None
        return {
            "namespace": namespace,
            "value": value,
            "found": True,
            "cached": True,
            "source": "mirror_confirmed_mapping" if row["user_confirmed"] else "mirror_verified_mapping",
            "candidate": candidate,
            "confidence": float(row["confidence"]),
            "user_confirmed": bool(row["user_confirmed"]),
            "authority": "MIRROR recognition memory; user-confirmed mappings outrank AI suggestions",
        }

    @app.get("/v1/enrichment/identifier/{namespace}/{value}")
    def lookup_identifier(namespace: str, value: str) -> dict[str, Any]:
        ns, normalized = _normalize_identifier(namespace, value)
        with connect() as db:
            known = mirror_mapping(db, ns, normalized)
        if known:
            return known
        return {"namespace": ns, "value": normalized, "found": False, "candidate": None, "source": "mirror", "authority": "no confirmed MIRROR mapping exists yet"}

    @app.post("/v1/enrichment/product-mapping")
    async def save_product_mapping(request: Request) -> dict[str, Any]:
        payload = await request.json()
        ns, normalized = _normalize_identifier(str(payload.get("namespace") or ""), str(payload.get("value") or ""))
        candidate = payload.get("candidate") or {}
        if not isinstance(candidate, dict) or not str(candidate.get("name") or "").strip():
            raise HTTPException(400, "candidate with a product name is required")
        user_confirmed = bool(payload.get("user_confirmed"))
        confidence = 1.0 if user_confirmed else float(payload.get("confidence") or 0.95)
        if confidence < 0 or confidence > 1:
            raise HTTPException(400, "confidence must be between 0 and 1")
        now = _now()
        profile_uuid = str(payload.get("profile_uuid") or __import__("uuid").uuid4())
        with connect() as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='recognition_profiles'").fetchone():
                raise HTTPException(503, "MIRROR recognition memory is not initialized")
            db.execute(
                "INSERT INTO recognition_profiles(profile_uuid,profile_type,lookup_key,value_json,confidence,user_confirmed,source_entity_type,source_entity_uuid,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(profile_type,lookup_key) DO UPDATE SET value_json=excluded.value_json,confidence=CASE WHEN recognition_profiles.user_confirmed=1 AND excluded.user_confirmed=0 THEN recognition_profiles.confidence ELSE excluded.confidence END,user_confirmed=max(recognition_profiles.user_confirmed,excluded.user_confirmed),source_entity_type=excluded.source_entity_type,source_entity_uuid=excluded.source_entity_uuid,updated_at=excluded.updated_at",
                (profile_uuid, "product_identifier", f"{ns}:{normalized}", json.dumps(candidate, separators=(",", ":"), sort_keys=True), confidence, 1 if user_confirmed else 0, str(payload.get("source_entity_type") or "product_mapping"), str(payload.get("source_entity_uuid") or "") or None, now, now),
            )
            db.commit()
            known = mirror_mapping(db, ns, normalized)
        return {"readback_verified": known is not None, "mapping": known}

    @app.get("/v1/enrichment/gtin/{value}")
    async def lookup_gtin(value: str) -> dict[str, Any]:
        gtin = _normalize_gtin(value)
        with connect() as db:
            known = mirror_mapping(db, "gtin", gtin)
            if known:
                return {"gtin": gtin, **known}
            cached = db.execute("SELECT * FROM product_enrichment_cache WHERE gtin=?", (gtin,)).fetchone()
        if cached:
            return {
                "gtin": gtin,
                "found": True,
                "cached": True,
                "source": cached["source"],
                "candidate": json.loads(cached["candidate_json"]),
                "authority": "candidate only; user/MIRROR confirmation required before canonical mutation",
            }

        template = os.environ.get("MIRROR_GTIN_LOOKUP_URL_TEMPLATE", "").strip()
        source = os.environ.get("MIRROR_GTIN_LOOKUP_SOURCE", "configured_gtin_provider").strip() or "configured_gtin_provider"
        if not template:
            return {
                "gtin": gtin,
                "found": False,
                "configured": False,
                "candidate": None,
                "authority": "no general GTIN provider configured; MIRROR will not fabricate product metadata",
            }
        if "{gtin}" not in template:
            raise HTTPException(503, "MIRROR_GTIN_LOOKUP_URL_TEMPLATE must contain {gtin}")

        headers = {"Accept": "application/json", "User-Agent": "MIRA-MIRROR-product-enrichment"}
        auth_header = os.environ.get("MIRROR_GTIN_LOOKUP_AUTH_HEADER", "").strip()
        auth_value = os.environ.get("MIRROR_GTIN_LOOKUP_AUTH_VALUE", "").strip()
        if auth_header and auth_value:
            headers[auth_header] = auth_value

        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.get(template.replace("{gtin}", gtin), headers=headers)
        except Exception as exc:
            raise HTTPException(502, f"GTIN provider unavailable: {type(exc).__name__}") from exc
        if response.status_code == 404:
            return {"gtin": gtin, "found": False, "configured": True, "source": source, "candidate": None}
        if response.status_code >= 400:
            raise HTTPException(502, f"GTIN provider returned HTTP {response.status_code}")
        try:
            raw = response.json()
        except ValueError as exc:
            raise HTTPException(502, "GTIN provider did not return JSON") from exc

        candidate = _candidate_from_payload(raw)
        found = any(candidate.values())
        if found:
            with connect() as db:
                db.execute(
                    "INSERT OR REPLACE INTO product_enrichment_cache(gtin,source,candidate_json,raw_json,fetched_at) VALUES(?,?,?,?,?)",
                    (gtin, source, json.dumps(candidate, separators=(",", ":"), sort_keys=True), json.dumps(raw, separators=(",", ":"), sort_keys=True), _now()),
                )
                db.commit()
        return {
            "gtin": gtin,
            "found": found,
            "cached": False,
            "source": source,
            "candidate": candidate if found else None,
            "authority": "candidate only; user/MIRROR confirmation required before canonical mutation",
        }
