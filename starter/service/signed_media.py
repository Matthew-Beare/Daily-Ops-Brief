from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from fastapi import HTTPException, Query, Request
from fastapi.responses import FileResponse, Response


def _key() -> bytes:
    explicit = os.environ.get("MIRROR_MEDIA_SIGNING_KEY", "").strip()
    if explicit:
        return explicit.encode("utf-8")
    access = os.environ.get("MIRROR_ACCESS_TOKEN", "").strip()
    if access:
        return hashlib.sha256(("mirror-media:" + access).encode("utf-8")).digest()
    token_key = os.environ.get("MIRROR_TOKEN_KEY", "").strip()
    if token_key:
        return hashlib.sha256(("mirror-media:" + token_key).encode("utf-8")).digest()
    raise HTTPException(503, "media signing requires MIRROR_MEDIA_SIGNING_KEY, MIRROR_ACCESS_TOKEN, or MIRROR_TOKEN_KEY")


def _signature(resource: str, expires: int) -> str:
    message = f"{resource}\n{expires}".encode("utf-8")
    return hmac.new(_key(), message, hashlib.sha256).hexdigest()


def _verify(resource: str, expires: int, signature: str) -> None:
    now = int(time.time())
    if expires < now:
        raise HTTPException(410, "signed media link expired")
    if expires > now + 3600:
        raise HTTPException(400, "signed media link lifetime exceeds maximum")
    expected = _signature(resource, expires)
    if not hmac.compare_digest(expected, signature or ""):
        raise HTTPException(403, "invalid signed media link")


def install_signed_media(app: Any, core_module) -> None:
    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH)
        db.row_factory = sqlite3.Row
        return db

    @app.get("/v1/access-link")
    def access_link(request: Request, resource: str = Query(...), ttl_seconds: int = Query(default=300, ge=30, le=1800)) -> dict[str, Any]:
        if resource.startswith("evidence:"):
            evidence_uuid = resource.split(":", 1)[1]
            with connect() as db:
                if not db.execute("SELECT 1 FROM evidence WHERE uuid=?", (evidence_uuid,)).fetchone():
                    raise HTTPException(404, "evidence not found")
            public_path = f"/media/evidence/{evidence_uuid}"
            signed_resource = resource
        elif resource.startswith("label:"):
            parts = resource.split(":", 2)
            if len(parts) != 3 or parts[2] not in {"qr", "code128"}:
                raise HTTPException(400, "label resource must include qr or code128")
            asset_uuid, kind = parts[1], parts[2]
            with connect() as db:
                if not db.execute("SELECT 1 FROM assets WHERE uuid=?", (asset_uuid,)).fetchone():
                    raise HTTPException(404, "asset not found")
            public_path = f"/media/label/{asset_uuid}.svg?kind={kind}"
            signed_resource = resource
        else:
            raise HTTPException(400, "unsupported signed-media resource")

        expires = int(time.time()) + ttl_seconds
        sig = _signature(signed_resource, expires)
        separator = "&" if "?" in public_path else "?"
        relative = f"{public_path}{separator}{urlencode({'expires': expires, 'sig': sig})}"
        base = str(request.base_url).rstrip("/")
        return {"url": base + relative, "expires_epoch": expires, "ttl_seconds": ttl_seconds}

    @app.get("/media/evidence/{evidence_uuid}")
    def signed_evidence(evidence_uuid: str, expires: int, sig: str) -> FileResponse:
        _verify(f"evidence:{evidence_uuid}", expires, sig)
        with connect() as db:
            row = db.execute("SELECT * FROM evidence WHERE uuid=?", (evidence_uuid,)).fetchone()
        if not row:
            raise HTTPException(404, "evidence not found")
        path = Path(row["storage_path"])
        if not path.is_file():
            raise HTTPException(410, "evidence metadata exists but content is unavailable")
        return FileResponse(
            path,
            media_type=row["mime_type"],
            filename=row["filename"],
            content_disposition_type="inline",
            headers={"Cache-Control": "private, no-store"},
        )

    @app.get("/media/label/{asset_uuid}.svg")
    def signed_label(asset_uuid: str, kind: str, expires: int, sig: str) -> Response:
        if kind not in {"qr", "code128"}:
            raise HTTPException(400, "kind must be qr or code128")
        _verify(f"label:{asset_uuid}:{kind}", expires, sig)
        response = core_module.render_label(asset_uuid, kind)
        response.headers["Cache-Control"] = "private, no-store"
        return response
