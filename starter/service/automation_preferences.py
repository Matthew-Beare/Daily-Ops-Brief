"""Persist Daily Cleanup preferences and produce slot-aware scheduler plans.

MIRROR stores what the user wants; ChatGPT remains responsible for creating or
updating ChatGPT scheduled tasks. The planner always prefers consolidation.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request

DEFAULTS: dict[str, Any] = {
    "daily_cleanup.enabled": True,
    "daily_cleanup.times": ["00:01"],
    "daily_cleanup.timezone_mode": "local",
    "daily_cleanup.attach_to_existing_cycle": True,
    "daily_briefs.configured": False,
    "scheduler.max_chatgpt_slots": 5,
    "scheduler.prefer_consolidation": True,
    "ai.monthly_budget": None,
    "ai.budget_hard_stop": False,
    "ai.warning_thresholds": [50, 75, 90],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _valid_time(value: str) -> bool:
    if len(value) != 5 or value[2] != ":":
        return False
    try:
        hour, minute = (int(part) for part in value.split(":"))
    except ValueError:
        return False
    return 0 <= hour <= 23 and 0 <= minute <= 59


def install_automation_preferences(app: Any, core_module: Any) -> None:
    """Install automation preference storage and consolidation planning APIs."""

    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS automation_preferences(setting_key TEXT PRIMARY KEY,value_json TEXT NOT NULL,updated_at TEXT NOT NULL)"
        )
        now = _now()
        for key, value in DEFAULTS.items():
            db.execute("INSERT OR IGNORE INTO automation_preferences(setting_key,value_json,updated_at) VALUES(?,?,?)", (key, json.dumps(value), now))
        db.commit()

    def read_preferences() -> dict[str, Any]:
        with connect() as db:
            rows = db.execute("SELECT setting_key,value_json FROM automation_preferences ORDER BY setting_key").fetchall()
        result = {row["setting_key"]: json.loads(row["value_json"]) for row in rows}
        for key, value in DEFAULTS.items():
            result.setdefault(key, value)
        return result

    def validate(key: str, value: Any) -> Any:
        if key == "daily_cleanup.enabled" or key == "daily_cleanup.attach_to_existing_cycle" or key == "daily_briefs.configured" or key == "scheduler.prefer_consolidation" or key == "ai.budget_hard_stop":
            if not isinstance(value, bool):
                raise HTTPException(400, f"{key} must be true or false")
            return value
        if key == "daily_cleanup.times":
            if not isinstance(value, list) or not value or len(value) > 12 or any(not isinstance(item, str) or not _valid_time(item) for item in value):
                raise HTTPException(400, "daily_cleanup.times must contain 1-12 local HH:MM times")
            return sorted(set(value))
        if key == "daily_cleanup.timezone_mode":
            if value not in {"local", "fixed"}:
                raise HTTPException(400, "daily_cleanup.timezone_mode must be local or fixed")
            return value
        if key == "scheduler.max_chatgpt_slots":
            number = int(value)
            if number < 1 or number > 20:
                raise HTTPException(400, "scheduler.max_chatgpt_slots must be 1-20")
            return number
        if key == "ai.monthly_budget":
            if value is None:
                return None
            number = float(value)
            if number < 0:
                raise HTTPException(400, "ai.monthly_budget cannot be negative")
            return number
        if key == "ai.warning_thresholds":
            if not isinstance(value, list) or any(float(item) <= 0 or float(item) > 100 for item in value):
                raise HTTPException(400, "ai.warning_thresholds must contain percentages from 1 to 100")
            return sorted({float(item) for item in value})
        raise HTTPException(400, f"unsupported automation preference: {key}")

    @app.get("/v1/automation/preferences")
    def get_preferences() -> dict[str, Any]:
        return {"preferences": read_preferences(), "readback_verified": True}

    @app.patch("/v1/automation/preferences")
    async def patch_preferences(request: Request) -> dict[str, Any]:
        payload = await request.json()
        updates = payload.get("preferences") if isinstance(payload, dict) and "preferences" in payload else payload
        if not isinstance(updates, dict) or not updates:
            raise HTTPException(400, "preferences object is required")
        normalized = {str(key): validate(str(key), value) for key, value in updates.items()}
        now = _now()
        with connect() as db:
            for key, value in normalized.items():
                db.execute("INSERT INTO automation_preferences(setting_key,value_json,updated_at) VALUES(?,?,?) ON CONFLICT(setting_key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at", (key, json.dumps(value, separators=(",", ":"), sort_keys=True), now))
            db.commit()
        return {"preferences": read_preferences(), "readback_verified": True}

    @app.post("/v1/automation/plan")
    async def plan_schedule(request: Request) -> dict[str, Any]:
        payload = await request.json()
        prefs = read_preferences()
        existing_cycle = bool(payload.get("existing_mira_cycle"))
        slots_used = max(0, int(payload.get("chatgpt_task_slots_used") or 0))
        max_slots = int(payload.get("max_chatgpt_task_slots") or prefs["scheduler.max_chatgpt_slots"])
        requested_times = payload.get("requested_times") or prefs["daily_cleanup.times"]
        if not isinstance(requested_times, list) or any(not isinstance(item, str) or not _valid_time(item) for item in requested_times):
            raise HTTPException(400, "requested_times must contain local HH:MM values")
        if existing_cycle and prefs["scheduler.prefer_consolidation"]:
            strategy = "merge_into_existing_mira_cycle"
            new_slot_required = False
        else:
            strategy = "one_recurring_daily_cleanup_task_with_multiple_times"
            new_slot_required = True
        projected = slots_used + (1 if new_slot_required else 0)
        warnings: list[str] = []
        if new_slot_required and projected >= max_slots:
            warnings.append(f"This would use {projected} of {max_slots} available ChatGPT scheduled-task slots. Reusing an existing MIRA cycle is preferred.")
        if len(requested_times) > 1:
            warnings.append("Multiple cleanup windows should stay on one recurring task when the scheduler supports multiple daily execution times; they should not become one task per time.")
        return {
            "strategy": strategy,
            "requested_times": sorted(set(requested_times)),
            "new_slot_required": new_slot_required,
            "chatgpt_task_slots_used": slots_used,
            "projected_task_slots_used": projected,
            "max_chatgpt_task_slots": max_slots,
            "warnings": warnings,
            "cleanup_before_brief": True,
            "readback_verified": True,
        }
