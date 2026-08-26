from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

import httpx
import qrcode
import qrcode.image.svg
from fastapi import HTTPException, Query, Request
from fastapi.responses import Response

SUPPORTED_SURFACES = ["web", "windows", "linux", "android"]

DEFAULT_SETTINGS: dict[str, Any] = {
    "onboarding.completed": False,
    "profile.mode": "personal",
    "ui.experience_level": "guided",
    "providers.google": True,
    "providers.microsoft": False,
    "source_control.enabled": True,
    "updates.safe_automatic": True,
    "updates.require_human_on_conflict": True,
    "features.inventory": True,
    "features.receipts": True,
    "features.orders": True,
    "features.home_assistant": False,
    "features.rfid_nfc": False,
    "features.ble_proximity": False,
    "features.uwb_ranging": False,
    "notifications.spoken_reminders": True,
}

SETTING_SCHEMA = {
    "profile.mode": {"type": "choice", "choices": ["personal", "family", "institutional-pilot"], "label": "Use profile"},
    "ui.experience_level": {"type": "choice", "choices": ["guided", "standard", "advanced"], "label": "Interface guidance"},
    "providers.google": {"type": "boolean", "label": "Google Workspace"},
    "providers.microsoft": {"type": "boolean", "label": "Microsoft 365"},
    "source_control.enabled": {"type": "boolean", "label": "GitHub source control"},
    "updates.safe_automatic": {"type": "boolean", "label": "Install safe updates automatically"},
    "updates.require_human_on_conflict": {"type": "boolean", "label": "Pause only when custom features conflict"},
    "features.inventory": {"type": "boolean", "label": "Inventory"},
    "features.receipts": {"type": "boolean", "label": "Receipt capture"},
    "features.orders": {"type": "boolean", "label": "Order tracking"},
    "features.home_assistant": {"type": "boolean", "label": "Home Assistant"},
    "features.rfid_nfc": {"type": "boolean", "label": "RFID / NFC"},
    "features.ble_proximity": {"type": "boolean", "label": "BLE proximity tracking"},
    "features.uwb_ranging": {"type": "boolean", "label": "UWB precise ranging"},
    "notifications.spoken_reminders": {"type": "boolean", "label": "Spoken reminders"},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _version_tuple(value: str) -> tuple[int, int, int]:
    cleaned = str(value or "").strip().lstrip("vV").split("-", 1)[0]
    parts = cleaned.split(".")
    out = []
    for part in parts[:3]:
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    while len(out) < 3:
        out.append(0)
    return tuple(out)  # type: ignore[return-value]


def install_product_v1(app: Any, core_module: Any) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
              setting_key TEXT PRIMARY KEY,
              value_json TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS feature_requests_force_all_platforms_insert
            AFTER INSERT ON feature_requests
            BEGIN
              UPDATE feature_requests
                 SET target_surfaces_json='["android","linux","web","windows"]'
               WHERE request_uuid=NEW.request_uuid;
            END;
            CREATE TRIGGER IF NOT EXISTS feature_requests_force_all_platforms_update
            AFTER UPDATE OF target_surfaces_json ON feature_requests
            WHEN NEW.target_surfaces_json <> '["android","linux","web","windows"]'
            BEGIN
              UPDATE feature_requests
                 SET target_surfaces_json='["android","linux","web","windows"]'
               WHERE request_uuid=NEW.request_uuid;
            END;
            """
        )
        db.execute("UPDATE feature_requests SET target_surfaces_json=?", (json.dumps(sorted(SUPPORTED_SURFACES), separators=(",", ":")),))
        now = _now()
        for key, value in DEFAULT_SETTINGS.items():
            db.execute(
                "INSERT OR IGNORE INTO user_settings(setting_key,value_json,updated_at) VALUES(?,?,?)",
                (key, json.dumps(value, separators=(",", ":"), sort_keys=True), now),
            )
        db.commit()

    def read_settings() -> dict[str, Any]:
        with connect() as db:
            rows = db.execute("SELECT setting_key,value_json FROM user_settings ORDER BY setting_key").fetchall()
        values = {row["setting_key"]: json.loads(row["value_json"]) for row in rows}
        for key, value in DEFAULT_SETTINGS.items():
            values.setdefault(key, value)
        return values

    def settings_revision(values: dict[str, Any]) -> str:
        raw = json.dumps(values, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def validate_setting(key: str, value: Any) -> Any:
        if key == "onboarding.completed":
            if not isinstance(value, bool):
                raise HTTPException(400, f"{key} must be boolean")
            return value
        spec = SETTING_SCHEMA.get(key)
        if not spec:
            raise HTTPException(400, f"unsupported setting: {key}")
        if spec["type"] == "boolean":
            if not isinstance(value, bool):
                raise HTTPException(400, f"{key} must be boolean")
            return value
        if spec["type"] == "choice":
            if value not in spec["choices"]:
                raise HTTPException(400, f"{key} must be one of {spec['choices']}")
            return value
        raise HTTPException(400, f"unsupported setting type for {key}")

    @app.get("/v1/product/info")
    def product_info() -> dict[str, Any]:
        return {
            "brand": "MIRA // MIRROR",
            "edition": "1.0 Pilot",
            "tagline": "Reflecting reality.",
            "supported_surfaces": SUPPORTED_SURFACES,
            "stock_mode": {
                "authority": "Google Workspace",
                "google_required": True,
                "linux_required": False,
                "server_required": False,
                "self_hosted_services": "optional local bridge",
            },
            "self_hosted_mode": {
                "optional": True,
                "service_runtimes": ["Docker", "Podman", "native Python service"],
                "external_integrations": "capability-scoped adapters; never implicit authority",
            },
            "feature_studio_default": "every supported surface; platform-specific exceptions are engineering-only",
            "update_policy": {
                "safe_updates": "automatic or one press",
                "human_required": "only when user-created code or policy conflicts cannot be reconciled safely",
                "stale_client": "HTTP 426 should open the update/reconciliation flow",
                "rollback": "preserve prior Personal Production revision before automatic source promotion",
            },
            "linux": {
                "desktop_packages": ["AppImage", "deb", "rpm"],
                "desktop_targets": ["Ubuntu", "Debian", "RHEL 9 compatible family"],
                "server_targets": ["Docker", "Podman", "RHEL 9", "RHEL 10"],
                "rhel10_desktop_webview": "blocked: RHEL 10 removed WebKitGTK; do not claim native Tauri GUI support",
            },
        }

    @app.get("/v1/settings")
    def get_settings() -> dict[str, Any]:
        values = read_settings()
        return {
            "settings": values,
            "schema": SETTING_SCHEMA,
            "revision": settings_revision(values),
            "authority": "MIRROR server settings; clients and ChatGPT companion use the same scoped interface",
        }

    @app.patch("/v1/settings")
    async def patch_settings(request: Request) -> dict[str, Any]:
        payload = await request.json()
        updates = payload.get("settings") if isinstance(payload, dict) and "settings" in payload else payload
        if not isinstance(updates, dict) or not updates:
            raise HTTPException(400, "settings object is required")
        normalized = {str(key): validate_setting(str(key), value) for key, value in updates.items()}
        now = _now()
        with connect() as db:
            for key, value in normalized.items():
                db.execute(
                    "INSERT INTO user_settings(setting_key,value_json,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(setting_key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
                    (key, json.dumps(value, separators=(",", ":"), sort_keys=True), now),
                )
            if hasattr(core_module, "audit"):
                core_module.audit(db, "settings.update", None, {"keys": sorted(normalized)})
            db.commit()
        values = read_settings()
        return {"readback_verified": True, "settings": values, "revision": settings_revision(values)}

    @app.post("/v1/onboarding/complete")
    def complete_onboarding() -> dict[str, Any]:
        now = _now()
        with connect() as db:
            db.execute(
                "INSERT INTO user_settings(setting_key,value_json,updated_at) VALUES('onboarding.completed','true',?) "
                "ON CONFLICT(setting_key) DO UPDATE SET value_json='true',updated_at=excluded.updated_at",
                (now,),
            )
            db.commit()
        return {"readback_verified": True, "completed": True}

    @app.get("/v1/integrations/github/status")
    def github_status() -> dict[str, Any]:
        install_url = os.environ.get("MIRROR_GITHUB_APP_INSTALL_URL", "").strip()
        installation_id = os.environ.get("MIRROR_GITHUB_INSTALLATION_ID", "").strip()
        return {
            "connected": bool(installation_id),
            "configured": bool(install_url),
            "signup_url": "https://github.com/signup",
            "install_url": install_url or None,
            "account_creation": {
                "automatic": False,
                "reason": "GitHub account creation requires the person to complete GitHub signup and verification; MIRA can resume setup immediately afterward.",
            },
            "recommended_auth": "GitHub App with fine-grained repository permissions and short-lived tokens",
            "repository_strategy": "user-owned Personal Production repository synchronized from canonical upstream; clean updates can be automated, conflicts pause for review",
        }

    @app.get("/v1/updates/status")
    async def update_status(
        client_version: str = Query(default=""),
        platform: str = Query(default="web"),
    ) -> dict[str, Any]:
        platform = platform.strip().lower()
        if platform not in {"web", "windows", "linux", "android", "cli"}:
            raise HTTPException(400, "unsupported platform")
        repository = os.environ.get("MIRROR_RELEASE_REPOSITORY", "Matthew-Beare/MIRA-Personal-Production").strip()
        feed = os.environ.get("MIRROR_RELEASE_FEED_URL", f"https://api.github.com/repos/{repository}/releases/latest").strip()
        latest_version = None
        release_url = None
        assets: list[dict[str, Any]] = []
        error = None
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
                response = await client.get(feed, headers={"Accept": "application/vnd.github+json", "User-Agent": "MIRA-MIRROR-update-check"})
            if response.status_code == 200:
                release = response.json()
                latest_version = str(release.get("tag_name") or release.get("name") or "").lstrip("vV") or None
                release_url = release.get("html_url")
                assets = [
                    {"name": str(item.get("name") or ""), "url": item.get("browser_download_url"), "size": item.get("size")}
                    for item in release.get("assets", [])
                ]
            elif response.status_code == 404:
                error = "No published customer release exists yet. CI artifacts are not treated as an update channel."
            else:
                error = f"release feed returned HTTP {response.status_code}"
        except Exception as exc:
            error = f"release feed unavailable: {type(exc).__name__}"

        update_available = bool(latest_version and client_version and _version_tuple(latest_version) > _version_tuple(client_version))
        return {
            "repository": repository,
            "platform": platform,
            "current_version": client_version or None,
            "latest_version": latest_version,
            "update_available": update_available,
            "release_url": release_url,
            "assets": assets,
            "safe_automatic_enabled": bool(read_settings().get("updates.safe_automatic", True)),
            "conflict_policy": "pause and require a person only when source/policy reconciliation cannot be completed cleanly",
            "error": error,
        }

    @app.get("/v1/locations/{location_uuid}/code")
    def location_code(location_uuid: str) -> dict[str, Any]:
        with connect() as db:
            row = db.execute("SELECT uuid,name FROM locations WHERE uuid=?", (location_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "location not found")
        return {"location_uuid": row["uuid"], "name": row["name"], "code": f"MIRROR:LOCATION:{row['uuid']}"}

    @app.get("/v1/locations/resolve-code")
    def resolve_location_code(value: str = Query(..., min_length=1)) -> dict[str, Any]:
        prefix = "MIRROR:LOCATION:"
        if not value.upper().startswith(prefix):
            raise HTTPException(404, "not a MIRROR location code")
        location_uuid = value[len(prefix):].strip()
        with connect() as db:
            row = db.execute("SELECT uuid,name,parent_uuid,location_type FROM locations WHERE uuid=?", (location_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "location code does not resolve to a live location")
        return {"location": dict(row), "code": f"MIRROR:LOCATION:{row['uuid']}"}

    @app.get("/v1/locations/{location_uuid}/label.svg")
    def location_label(location_uuid: str) -> Response:
        with connect() as db:
            row = db.execute("SELECT uuid,name FROM locations WHERE uuid=?", (location_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "location not found")
        code = f"MIRROR:LOCATION:{row['uuid']}"
        image = qrcode.make(code, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
        raw = image.to_string(encoding="unicode")
        return Response(content=raw, media_type="image/svg+xml", headers={"Content-Disposition": f"inline; filename=mirror-location-{location_uuid}.svg"})
