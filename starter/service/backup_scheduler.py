from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import threading
import time
import uuid
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _load_defaults() -> dict[str, Any]:
    path = Path(__file__).resolve().parent / "backup-policy.json"
    if not path.is_file():
        path = Path(__file__).resolve().parent.parent / "backup-policy.json"
    return json.loads(path.read_text(encoding="utf-8"))["defaults"]


def install_backup_scheduler(app: Any, core_module: Any) -> None:
    defaults = _load_defaults()
    backup_dir = Path(os.environ.get("MIRROR_BACKUP_DIR", str(Path(core_module.DATA_DIR) / "backups")))
    backup_dir.mkdir(parents=True, exist_ok=True)

    def connect() -> sqlite3.Connection:
        db = sqlite3.connect(core_module.DB_PATH, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS backup_policy (
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              enabled INTEGER NOT NULL,
              full_interval_days INTEGER NOT NULL,
              incremental_interval_days INTEGER NOT NULL,
              destination TEXT NOT NULL,
              retention_mode TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS backup_runs (
              backup_uuid TEXT PRIMARY KEY,
              requested_type TEXT NOT NULL,
              effective_type TEXT NOT NULL,
              destination TEXT NOT NULL,
              status TEXT NOT NULL,
              local_path TEXT,
              sha256 TEXT,
              size_bytes INTEGER,
              provider_locator TEXT,
              readback_verified INTEGER NOT NULL DEFAULT 0,
              detail_json TEXT NOT NULL DEFAULT '{}',
              started_at TEXT NOT NULL,
              completed_at TEXT
            );
            """
        )
        db.execute(
            "INSERT OR IGNORE INTO backup_policy(singleton,enabled,full_interval_days,incremental_interval_days,destination,retention_mode,updated_at) VALUES(1,?,?,?,?,?,?)",
            (
                1 if defaults.get("enabled", True) else 0,
                int(defaults.get("full_interval_days", 7)),
                int(defaults.get("incremental_interval_days", 1)),
                str(defaults.get("destination", "google_drive")),
                str(defaults.get("retention_mode", "keep_until_user_changes")),
                _now_iso(),
            ),
        )
        db.commit()

    def read_policy() -> dict[str, Any]:
        with connect() as db:
            row = db.execute("SELECT * FROM backup_policy WHERE singleton=1").fetchone()
        result = dict(row)
        result["enabled"] = bool(result["enabled"])
        result.pop("singleton", None)
        result["recommendations"] = {
            "full": "once a week",
            "incremental": "once a day",
            "destination": "Google Drive for stock MIRA",
        }
        result["incremental_semantics"] = "full_fallback until complete logical change-journal coverage is certified"
        return result

    def _sqlite_snapshot(target: Path) -> None:
        source = sqlite3.connect(core_module.DB_PATH, timeout=60)
        destination = sqlite3.connect(target)
        try:
            source.backup(destination)
            destination.execute("PRAGMA integrity_check")
            check = destination.execute("PRAGMA integrity_check").fetchone()[0]
            if check != "ok":
                raise RuntimeError(f"SQLite backup integrity check returned {check}")
        finally:
            destination.close()
            source.close()

    def _build_archive(backup_uuid: str, effective_type: str) -> tuple[Path, str, int]:
        final_path = backup_dir / f"mirror-{backup_uuid}-{effective_type}.zip"
        with tempfile.TemporaryDirectory(prefix="mirror-backup-") as temp_dir:
            temp = Path(temp_dir)
            db_copy = temp / "mirror.db"
            _sqlite_snapshot(db_copy)
            manifest: dict[str, Any] = {
                "schema_version": 1,
                "backup_uuid": backup_uuid,
                "effective_type": effective_type,
                "created_at": _now_iso(),
                "files": [],
            }
            evidence_dir = Path(core_module.EVIDENCE_DIR)
            with zipfile.ZipFile(final_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                archive.write(db_copy, "state/mirror.db")
                manifest["files"].append({"path": "state/mirror.db", "size": db_copy.stat().st_size})
                if evidence_dir.is_dir():
                    for path in sorted(evidence_dir.rglob("*")):
                        if not path.is_file() or backup_dir in path.parents:
                            continue
                        relative = path.relative_to(evidence_dir)
                        arcname = f"evidence/{relative.as_posix()}"
                        archive.write(path, arcname)
                        manifest["files"].append({"path": arcname, "size": path.stat().st_size})
                archive.writestr("backup-manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        digest = hashlib.sha256(final_path.read_bytes()).hexdigest()
        return final_path, digest, final_path.stat().st_size

    async def _replicate(backup_uuid: str, path: Path, digest: str, destination: str) -> dict[str, Any]:
        if destination == "local":
            verify = hashlib.sha256(path.read_bytes()).hexdigest()
            return {
                "provider_locator": str(path),
                "readback_verified": verify == digest,
                "provider": "local",
            }
        try:
            import provider_extensions
        except Exception as exc:
            raise HTTPException(503, "cloud backup adapter is unavailable") from exc
        content = path.read_bytes()
        if destination == "google_drive":
            result = await provider_extensions._google_upload(backup_uuid, path.name, "application/zip", content, digest)
        elif destination == "onedrive":
            result = await provider_extensions._microsoft_upload(backup_uuid, path.name, "application/zip", content, digest)
        else:
            raise HTTPException(400, "unsupported backup destination")
        if not result.get("readback_verified"):
            raise HTTPException(502, "backup provider did not pass readback verification")
        return result

    async def run_backup(requested_type: str, destination_override: str | None = None) -> dict[str, Any]:
        if requested_type not in {"full", "incremental"}:
            raise HTTPException(400, "backup type must be full or incremental")
        policy = read_policy()
        destination = destination_override or policy["destination"]
        if destination not in {"google_drive", "onedrive", "local"}:
            raise HTTPException(400, "unsupported backup destination")
        effective_type = "full" if requested_type == "full" else "full_fallback"
        reason = None if requested_type == "full" else "A complete change journal is not yet certified, so MIRA made a full snapshot instead of claiming an unprovable incremental backup."
        backup_uuid = str(uuid.uuid4())
        started = _now_iso()
        with connect() as db:
            db.execute(
                "INSERT INTO backup_runs(backup_uuid,requested_type,effective_type,destination,status,detail_json,started_at) VALUES(?,?,?,?,?,?,?)",
                (backup_uuid, requested_type, effective_type, destination, "running", json.dumps({"fallback_reason": reason}), started),
            )
            db.commit()
        try:
            archive_path, digest, size = _build_archive(backup_uuid, effective_type)
            replication = await _replicate(backup_uuid, archive_path, digest, destination)
            verified = bool(replication.get("readback_verified"))
            if not verified:
                raise RuntimeError("backup readback verification failed")
            completed = _now_iso()
            with connect() as db:
                db.execute(
                    "UPDATE backup_runs SET status='complete',local_path=?,sha256=?,size_bytes=?,provider_locator=?,readback_verified=1,completed_at=? WHERE backup_uuid=?",
                    (str(archive_path), digest, size, replication.get("provider_locator"), completed, backup_uuid),
                )
                db.commit()
            return {
                "readback_verified": True,
                "backup_uuid": backup_uuid,
                "requested_type": requested_type,
                "effective_type": effective_type,
                "fallback_reason": reason,
                "destination": destination,
                "sha256": digest,
                "size_bytes": size,
                "provider_locator": replication.get("provider_locator"),
            }
        except Exception as exc:
            with connect() as db:
                db.execute(
                    "UPDATE backup_runs SET status='failed',detail_json=?,completed_at=? WHERE backup_uuid=?",
                    (json.dumps({"error": type(exc).__name__, "message": str(exc)[:500], "fallback_reason": reason}), _now_iso(), backup_uuid),
                )
                db.commit()
            raise

    @app.get("/v1/backups/policy")
    def get_backup_policy() -> dict[str, Any]:
        return read_policy()

    @app.patch("/v1/backups/policy")
    async def patch_backup_policy(request: Request) -> dict[str, Any]:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(400, "backup policy object is required")
        current = read_policy()
        enabled = bool(payload.get("enabled", current["enabled"]))
        full_days = int(payload.get("full_interval_days", current["full_interval_days"]))
        incremental_days = int(payload.get("incremental_interval_days", current["incremental_interval_days"]))
        destination = str(payload.get("destination", current["destination"]))
        if not 1 <= full_days <= 365 or not 1 <= incremental_days <= 365:
            raise HTTPException(400, "backup intervals must be between 1 and 365 days")
        if destination not in {"google_drive", "onedrive", "local"}:
            raise HTTPException(400, "unsupported backup destination")
        with connect() as db:
            db.execute(
                "UPDATE backup_policy SET enabled=?,full_interval_days=?,incremental_interval_days=?,destination=?,updated_at=? WHERE singleton=1",
                (1 if enabled else 0, full_days, incremental_days, destination, _now_iso()),
            )
            db.commit()
        return {"readback_verified": True, "policy": read_policy()}

    @app.post("/v1/backups/run")
    async def manual_backup(request: Request) -> dict[str, Any]:
        payload = await request.json()
        if not isinstance(payload, dict):
            payload = {}
        return await run_backup(str(payload.get("type") or "full"), payload.get("destination"))

    @app.get("/v1/backups/history")
    def backup_history() -> dict[str, Any]:
        with connect() as db:
            rows = db.execute("SELECT * FROM backup_runs ORDER BY started_at DESC LIMIT 100").fetchall()
        return {"backups": [dict(row) for row in rows]}

    async def _maybe_scheduled_backup() -> None:
        policy = read_policy()
        if not policy["enabled"]:
            return
        now = _now()
        with connect() as db:
            full = db.execute("SELECT completed_at FROM backup_runs WHERE status='complete' AND requested_type='full' ORDER BY completed_at DESC LIMIT 1").fetchone()
            any_run = db.execute("SELECT completed_at FROM backup_runs WHERE status='complete' ORDER BY completed_at DESC LIMIT 1").fetchone()
        full_due = not full or datetime.fromisoformat(full["completed_at"]) <= now - timedelta(days=policy["full_interval_days"])
        incremental_due = not any_run or datetime.fromisoformat(any_run["completed_at"]) <= now - timedelta(days=policy["incremental_interval_days"])
        if full_due:
            await run_backup("full")
        elif incremental_due:
            await run_backup("incremental")

    def scheduler_loop() -> None:
        import asyncio
        while True:
            try:
                asyncio.run(_maybe_scheduled_backup())
            except Exception:
                pass
            time.sleep(3600)

    if os.environ.get("MIRROR_ENABLE_BACKUP_SCHEDULER", "true").strip().lower() in {"1", "true", "yes", "on"}:
        thread = threading.Thread(target=scheduler_loop, name="mirror-backup-scheduler", daemon=True)
        thread.start()
