from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi import Query, Request
from fastapi.responses import JSONResponse

_CLIENT_RE = re.compile(r"^[^/]+/(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def _version_tuple(value: str) -> tuple[int, int, int] | None:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$", (value or "").strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def _client_version(header: str) -> str | None:
    match = _CLIENT_RE.match((header or "").strip())
    if not match:
        return None
    return ".".join(match.groups())


def install_release_guard(app: Any, release_path: Path, api_major: int, api_contract: str) -> None:
    release = json.loads(release_path.read_text(encoding="utf-8"))
    minimum = release["compatibility"]["minimum_client_version"]
    minimum_tuple = _version_tuple(minimum)
    if minimum_tuple is None:
        raise RuntimeError("release.json minimum_client_version is invalid")

    app.router.routes[:] = [
        route for route in app.router.routes
        if not (getattr(route, "path", None) == "/v1/compatibility" and "GET" in (getattr(route, "methods", set()) or set()))
    ]

    @app.get("/v1/compatibility")
    def compatibility(client_api: str = Query(default=""), client_version: str = Query(default="")) -> dict[str, Any]:
        try:
            major = int(client_api.split(".", 1)[0]) if client_api else None
        except ValueError:
            major = None
        version_tuple = _version_tuple(client_version)
        api_ok = major == api_major
        version_ok = version_tuple is not None and version_tuple >= minimum_tuple
        compatible = api_ok and version_ok
        if not api_ok:
            reason = "unsupported API major; update client or server before mutation"
        elif not version_ok:
            reason = f"client {client_version or 'unknown'} is below minimum supported {minimum}"
        else:
            reason = "compatible"
        return {
            "compatible": compatible,
            "server_api": api_contract,
            "supported_api_majors": [api_major],
            "minimum_client_version": minimum,
            "client_api": client_api or None,
            "client_version": client_version or None,
            "mutation_allowed": compatible,
            "reason": reason,
        }

    @app.middleware("http")
    async def release_guard(request: Request, call_next):
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"} or not request.url.path.startswith("/v1/"):
            return await call_next(request)
        if request.url.path.startswith("/v1/auth/"):
            return await call_next(request)

        api_header = (request.headers.get("X-Mirror-Api-Version") or "").strip()
        try:
            supplied_major = int(api_header.split(".", 1)[0]) if api_header else None
        except ValueError:
            supplied_major = None
        if supplied_major != api_major:
            return JSONResponse(
                {"detail": f"client API {api_header or 'missing'} is incompatible with server API {api_contract}", "minimum_client_version": minimum},
                status_code=426,
            )

        client_header = (request.headers.get("X-Mirror-Client") or "").strip()
        version = _client_version(client_header)
        version_tuple = _version_tuple(version or "")
        if version_tuple is None:
            return JSONResponse(
                {"detail": "mutation requires X-Mirror-Client with semantic version identity", "minimum_client_version": minimum},
                status_code=426,
            )
        if version_tuple < minimum_tuple:
            return JSONResponse(
                {"detail": f"client {version} is below minimum supported {minimum}", "minimum_client_version": minimum},
                status_code=426,
            )
        return await call_next(request)
