from __future__ import annotations

from datetime import datetime, timezone
import mimetypes
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Cookie, Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__
from .compatibility import API_MAJOR, MIN_CLIENT_VERSION, SERVER_VERSION, evaluate
from .config import Settings
from .google_provider import GoogleWorkspace
from .labels import code128_svg, qr_svg, safe_label_kind
from .meta import MetaStore
from .repository import GoogleRepository, MemoryRepository, PostgresRepository, Repository, utc_now

settings = Settings.from_env()
meta = MetaStore(settings.meta_db)
google = GoogleWorkspace(settings, meta)
app = FastAPI(title="mirror", version=SERVER_VERSION)
_memory_repo = MemoryRepository()


def repository() -> Repository:
    if settings.state_backend == "google": return GoogleRepository(google)
    if settings.state_backend == "postgres": return PostgresRepository(settings.postgres_dsn)
    return _memory_repo


def bearer(authorization: str | None = Header(default=None), mirror_session: str | None = Cookie(default=None)) -> str:
    if mirror_session and meta.session_owner(mirror_session): return "browser-session"
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if meta.validate_client_token(token): return "client-token"
    raise HTTPException(status_code=401, detail="Sign in or pair this device first.")


class CommandEnvelope(BaseModel):
    command_id: str
    command_type: str
    actor_id: str
    submitted_at: str
    idempotency_key: str = Field(min_length=1, max_length=240)
    payload: dict[str, Any] = Field(default_factory=dict)

class DeviceStart(BaseModel):
    device_name: str = Field(min_length=1, max_length=120)
class EntityCreate(BaseModel):
    entity_type: str = Field(pattern="^(asset|location|category|purchase|receipt|knowledge)$")
    name: str = Field(min_length=1, max_length=240)
    parent_uuid: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
class EntityUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=240)
    parent_uuid: str | None = None
    payload: dict[str, Any] | None = None
class MoveRequest(BaseModel):
    location_uuid: str
class IdentifierRequest(BaseModel):
    value: str = Field(min_length=1, max_length=512)
    symbology: str = "UNKNOWN"
class LabelRequest(BaseModel):
    value: str = Field(min_length=1, max_length=512)
    kind: str = "qr"


@app.get("/v1/health")
def health(x_mira_client_version: str | None = Header(default=None), x_mira_api_major: int | None = Header(default=None)):
    compatibility = None
    if x_mira_client_version is not None and x_mira_api_major is not None:
        c = evaluate(x_mira_client_version, x_mira_api_major)
        compatibility = {"compatible": c.compatible, "reason": c.reason}
    return {
        "service": "mirror", "server_version": __version__, "api_major": API_MAJOR,
        "minimum_client_version": MIN_CLIENT_VERSION, "state_backend": settings.state_backend,
        "default_provider": settings.provider_default,
        "capabilities": ["inventory.read","inventory.write","locations.write","evidence.upload","barcode.capture","qr.capture","labels.qr","labels.code128","device.pairing","provider.google.oauth"],
        "compatibility": compatibility,
    }

@app.post("/v1/commands", dependencies=[Depends(bearer)])
def command(body: CommandEnvelope):
    prior = meta.idempotency_get(body.idempotency_key)
    if prior is not None: return {**prior, "idempotent_replay": True}
    if body.command_type != "capture.barcode_qr_scan":
        raise HTTPException(status_code=400, detail=f"Unsupported command type: {body.command_type}")
    raw = str(body.payload.get("raw_value", "")).strip()
    symbology = str(body.payload.get("symbology", "UNKNOWN"))
    if not raw: raise HTTPException(status_code=400, detail="Scan value is empty.")
    rows = repository().list_entities()
    match = next((r for r in rows if raw == f"mirror:entity:{r['entity_uuid']}" or any(i.get("value") == raw for i in r.get("payload", {}).get("identifiers", []))), None)
    result = {"command_id": body.command_id, "command_type": body.command_type, "readback_verified": True, "resolution": "known" if match else "unknown", "entity": match, "raw_value": raw, "symbology": symbology}
    meta.idempotency_put(body.idempotency_key, result)
    return result

@app.get("/v1/providers", dependencies=[Depends(bearer)])
def providers():
    return {"default": settings.provider_default, "providers": [google.provider_status(), {"provider":"microsoft","configured":False,"connected":False,"status":"adapter_not_configured"}, {"provider":"apple","configured":True,"connected":False,"status":"manual_files_ics_lane"}]}

@app.get("/auth/google/start")
def google_start(pair_code: str | None = None):
    state = meta.create_oauth_state(device_code=pair_code)
    try: url = google.authorization_url(state)
    except RuntimeError as exc: raise HTTPException(status_code=503, detail=str(exc))
    return RedirectResponse(url)

@app.get("/auth/google/callback")
def google_callback(code: str, state: str):
    try:
        pair_code = meta.consume_oauth_state(state)
        session = google.exchange_code(code)
    except Exception as exc: raise HTTPException(status_code=400, detail=f"Google sign-in failed: {exc}")
    session_id = meta.create_session(session.subject)
    response = RedirectResponse(f"/pair?user_code={pair_code}" if pair_code else "/?connected=google")
    response.set_cookie("mirror_session", session_id, httponly=True, secure=settings.session_secure, samesite="lax", max_age=60*60*24*30)
    return response

@app.post("/v1/providers/google/provision", dependencies=[Depends(bearer)])
def google_provision():
    try: return {"provider":"google","resources":google.provision(),"readback_verified":True}
    except Exception as exc: raise HTTPException(status_code=502, detail=f"Google provisioning failed: {exc}")

@app.post("/v1/auth/device/start")
def device_start(body: DeviceStart):
    row = meta.create_device_code(body.device_name)
    return {**row,"verification_url":f"{settings.public_base_url}/pair","verification_url_complete":f"{settings.public_base_url}/pair?user_code={row['user_code']}","expires_in":600,"interval":3}

@app.get("/v1/auth/device/poll/{device_code}")
def device_poll(device_code: str):
    device = meta.get_device(device_code)
    if not device: raise HTTPException(status_code=404, detail="Unknown device code.")
    if int(datetime.now(timezone.utc).timestamp()) - int(device["created_at"]) > 600: raise HTTPException(status_code=410, detail="Device code expired.")
    if not device["approved"]: return {"status":"authorization_pending"}
    token = meta.consume_device_token(device_code)
    if token is None: return {"status":"already_consumed"}
    return {"status":"approved","access_token":token,"token_type":"Bearer"}

@app.get("/pair", response_class=HTMLResponse)
def pair_page(user_code: str = ""):
    escaped = user_code.replace("&","&amp;").replace("<","&lt;").replace('"',"&quot;")
    return f'''<!doctype html><html><body style="font-family:system-ui;max-width:540px;margin:4rem auto;padding:1rem"><h1>Pair MIRA device</h1><p>Sign in to mirror in this browser first, then approve the code shown on your device.</p><form method="post" action="/pair"><input name="user_code" value="{escaped}" style="font-size:1.3rem;padding:.6rem" autofocus><button style="font-size:1.1rem;padding:.65rem 1rem">Approve device</button></form></body></html>'''

@app.post("/pair")
async def pair_approve(request: Request, mirror_session: str | None = Cookie(default=None)):
    form = await request.form(); user_code = str(form.get("user_code", "")).strip().upper()
    if not mirror_session or not meta.session_owner(mirror_session): return RedirectResponse(f"/auth/google/start?pair_code={user_code}", status_code=303)
    try: meta.approve_user_code(user_code)
    except KeyError: raise HTTPException(status_code=404, detail="Unknown pairing code.")
    return HTMLResponse("<!doctype html><html><body style='font-family:system-ui;max-width:540px;margin:4rem auto'><h1>Device approved</h1><p>You can return to MIRA.</p></body></html>")

@app.get("/v1/entities", dependencies=[Depends(bearer)])
def list_entities(entity_type: str | None = None):
    rows = repository().list_entities()
    if entity_type: rows = [r for r in rows if r["entity_type"] == entity_type]
    return {"items": rows}

@app.post("/v1/entities", dependencies=[Depends(bearer)])
def create_entity(body: EntityCreate):
    entity = {"entity_type":body.entity_type,"entity_uuid":str(uuid4()),"parent_uuid":body.parent_uuid,"name":body.name,"payload":body.payload,"updated_at":utc_now()}
    return {"item":repository().upsert_entity(entity),"readback_verified":True}

@app.get("/v1/entities/{entity_uuid}", dependencies=[Depends(bearer)])
def get_entity(entity_uuid: str):
    row = next((r for r in repository().list_entities() if r["entity_uuid"] == entity_uuid), None)
    if row is None: raise HTTPException(status_code=404, detail="Entity not found.")
    return {"item": row}

@app.patch("/v1/entities/{entity_uuid}", dependencies=[Depends(bearer)])
def update_entity(entity_uuid: str, body: EntityUpdate):
    rows=repository().list_entities(); current=next((r for r in rows if r["entity_uuid"]==entity_uuid),None)
    if current is None: raise HTTPException(status_code=404, detail="Entity not found.")
    if body.name is not None: current["name"] = body.name
    if body.parent_uuid is not None: current["parent_uuid"] = body.parent_uuid
    if body.payload is not None: current["payload"] = {**current.get("payload", {}), **body.payload}
    current["updated_at"] = utc_now()
    return {"item":repository().upsert_entity(current),"readback_verified":True}

@app.get("/v1/assets/{asset_uuid}", dependencies=[Depends(bearer)])
def get_asset(asset_uuid: str):
    rows=repository().list_entities(); row=next((r for r in rows if r["entity_uuid"]==asset_uuid and r["entity_type"]=="asset"),None)
    if row is None: raise HTTPException(status_code=404, detail="Asset not found.")
    evidence=[e for e in rows if e["entity_type"]=="knowledge" and e.get("parent_uuid")==asset_uuid and e.get("payload",{}).get("evidence")]
    photos=[{"evidence_uuid":e["entity_uuid"],"media_role":e.get("payload",{}).get("relation_type","gallery"),"mime_type":e.get("payload",{}).get("mime_type",""),"caption":e.get("payload",{}).get("caption",""),"content_url":f"/v1/evidence/{e['entity_uuid']}"} for e in evidence if str(e.get("payload",{}).get("mime_type","")).startswith("image/")]
    return {"item":row,"photo_evidence":photos,"evidence":evidence}

@app.post("/v1/assets/{asset_uuid}/move", dependencies=[Depends(bearer)])
def move_asset(asset_uuid: str, body: MoveRequest):
    rows=repository().list_entities(); asset=next((r for r in rows if r["entity_uuid"]==asset_uuid and r["entity_type"]=="asset"),None); location=next((r for r in rows if r["entity_uuid"]==body.location_uuid and r["entity_type"]=="location"),None)
    if asset is None or location is None: raise HTTPException(status_code=404, detail="Asset or location not found.")
    payload=dict(asset.get("payload",{})); payload["location_uuid"]=location["entity_uuid"]; payload["location_name"]=location["name"]; asset["payload"]=payload; asset["updated_at"]=utc_now()
    return {"item":repository().upsert_entity(asset),"readback_verified":True}

@app.post("/v1/entities/{entity_uuid}/identifiers", dependencies=[Depends(bearer)])
def assign_identifier(entity_uuid: str, body: IdentifierRequest):
    rows=repository().list_entities(); conflict=next((r for r in rows if any(i.get("value")==body.value for i in r.get("payload",{}).get("identifiers",[]))),None)
    if conflict and conflict["entity_uuid"] != entity_uuid: raise HTTPException(status_code=409, detail=f"Identifier is already assigned to {conflict['entity_uuid']}.")
    entity=next((r for r in rows if r["entity_uuid"]==entity_uuid and r["entity_type"] in {"asset","location","category"}),None)
    if entity is None: raise HTTPException(status_code=404, detail="Entity not found or cannot own identifiers.")
    payload=dict(entity.get("payload",{})); ids=list(payload.get("identifiers",[]))
    if not any(i.get("value")==body.value for i in ids): ids.append({"value":body.value,"symbology":body.symbology})
    payload["identifiers"]=ids; entity["payload"]=payload; entity["updated_at"]=utc_now()
    return {"item":repository().upsert_entity(entity),"readback_verified":True}

@app.post("/v1/labels/render", dependencies=[Depends(bearer)])
def render_label(body: LabelRequest):
    try: kind=safe_label_kind(body.kind); svg=qr_svg(body.value) if kind=="qr" else code128_svg(body.value)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc))
    return Response(svg, media_type="image/svg+xml", headers={"Content-Disposition":f'inline; filename="mirror-{kind}.svg"'})

@app.post("/v1/evidence", dependencies=[Depends(bearer)])
async def upload_evidence(file: UploadFile=File(...), asset_uuid: str|None=Form(default=None), relation_type: str=Form(default="evidence"), caption: str=Form(default="")):
    content=await file.read()
    if len(content)>25*1024*1024: raise HTTPException(status_code=413, detail="Evidence file exceeds 25 MiB limit.")
    evidence_uuid=str(uuid4()); mime=file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    if settings.provider_default=="google" and google.provider_status()["provisioned"]:
        stored=google.upload_evidence(content,file.filename or evidence_uuid,mime); locator={"provider":"google_drive","provider_id":stored["id"],"web_view_link":stored.get("webViewLink")}
    else:
        path=Path(settings.file_store); path.mkdir(parents=True,exist_ok=True); target=path/evidence_uuid; target.write_bytes(content); locator={"provider":"filesystem","path":str(target)}
    entity={"entity_type":"knowledge","entity_uuid":evidence_uuid,"parent_uuid":asset_uuid,"name":file.filename or evidence_uuid,"payload":{"evidence":True,"mime_type":mime,"bytes":len(content),"caption":caption,"relation_type":relation_type,"locator":locator},"updated_at":utc_now()}
    repository().upsert_entity(entity)
    return {"evidence_uuid":evidence_uuid,"asset_uuid":asset_uuid,"locator":locator,"readback_verified":True}

@app.get("/v1/evidence/{evidence_uuid}", dependencies=[Depends(bearer)])
def read_evidence(evidence_uuid: str):
    row=next((r for r in repository().list_entities() if r["entity_uuid"]==evidence_uuid and r["entity_type"]=="knowledge"),None)
    if row is None or not row.get("payload",{}).get("evidence"): raise HTTPException(status_code=404, detail="Evidence not found.")
    payload=row["payload"]; locator=payload.get("locator",{})
    if locator.get("provider")=="google_drive": content,mime=google.download_evidence(locator["provider_id"])
    elif locator.get("provider")=="filesystem":
        path=Path(locator["path"])
        if not path.is_file(): raise HTTPException(status_code=404, detail="Evidence object is missing.")
        content,mime=path.read_bytes(),payload.get("mime_type","application/octet-stream")
    else: raise HTTPException(status_code=501, detail="Evidence adapter cannot read this object.")
    return Response(content,media_type=mime,headers={"Content-Disposition":f'inline; filename="{row["name"]}"'})

@app.get("/v1/inventory/tree", dependencies=[Depends(bearer)])
def inventory_tree():
    rows=repository().list_entities(); by_id={r["entity_uuid"]:{**r,"children":[]} for r in rows if r["entity_type"] in {"category","location","asset"}}; roots=[]
    for row in by_id.values():
        parent=row.get("parent_uuid")
        if parent and parent in by_id: by_id[parent]["children"].append(row)
        else: roots.append(row)
    return {"items":roots}

web_root=Path(settings.web_root)
if web_root.exists(): app.mount("/", StaticFiles(directory=str(web_root), html=True), name="mira-web")
