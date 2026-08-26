from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Protocol

from .google_provider import GoogleWorkspace


class Repository(Protocol):
    def list_entities(self) -> list[dict[str, Any]]: ...
    def upsert_entity(self, entity: dict[str, Any]) -> dict[str, Any]: ...


class MemoryRepository:
    def __init__(self):
        self.rows: dict[str, dict[str, Any]] = {}

    def list_entities(self) -> list[dict[str, Any]]:
        return [dict(v) for v in self.rows.values()]

    def upsert_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        current = self.rows.get(entity["entity_uuid"], {})
        row = dict(entity)
        row["revision"] = int(current.get("revision", 0)) + 1
        self.rows[row["entity_uuid"]] = row
        return dict(row)


class GoogleRepository:
    def __init__(self, google: GoogleWorkspace):
        self.google = google
    def list_entities(self) -> list[dict[str, Any]]:
        return self.google.list_entities()
    def upsert_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        return self.google.upsert_entity(entity)


class PostgresRepository:
    def __init__(self, dsn: str):
        if not dsn:
            raise ValueError("MIRROR_POSTGRES_DSN is required for postgres backend")
        self.dsn = dsn
        self._ensure()

    def _connect(self):
        import psycopg
        return psycopg.connect(self.dsn)

    def _ensure(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS mirror_entities (
                    entity_uuid UUID PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    parent_uuid UUID NULL,
                    name TEXT NOT NULL,
                    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                    updated_at TIMESTAMPTZ NOT NULL,
                    revision BIGINT NOT NULL DEFAULT 1
                )
            """)

    def list_entities(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT entity_type,entity_uuid,parent_uuid,name,payload,updated_at,revision FROM mirror_entities ORDER BY name"
            ).fetchall()
        return [{
            "entity_type": r[0], "entity_uuid": str(r[1]), "parent_uuid": str(r[2]) if r[2] else None,
            "name": r[3], "payload": r[4], "updated_at": r[5].isoformat(), "revision": int(r[6]),
        } for r in rows]

    def upsert_entity(self, entity: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("""
                INSERT INTO mirror_entities(entity_uuid,entity_type,parent_uuid,name,payload,updated_at,revision)
                VALUES(%s,%s,%s,%s,%s::jsonb,%s,1)
                ON CONFLICT(entity_uuid) DO UPDATE SET
                  entity_type=excluded.entity_type,
                  parent_uuid=excluded.parent_uuid,
                  name=excluded.name,
                  payload=excluded.payload,
                  updated_at=excluded.updated_at,
                  revision=mirror_entities.revision+1
                RETURNING revision
            """, (
                entity["entity_uuid"], entity["entity_type"], entity.get("parent_uuid"), entity.get("name", ""),
                json.dumps(entity.get("payload", {})), entity["updated_at"],
            )).fetchone()
        result = dict(entity)
        result["revision"] = int(row[0])
        return result


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
