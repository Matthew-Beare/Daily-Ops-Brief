from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_idempotency(app: Any, db_path: Path) -> None:
    def connect() -> sqlite3.Connection:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(db_path, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS command_idempotency (
              idempotency_key TEXT PRIMARY KEY,
              state TEXT NOT NULL,
              response_status INTEGER,
              response_json TEXT,
              created_at TEXT NOT NULL,
              completed_at TEXT
            )
            """
        )
        db.commit()

    @app.middleware("http")
    async def command_idempotency(request: Request, call_next):
        if request.method != "POST" or request.url.path != "/v1/commands":
            return await call_next(request)

        key = (request.headers.get("Idempotency-Key") or "").strip()
        if not key:
            # Older/custom clients remain usable during migration, but official 0.2 clients
            # are tested to send this header for every command mutation.
            return await call_next(request)
        if len(key) > 240:
            return JSONResponse({"detail": "Idempotency-Key exceeds 240 characters"}, status_code=400)

        reserved = False
        try:
            with connect() as db:
                try:
                    db.execute(
                        "INSERT INTO command_idempotency(idempotency_key,state,created_at) VALUES(?,?,?)",
                        (key, "processing", now_iso()),
                    )
                    db.commit()
                    reserved = True
                except sqlite3.IntegrityError:
                    row = db.execute(
                        "SELECT state,response_status,response_json FROM command_idempotency WHERE idempotency_key=?",
                        (key,),
                    ).fetchone()
                    if row and row["state"] == "complete" and row["response_json"] is not None:
                        return Response(
                            content=row["response_json"],
                            status_code=int(row["response_status"] or 200),
                            media_type="application/json",
                            headers={"X-Mirror-Idempotent-Replay": "true"},
                        )
                    return JSONResponse(
                        {"detail": "command with this idempotency key is already processing"},
                        status_code=409,
                        headers={"Retry-After": "1"},
                    )

            response = await call_next(request)
            body = b""
            async for chunk in response.body_iterator:
                body += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")

            headers = dict(response.headers)
            headers.pop("content-length", None)
            rebuilt = Response(
                content=body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

            if 200 <= response.status_code < 300:
                serialized = body.decode("utf-8", errors="strict")
                with connect() as db:
                    db.execute(
                        "UPDATE command_idempotency SET state='complete',response_status=?,response_json=?,completed_at=? WHERE idempotency_key=?",
                        (response.status_code, serialized, now_iso(), key),
                    )
                    db.commit()
            elif reserved:
                with connect() as db:
                    db.execute("DELETE FROM command_idempotency WHERE idempotency_key=?", (key,))
                    db.commit()
            return rebuilt
        except Exception:
            if reserved:
                with connect() as db:
                    db.execute("DELETE FROM command_idempotency WHERE idempotency_key=? AND state='processing'", (key,))
                    db.commit()
            raise
