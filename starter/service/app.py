from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
import qrcode
import qrcode.image.svg
from barcode import Code128
from barcode.writer import SVGWriter
from cryptography.fernet import Fernet
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, Response

PRODUCT_VERSION = "0.2.0"
API_CONTRACT = "1.1"
API_MAJOR = 1
DATA_DIR = Path(os.environ.get("MIRROR_DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "mirror.db"
EVIDENCE_DIR = DATA_DIR / "evidence"
DEFAULT_PROVIDER = os.environ.get("MIRROR_DEFAULT_PROVIDER", "google_workspace")
PUBLIC_BASE_URL = os.environ.get("MIRROR_PUBLIC_BASE_URL", "http://localhost:8765").rstrip("/")

app = FastAPI(title="mirror service", version=PRODUCT_VERSION)
allowed_origins = [value.strip() for value in os.environ.get(
    "MIRROR_CORS_ORIGINS",
    "http://localhost:8765,http://127.0.0.1:8765,https://appassets.androidplatform.net,null",
).split(",") if value.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Mirror-Api-Version", "X-Mirror-Client"],
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
              uuid TEXT PRIMARY KEY, name TEXT NOT NULL, parent_uuid TEXT,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              FOREIGN KEY(parent_uuid) REFERENCES categories(uuid)
            );
            CREATE TABLE IF NOT EXISTS locations (
              uuid TEXT PRIMARY KEY, name TEXT NOT NULL, parent_uuid TEXT, location_type TEXT NOT NULL,
              created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              FOREIGN KEY(parent_uuid) REFERENCES locations(uuid)
            );
            CREATE TABLE IF NOT EXISTS assets (
              uuid TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
              category_uuid TEXT, location_uuid TEXT, status TEXT NOT NULL DEFAULT 'active',
              metadata_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              FOREIGN KEY(category_uuid) REFERENCES categories(uuid),
              FOREIGN KEY(location_uuid) REFERENCES locations(uuid)
            );
            CREATE TABLE IF NOT EXISTS identifiers (
              namespace TEXT NOT NULL, value TEXT NOT NULL, asset_uuid TEXT NOT NULL,
              created_at TEXT NOT NULL, PRIMARY KEY(namespace, value),
              FOREIGN KEY(asset_uuid) REFERENCES assets(uuid)
            );
            CREATE TABLE IF NOT EXISTS evidence (
              uuid TEXT PRIMARY KEY, asset_uuid TEXT NOT NULL, filename TEXT NOT NULL,
              mime_type TEXT NOT NULL, sha256 TEXT NOT NULL, storage_path TEXT NOT NULL,
              role TEXT NOT NULL, created_at TEXT NOT NULL,
              FOREIGN KEY(asset_uuid) REFERENCES assets(uuid)
            );
            CREATE TABLE IF NOT EXISTS audit_events (
              event_uuid TEXT PRIMARY KEY, event_type TEXT NOT NULL, target_uuid TEXT,
              payload_json TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS oauth_states (
              state TEXT PRIMARY KEY, provider TEXT NOT NULL, verifier TEXT NOT NULL,
              return_to TEXT NOT NULL, expires_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS oauth_tokens (
              provider TEXT PRIMARY KEY, encrypted_json TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            """
        )


@app.on_event("startup")
def startup() -> None:
    init_db()


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    result = dict(row)
    if "metadata_json" in result:
        result["metadata"] = json.loads(result.pop("metadata_json") or "{}")
    return result


def audit(db: sqlite3.Connection, event_type: str, target_uuid: str | None, payload: dict[str, Any]) -> None:
    db.execute(
        "INSERT INTO audit_events(event_uuid,event_type,target_uuid,payload_json,created_at) VALUES(?,?,?,?,?)",
        (str(uuid.uuid4()), event_type, target_uuid, json.dumps(payload, sort_keys=True), now_iso()),
    )


def asset_readback(db: sqlite3.Connection, asset_uuid: str) -> dict[str, Any]:
    asset = row_dict(db.execute("SELECT * FROM assets WHERE uuid=?", (asset_uuid,)).fetchone())
    if not asset:
        raise HTTPException(404, "asset not found")
    asset["identifiers"] = [dict(row) for row in db.execute(
        "SELECT namespace,value,created_at FROM identifiers WHERE asset_uuid=? ORDER BY namespace,value", (asset_uuid,)
    )]
    asset["photo_evidence"] = [dict(row) for row in db.execute(
        "SELECT uuid AS evidence_uuid, role AS media_role, mime_type, sha256 AS content_hash, filename, created_at AS captured_at FROM evidence WHERE asset_uuid=? AND mime_type LIKE 'image/%' ORDER BY created_at DESC",
        (asset_uuid,),
    )]
    asset["evidence"] = [dict(row) for row in db.execute(
        "SELECT uuid AS evidence_uuid, role, mime_type, sha256 AS content_hash, filename, created_at FROM evidence WHERE asset_uuid=? ORDER BY created_at DESC",
        (asset_uuid,),
    )]
    return asset


def parse_api_major(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value.strip().split(".", 1)[0])
    except ValueError:
        return None


def require_compatible(request: Request) -> None:
    supplied = request.headers.get("X-Mirror-Api-Version")
    major = parse_api_major(supplied)
    if supplied and major != API_MAJOR:
        raise HTTPException(426, f"client API {supplied} is incompatible with server API {API_CONTRACT}")


@app.get("/v1/health")
def health() -> dict[str, Any]:
    with connect() as db:
        db.execute("SELECT 1").fetchone()
    return {
        "status": "ready",
        "product": "mirror",
        "product_version": PRODUCT_VERSION,
        "api_contract": API_CONTRACT,
        "api_major": API_MAJOR,
        "default_provider": DEFAULT_PROVIDER,
        "capabilities": [
            "inventory_crud", "hierarchical_categories", "hierarchical_locations", "asset_relocation",
            "barcode_qr_ingress", "preprinted_identifier_binding", "evidence_ingress", "label_rendering",
            "oauth_google", "oauth_microsoft", "client_compatibility_preflight"
        ],
    }


@app.get("/v1/compatibility")
def compatibility(client_api: str = Query(default=""), client_version: str = Query(default="")) -> dict[str, Any]:
    major = parse_api_major(client_api)
    compatible = major == API_MAJOR
    return {
        "compatible": compatible,
        "server_api": API_CONTRACT,
        "supported_api_majors": [API_MAJOR],
        "client_api": client_api or None,
        "client_version": client_version or None,
        "mutation_allowed": compatible,
        "reason": "compatible" if compatible else "unsupported API major; update client or server before mutation",
    }


@app.get("/v1/inventory/tree")
def inventory_tree() -> dict[str, Any]:
    with connect() as db:
        categories = [dict(row) for row in db.execute("SELECT * FROM categories ORDER BY name")]
        locations = [dict(row) for row in db.execute("SELECT * FROM locations ORDER BY name")]
    return {"categories": categories, "locations": locations}


@app.get("/v1/assets")
def list_assets(
    q: str = Query(default=""), category_uuid: str = Query(default=""),
    location_uuid: str = Query(default=""), status: str = Query(default="active"), limit: int = Query(default=250, ge=1, le=1000),
) -> dict[str, Any]:
    where = ["status=?"]
    params: list[Any] = [status]
    if q:
        where.append("(name LIKE ? OR description LIKE ? OR uuid LIKE ?)")
        token = f"%{q}%"
        params.extend([token, token, token])
    if category_uuid:
        where.append("category_uuid=?")
        params.append(category_uuid)
    if location_uuid:
        where.append("location_uuid=?")
        params.append(location_uuid)
    params.append(limit)
    sql = f"SELECT * FROM assets WHERE {' AND '.join(where)} ORDER BY updated_at DESC LIMIT ?"
    with connect() as db:
        rows = [row_dict(row) for row in db.execute(sql, params)]
    return {"assets": rows, "count": len(rows)}


@app.get("/v1/assets/{asset_uuid}")
def get_asset(asset_uuid: str) -> dict[str, Any]:
    with connect() as db:
        return asset_readback(db, asset_uuid)


@app.post("/v1/commands")
async def command(request: Request) -> dict[str, Any]:
    require_compatible(request)
    body = await request.json()
    command_type = str(body.get("command_type", ""))
    payload = body.get("payload") or {}
    if not command_type or not isinstance(payload, dict):
        raise HTTPException(400, "command_type and object payload are required")
    with connect() as db:
        ts = now_iso()
        if command_type == "inventory.category.create":
            entity_uuid = str(payload.get("category_uuid") or uuid.uuid4())
            db.execute("INSERT INTO categories(uuid,name,parent_uuid,created_at,updated_at) VALUES(?,?,?,?,?)",
                       (entity_uuid, str(payload["name"]).strip(), payload.get("parent_uuid") or None, ts, ts))
            audit(db, command_type, entity_uuid, payload)
            db.commit()
            return {"readback_verified": True, "category": dict(db.execute("SELECT * FROM categories WHERE uuid=?", (entity_uuid,)).fetchone())}
        if command_type == "inventory.location.create":
            entity_uuid = str(payload.get("location_uuid") or uuid.uuid4())
            db.execute("INSERT INTO locations(uuid,name,parent_uuid,location_type,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                       (entity_uuid, str(payload["name"]).strip(), payload.get("parent_uuid") or None, str(payload.get("location_type") or "storage"), ts, ts))
            audit(db, command_type, entity_uuid, payload)
            db.commit()
            return {"readback_verified": True, "location": dict(db.execute("SELECT * FROM locations WHERE uuid=?", (entity_uuid,)).fetchone())}
        if command_type == "inventory.asset.create":
            asset_uuid = str(payload.get("asset_uuid") or uuid.uuid4())
            db.execute(
                "INSERT INTO assets(uuid,name,description,category_uuid,location_uuid,status,metadata_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (asset_uuid, str(payload["name"]).strip(), str(payload.get("description") or ""), payload.get("category_uuid") or None,
                 payload.get("location_uuid") or None, "active", json.dumps(payload.get("metadata") or {}, sort_keys=True), ts, ts),
            )
            audit(db, command_type, asset_uuid, payload)
            db.commit()
            return {"readback_verified": True, "asset": asset_readback(db, asset_uuid)}
        if command_type == "inventory.asset.update":
            asset_uuid = str(payload["asset_uuid"])
            current = asset_readback(db, asset_uuid)
            db.execute(
                "UPDATE assets SET name=?,description=?,category_uuid=?,location_uuid=?,metadata_json=?,updated_at=? WHERE uuid=?",
                (str(payload.get("name", current["name"])), str(payload.get("description", current["description"])),
                 payload.get("category_uuid", current.get("category_uuid")) or None,
                 payload.get("location_uuid", current.get("location_uuid")) or None,
                 json.dumps(payload.get("metadata", current.get("metadata") or {}), sort_keys=True), ts, asset_uuid),
            )
            audit(db, command_type, asset_uuid, payload)
            db.commit()
            return {"readback_verified": True, "asset": asset_readback(db, asset_uuid)}
        if command_type == "inventory.asset.relocate":
            asset_uuid = str(payload["asset_uuid"])
            location_uuid = str(payload["location_uuid"])
            asset_readback(db, asset_uuid)
            if not db.execute("SELECT 1 FROM locations WHERE uuid=?", (location_uuid,)).fetchone():
                raise HTTPException(404, "location not found")
            db.execute("UPDATE assets SET location_uuid=?,updated_at=? WHERE uuid=?", (location_uuid, ts, asset_uuid))
            audit(db, command_type, asset_uuid, payload)
            db.commit()
            return {"readback_verified": True, "asset": asset_readback(db, asset_uuid)}
        if command_type == "inventory.identifier.assign":
            asset_uuid = str(payload["asset_uuid"])
            asset_readback(db, asset_uuid)
            namespace = str(payload.get("namespace") or "preprinted").strip().lower()
            value = str(payload["value"]).strip()
            db.execute("INSERT INTO identifiers(namespace,value,asset_uuid,created_at) VALUES(?,?,?,?)",
                       (namespace, value, asset_uuid, ts))
            audit(db, command_type, asset_uuid, payload)
            db.commit()
            return {"readback_verified": True, "asset": asset_readback(db, asset_uuid)}
        if command_type == "capture.barcode_qr_scan":
            value = str(payload.get("raw_value") or "").strip()
            match = db.execute("SELECT asset_uuid,namespace,value FROM identifiers WHERE value=? LIMIT 1", (value,)).fetchone()
            return {
                "readback_verified": True,
                "scan": payload,
                "matched": bool(match),
                "asset": asset_readback(db, match["asset_uuid"]) if match else None,
                "next_action": "open_asset" if match else "classify_or_assign_identifier",
            }
    raise HTTPException(400, f"unsupported command_type: {command_type}")


@app.post("/v1/evidence")
async def upload_evidence(
    request: Request,
    asset_uuid: str = Form(...), role: str = Form(default="attachment"),
    media_role: str = Form(default=""), file: UploadFile = File(...),
) -> dict[str, Any]:
    require_compatible(request)
    chosen_role = media_role or role or "attachment"
    with connect() as db:
        asset_readback(db, asset_uuid)
        evidence_uuid = str(uuid.uuid4())
        safe_name = Path(file.filename or "attachment").name
        target = EVIDENCE_DIR / f"{evidence_uuid}-{safe_name}"
        digest = hashlib.sha256()
        size = 0
        with target.open("wb") as handle:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > 100 * 1024 * 1024:
                    target.unlink(missing_ok=True)
                    raise HTTPException(413, "evidence exceeds 100 MiB starter service limit")
                digest.update(chunk)
                handle.write(chunk)
        db.execute(
            "INSERT INTO evidence(uuid,asset_uuid,filename,mime_type,sha256,storage_path,role,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (evidence_uuid, asset_uuid, safe_name, file.content_type or "application/octet-stream", digest.hexdigest(), str(target), chosen_role, now_iso()),
        )
        audit(db, "evidence.upload", asset_uuid, {"evidence_uuid": evidence_uuid, "filename": safe_name, "role": chosen_role, "sha256": digest.hexdigest()})
        db.commit()
        return {"readback_verified": True, "evidence_uuid": evidence_uuid, "asset_uuid": asset_uuid, "filename": safe_name, "mime_type": file.content_type or "application/octet-stream", "content_hash": digest.hexdigest(), "role": chosen_role}


@app.get("/v1/evidence/{evidence_uuid}")
def get_evidence(evidence_uuid: str) -> FileResponse:
    with connect() as db:
        row = db.execute("SELECT * FROM evidence WHERE uuid=?", (evidence_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "evidence not found")
        path = Path(row["storage_path"])
        if not path.is_file():
            raise HTTPException(410, "evidence metadata exists but content is unavailable")
        return FileResponse(path, media_type=row["mime_type"], filename=row["filename"])


@app.get("/v1/labels/{asset_uuid}.svg")
def render_label(asset_uuid: str, kind: str = Query(default="qr")) -> Response:
    with connect() as db:
        asset = asset_readback(db, asset_uuid)
    payload = f"mirror:asset:{asset_uuid}"
    if kind == "qr":
        image = qrcode.make(payload, image_factory=qrcode.image.svg.SvgPathImage)
        buffer = io.BytesIO()
        image.save(buffer)
        return Response(buffer.getvalue(), media_type="image/svg+xml", headers={"Content-Disposition": f'inline; filename="mirror-{asset_uuid}.svg"'})
    if kind == "code128":
        buffer = io.BytesIO()
        Code128(payload, writer=SVGWriter()).write(buffer, options={"write_text": True})
        return Response(buffer.getvalue(), media_type="image/svg+xml", headers={"Content-Disposition": f'inline; filename="mirror-{asset_uuid}-code128.svg"'})
    raise HTTPException(400, "kind must be qr or code128")


def token_cipher() -> Fernet:
    key = os.environ.get("MIRROR_TOKEN_KEY", "").strip()
    if not key:
        raise HTTPException(503, "MIRROR_TOKEN_KEY is required before provider OAuth tokens may be stored")
    try:
        return Fernet(key.encode("ascii"))
    except Exception as exc:
        raise HTTPException(503, "MIRROR_TOKEN_KEY must be a valid Fernet key") from exc


def pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def store_oauth_state(provider: str, verifier: str, return_to: str) -> str:
    state = secrets.token_urlsafe(32)
    expires = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    with connect() as db:
        db.execute("INSERT INTO oauth_states(state,provider,verifier,return_to,expires_at) VALUES(?,?,?,?,?)", (state, provider, verifier, return_to, expires))
        db.commit()
    return state


def consume_oauth_state(provider: str, state: str) -> tuple[str, str]:
    with connect() as db:
        row = db.execute("SELECT * FROM oauth_states WHERE state=? AND provider=?", (state, provider)).fetchone()
        if not row:
            raise HTTPException(400, "invalid OAuth state")
        db.execute("DELETE FROM oauth_states WHERE state=?", (state,))
        db.commit()
    if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(400, "expired OAuth state")
    return row["verifier"], row["return_to"]


def save_provider_token(provider: str, token: dict[str, Any]) -> None:
    encrypted = token_cipher().encrypt(json.dumps(token).encode()).decode()
    with connect() as db:
        db.execute(
            "INSERT INTO oauth_tokens(provider,encrypted_json,updated_at) VALUES(?,?,?) ON CONFLICT(provider) DO UPDATE SET encrypted_json=excluded.encrypted_json,updated_at=excluded.updated_at",
            (provider, encrypted, now_iso()),
        )
        db.commit()


@app.get("/v1/auth/providers")
def auth_providers() -> dict[str, Any]:
    google_ready = bool(os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET") and os.environ.get("MIRROR_TOKEN_KEY"))
    microsoft_ready = bool(os.environ.get("MICROSOFT_CLIENT_ID") and os.environ.get("MICROSOFT_CLIENT_SECRET") and os.environ.get("MIRROR_TOKEN_KEY"))
    return {
        "default_provider": DEFAULT_PROVIDER,
        "providers": [
            {"id": "google_workspace", "default": True, "oauth_ready": google_ready, "start": "/v1/auth/google/start"},
            {"id": "microsoft_365", "default": False, "oauth_ready": microsoft_ready, "start": "/v1/auth/microsoft/start"},
            {"id": "apple_manual", "default": False, "oauth_ready": False, "note": "No claim of general iCloud Drive OAuth access; use explicit file/ICS handoff unless a verified adapter is installed."},
        ],
    }


@app.get("/v1/auth/google/start")
def google_start(return_to: str = Query(default="/"), capabilities: str = Query(default="identity")) -> RedirectResponse:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", f"{PUBLIC_BASE_URL}/v1/auth/google/callback")
    if not client_id:
        raise HTTPException(503, "Google OAuth client is not configured")
    token_cipher()
    verifier, challenge = pkce_pair()
    state = store_oauth_state("google", verifier, return_to)
    scopes = {"openid", "email", "profile"}
    requested = {item.strip() for item in capabilities.split(",") if item.strip()}
    if "drive" in requested:
        scopes.add("https://www.googleapis.com/auth/drive.file")
    if "sheets" in requested:
        scopes.add("https://www.googleapis.com/auth/spreadsheets")
    if "calendar" in requested:
        scopes.add("https://www.googleapis.com/auth/calendar.events")
    if "gmail_read" in requested:
        scopes.add("https://www.googleapis.com/auth/gmail.readonly")
    params = {
        "client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code",
        "scope": " ".join(sorted(scopes)), "access_type": "offline", "include_granted_scopes": "true",
        "prompt": "consent", "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
    }
    return RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


@app.get("/v1/auth/google/callback")
async def google_callback(code: str, state: str) -> RedirectResponse:
    verifier, return_to = consume_oauth_state("google", state)
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", f"{PUBLIC_BASE_URL}/v1/auth/google/callback")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code, "client_id": client_id, "client_secret": client_secret,
            "redirect_uri": redirect_uri, "grant_type": "authorization_code", "code_verifier": verifier,
        })
    if response.status_code >= 400:
        raise HTTPException(502, "Google token exchange failed")
    save_provider_token("google", response.json())
    return RedirectResponse(return_to or "/")


@app.get("/v1/auth/microsoft/start")
def microsoft_start(return_to: str = Query(default="/"), capabilities: str = Query(default="identity")) -> RedirectResponse:
    client_id = os.environ.get("MICROSOFT_CLIENT_ID", "").strip()
    tenant = os.environ.get("MICROSOFT_TENANT", "common").strip() or "common"
    redirect_uri = os.environ.get("MICROSOFT_REDIRECT_URI", f"{PUBLIC_BASE_URL}/v1/auth/microsoft/callback")
    if not client_id:
        raise HTTPException(503, "Microsoft OAuth client is not configured")
    token_cipher()
    verifier, challenge = pkce_pair()
    state = store_oauth_state("microsoft", verifier, return_to)
    scopes = {"openid", "email", "profile", "offline_access", "User.Read"}
    requested = {item.strip() for item in capabilities.split(",") if item.strip()}
    if "drive" in requested:
        scopes.add("Files.ReadWrite")
    if "calendar" in requested:
        scopes.add("Calendars.ReadWrite")
    if "mail_read" in requested:
        scopes.add("Mail.Read")
    params = {
        "client_id": client_id, "redirect_uri": redirect_uri, "response_type": "code",
        "response_mode": "query", "scope": " ".join(sorted(scopes)), "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
    }
    return RedirectResponse(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?" + urlencode(params))


@app.get("/v1/auth/microsoft/callback")
async def microsoft_callback(code: str, state: str) -> RedirectResponse:
    verifier, return_to = consume_oauth_state("microsoft", state)
    tenant = os.environ.get("MICROSOFT_TENANT", "common").strip() or "common"
    redirect_uri = os.environ.get("MICROSOFT_REDIRECT_URI", f"{PUBLIC_BASE_URL}/v1/auth/microsoft/callback")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token", data={
            "code": code, "client_id": os.environ.get("MICROSOFT_CLIENT_ID", ""),
            "client_secret": os.environ.get("MICROSOFT_CLIENT_SECRET", ""), "redirect_uri": redirect_uri,
            "grant_type": "authorization_code", "code_verifier": verifier,
        })
    if response.status_code >= 400:
        raise HTTPException(502, "Microsoft token exchange failed")
    save_provider_token("microsoft", response.json())
    return RedirectResponse(return_to or "/")
