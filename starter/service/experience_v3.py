from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request


DEFAULT_PREFERENCES: dict[str, Any] = {
    "features.meal_planning": True,
    "health.enabled": False,
    "health.goal": "none",
    "health.current_weight": None,
    "health.goal_weight": None,
    "health.weight_unit": "lb",
    "health.age": None,
    "health.sex": "prefer_not_to_say",
    "health.exercise": "none",
    "health.connected_sources": [],
    "recipes.collection_sources": [],
    "weather.display": "off",
    "weather.location": "",
    "weather.source": "automatic",
    "notifications.push_enabled": False,
    "kiosk.enabled": False,
    "kiosk.keep_awake": True,
    "shopping.purchase_insights": False,
    "shopping.sales_coupons": False,
}

SCHEMA: dict[str, dict[str, Any]] = {
    "features.meal_planning": {"type": "boolean"},
    "health.enabled": {"type": "boolean"},
    "health.goal": {"type": "choice", "choices": ["none", "maintain", "lose", "gain", "general_nutrition"]},
    "health.current_weight": {"type": "optional_number", "min": 20, "max": 1500},
    "health.goal_weight": {"type": "optional_number", "min": 20, "max": 1500},
    "health.weight_unit": {"type": "choice", "choices": ["lb", "kg"]},
    "health.age": {"type": "optional_number", "min": 0, "max": 130},
    "health.sex": {"type": "choice", "choices": ["female", "male", "intersex", "prefer_not_to_say", "self_describe"]},
    "health.exercise": {"type": "choice", "choices": ["none", "cardio", "strength", "both", "other"]},
    "health.connected_sources": {"type": "string_list", "max_items": 20},
    "recipes.collection_sources": {"type": "string_list", "max_items": 50},
    "weather.display": {"type": "choice", "choices": ["off", "morning", "all_day"]},
    "weather.location": {"type": "string", "max_length": 160},
    "weather.source": {"type": "choice", "choices": ["automatic", "nws", "weather_channel", "accuweather"]},
    "notifications.push_enabled": {"type": "boolean"},
    "kiosk.enabled": {"type": "boolean"},
    "kiosk.keep_awake": {"type": "boolean"},
    "shopping.purchase_insights": {"type": "boolean"},
    "shopping.sales_coupons": {"type": "boolean"},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate(key: str, value: Any) -> Any:
    spec = SCHEMA.get(key)
    if not spec:
        raise HTTPException(400, f"unsupported preference: {key}")
    kind = spec["type"]
    if kind == "boolean":
        if not isinstance(value, bool):
            raise HTTPException(400, f"{key} must be boolean")
        return value
    if kind == "choice":
        if value not in spec["choices"]:
            raise HTTPException(400, f"{key} must be one of {spec['choices']}")
        return value
    if kind == "optional_number":
        if value is None or value == "":
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise HTTPException(400, f"{key} must be a number or null")
        numeric = float(value)
        if numeric < spec["min"] or numeric > spec["max"]:
            raise HTTPException(400, f"{key} is outside the supported range")
        return numeric
    if kind == "string":
        if not isinstance(value, str):
            raise HTTPException(400, f"{key} must be text")
        cleaned = value.strip()
        if len(cleaned) > spec["max_length"]:
            raise HTTPException(400, f"{key} is too long")
        return cleaned
    if kind == "string_list":
        if not isinstance(value, list) or len(value) > spec["max_items"]:
            raise HTTPException(400, f"{key} must be a short list")
        cleaned = []
        for item in value:
            if not isinstance(item, str):
                raise HTTPException(400, f"{key} entries must be text")
            text = item.strip()
            if text:
                cleaned.append(text[:160])
        return cleaned
    raise HTTPException(400, f"unsupported preference type for {key}")


def install_experience_v3(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS experience_preferences (
              setting_key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recipes (
              recipe_uuid TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              source TEXT NOT NULL DEFAULT 'manual',
              source_locator TEXT,
              ingredients_json TEXT NOT NULL DEFAULT '[]',
              tags_json TEXT NOT NULL DEFAULT '[]',
              nutrition_json TEXT NOT NULL DEFAULT '{}',
              notes TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            """
        )
        now = _now()
        for key, value in DEFAULT_PREFERENCES.items():
            db.execute(
                "INSERT OR IGNORE INTO experience_preferences(setting_key,value_json,updated_at) VALUES(?,?,?)",
                (key, json.dumps(value, separators=(",", ":"), sort_keys=True), now),
            )
        db.commit()

    def read_preferences() -> dict[str, Any]:
        with connect() as db:
            rows = db.execute("SELECT setting_key,value_json FROM experience_preferences ORDER BY setting_key").fetchall()
        values = {row["setting_key"]: json.loads(row["value_json"]) for row in rows}
        for key, value in DEFAULT_PREFERENCES.items():
            values.setdefault(key, value)
        return values

    @app.get("/v1/preferences")
    def get_preferences() -> dict[str, Any]:
        return {
            "preferences": read_preferences(),
            "schema": SCHEMA,
            "privacy": {
                "health": "off by default; optional profile fields are stored only when the person enables health help",
                "shopping": "purchase-pattern and sale/coupon features are separate opt-ins; no advertising profile or data-sale behavior",
            },
        }

    @app.patch("/v1/preferences")
    async def patch_preferences(request: Request) -> dict[str, Any]:
        payload = await request.json()
        updates = payload.get("preferences") if isinstance(payload, dict) and "preferences" in payload else payload
        if not isinstance(updates, dict) or not updates:
            raise HTTPException(400, "preferences object is required")
        normalized = {str(key): _validate(str(key), value) for key, value in updates.items()}
        now = _now()
        with connect() as db:
            for key, value in normalized.items():
                db.execute(
                    "INSERT INTO experience_preferences(setting_key,value_json,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(setting_key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
                    (key, json.dumps(value, separators=(",", ":"), sort_keys=True), now),
                )
            if hasattr(core_module, "audit"):
                core_module.audit(db, "experience.preferences.update", None, {"keys": sorted(normalized)})
            db.commit()
        return {"readback_verified": True, "preferences": read_preferences()}

    @app.get("/v1/experience/capabilities")
    def experience_capabilities() -> dict[str, Any]:
        return {
            "mira": "the assistant you talk to",
            "mirror": "the private data and evidence layer underneath MIRA",
            "meal_planning": {
                "stock": True,
                "existing_recipe_collections": True,
                "new_recipe_suggestions": "MIRA assistant/model surface uses saved recipe and optional nutrition context; the storage API never invents recipes by itself",
            },
            "health": {
                "optional": True,
                "forced": False,
                "supported_context": ["weight_goal", "age", "sex_optional", "exercise_type", "connected_tracker_capabilities"],
            },
            "weather": {
                "display_modes": ["off", "morning", "all_day"],
                "sources": ["automatic", "nws", "weather_channel", "accuweather"],
                "provider_rule": "show only verified provider data; if a selected provider is not configured, explain the missing connection instead of silently substituting another source",
            },
            "kiosk": {
                "supported": True,
                "targets": ["browser_pwa", "android_tablet", "windows", "linux"],
                "purpose": "always-on dashboards such as a kitchen or fridge tablet",
            },
            "notifications": {
                "android_local_background": True,
                "pwa_permission_surface": True,
                "remote_web_push": "requires an installed PWA/client plus configured push delivery; ChatGPT-only MIRA cannot independently push from a web page that is not installed/running",
            },
            "shopping": {
                "purchase_insights": "opt-in",
                "sales_coupons": "separate opt-in",
                "data_sale": False,
            },
        }

    @app.get("/v1/meals/context")
    def meal_context() -> dict[str, Any]:
        prefs = read_preferences()
        with connect() as db:
            rows = db.execute(
                "SELECT recipe_uuid,title,source,source_locator,ingredients_json,tags_json,nutrition_json,notes FROM recipes ORDER BY updated_at DESC LIMIT 500"
            ).fetchall()
        recipes = []
        for row in rows:
            recipes.append({
                "recipe_uuid": row["recipe_uuid"],
                "title": row["title"],
                "source": row["source"],
                "source_locator": row["source_locator"],
                "ingredients": json.loads(row["ingredients_json"] or "[]"),
                "tags": json.loads(row["tags_json"] or "[]"),
                "nutrition": json.loads(row["nutrition_json"] or "{}"),
                "notes": row["notes"],
            })
        return {
            "meal_planning_enabled": bool(prefs["features.meal_planning"]),
            "health_enabled": bool(prefs["health.enabled"]),
            "goal": prefs["health.goal"] if prefs["health.enabled"] else "none",
            "exercise": prefs["health.exercise"] if prefs["health.enabled"] else "not_used",
            "recipe_collection_sources": prefs["recipes.collection_sources"],
            "recipes": recipes,
            "assistant_rule": "use nutrition/health fields only when health.enabled is true; otherwise plan from recipe, schedule, preference and grocery context only",
        }
