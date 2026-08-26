from __future__ import annotations

import hmac
import os
from pathlib import Path

import app as core_app
from automation_preferences import install_automation_preferences
from backup_scheduler import install_backup_scheduler
from device_auth import install_device_auth, valid_device_token
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import app
from enrichment import install_enrichment
from experience_v3 import install_experience_v3
from idempotency import install_idempotency
from integrations import install_integrations
from inventory_hierarchy import install_inventory_hierarchy
from maintenance import install_maintenance
from media import install_media
from merchants import install_merchants
from migration_apply import install_migration_apply
from oauth_hardening import install_oauth_hardening
from platform_foundations import install_platform_foundations
from product_v1 import install_product_v1
from provider_extensions import register_provider_extensions
from receipt_processing import install_receipt_processing
from receipts import install_receipts
from reconciliation import install_reconciliation
from release_guard import install_release_guard
from signed_media import install_signed_media

install_oauth_hardening(core_app)
register_provider_extensions(app)
install_platform_foundations(app, core_app)
install_product_v1(app, core_app)
install_automation_preferences(app, core_app)
install_experience_v3(app, core_app)
install_inventory_hierarchy(app, core_app)
install_enrichment(app, core_app)
install_receipts(app, core_app)
install_receipt_processing(app, core_app)
install_reconciliation(app, core_app)
install_merchants(app, core_app)
install_integrations(app, core_app)
install_media(app, core_app)
install_maintenance(app, core_app)
install_migration_apply(app, core_app)
install_backup_scheduler(app, core_app)
install_device_auth(app, core_app)
install_signed_media(app, core_app)
install_release_guard(app, Path(__file__).resolve().parent / "release.json", core_app.API_MAJOR, core_app.API_CONTRACT)
install_idempotency(app, core_app.DB_PATH)

# The starter core also has a conservative CORS layer. This outer layer is the
# complete official-client contract and, critically, allows Idempotency-Key
# during browser/desktop preflight without widening database access.
allowed_origins = [value.strip() for value in os.environ.get(
    "MIRROR_CORS_ORIGINS",
    "http://localhost:8765,http://127.0.0.1:8765,http://tauri.localhost,https://tauri.localhost,tauri://localhost,https://appassets.androidplatform.net,null",
).split(",") if value.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Mirror-Api-Version", "X-Mirror-Client"],
    expose_headers=["X-Mirror-Idempotent-Replay"],
)

PUBLIC_API_PREFIXES = (
    "/v1/health",
    "/v1/compatibility",
    "/v1/product/info",
    "/v1/auth/providers",
    "/v1/auth/google/start",
    "/v1/auth/google/callback",
    "/v1/auth/microsoft/start",
    "/v1/auth/microsoft/callback",
    "/v1/devices/enroll",
)


@app.middleware("http")
async def mirror_api_auth(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS" or not path.startswith("/v1/") or any(path.startswith(prefix) for prefix in PUBLIC_API_PREFIXES):
        return await call_next(request)

    mode = os.environ.get("MIRROR_AUTH_MODE", "required").strip().lower()
    if mode in {"development", "disabled"}:
        return await call_next(request)

    supplied = request.headers.get("Authorization", "")
    token = supplied[7:] if supplied.startswith("Bearer ") else ""
    expected = os.environ.get("MIRROR_ACCESS_TOKEN", "").strip()

    if expected and token and hmac.compare_digest(token, expected):
        return await call_next(request)
    if token and valid_device_token(core_app, token):
        return await call_next(request)

    if not expected:
        return JSONResponse(
            {"detail": "MIRROR API authentication is required but no bootstrap admin credential is configured and the supplied device credential was not valid"},
            status_code=503,
        )
    return JSONResponse({"detail": "valid MIRROR bootstrap or enrolled-device bearer token required"}, status_code=401)


UI_DIR = Path(__file__).resolve().parent / "ui"
if UI_DIR.is_dir():
    app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="mirror-ui")
