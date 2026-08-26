from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import HTTPException


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_gtin(value: str) -> str:
    gtin = re.sub(r"\D", "", str(value or ""))
    if len(gtin) not in {8, 12, 13, 14}:
        raise HTTPException(400, "GTIN/UPC/EAN must contain 8, 12, 13, or 14 digits")
    return gtin


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

    @app.get("/v1/enrichment/gtin/{value}")
    async def lookup_gtin(value: str) -> dict[str, Any]:
        gtin = _normalize_gtin(value)
        with connect() as db:
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
                    (
                        gtin,
                        source,
                        json.dumps(candidate, separators=(",", ":"), sort_keys=True),
                        json.dumps(raw, separators=(",", ":"), sort_keys=True),
                        _now(),
                    ),
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
