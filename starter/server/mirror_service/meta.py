from __future__ import annotations

import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Any


class MetaStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS kv (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS oauth_state (
              state TEXT PRIMARY KEY,
              created_at INTEGER NOT NULL,
              device_code TEXT
            );
            CREATE TABLE IF NOT EXISTS sessions (
              session_id TEXT PRIMARY KEY,
              owner_subject TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS device_codes (
              device_code TEXT PRIMARY KEY,
              user_code TEXT UNIQUE NOT NULL,
              device_name TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              approved INTEGER NOT NULL DEFAULT 0,
              token_hash TEXT
            );
            CREATE TABLE IF NOT EXISTS client_tokens (
              token_hash TEXT PRIMARY KEY,
              device_name TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              revoked INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS idempotency (
              idempotency_key TEXT PRIMARY KEY,
              response_json TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            """)
    def _db(self):
        return sqlite3.connect(self.path)

    def get_json(self, key: str, default: Any = None) -> Any:
        with self._db() as db:
            row = db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return default if row is None else json.loads(row[0])

    def put_json(self, key: str, value: Any) -> None:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
        with self._db() as db:
            db.execute("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, payload))

    def create_oauth_state(self, device_code: str | None = None) -> str:
        state = secrets.token_urlsafe(32)
        with self._db() as db:
            db.execute("INSERT INTO oauth_state(state,created_at,device_code) VALUES(?,?,?)", (state, int(time.time()), device_code))
        return state

    def consume_oauth_state(self, state: str, ttl_seconds: int = 600) -> str | None:
        with self._db() as db:
            row = db.execute("SELECT created_at,device_code FROM oauth_state WHERE state=?", (state,)).fetchone()
            db.execute("DELETE FROM oauth_state WHERE state=?", (state,))
        if not row or int(time.time()) - int(row[0]) > ttl_seconds:
            raise ValueError("OAuth state is missing or expired")
        return row[1]

    def create_session(self, owner_subject: str) -> str:
        session_id = secrets.token_urlsafe(32)
        with self._db() as db:
            db.execute("INSERT INTO sessions(session_id,owner_subject,created_at) VALUES(?,?,?)", (session_id, owner_subject, int(time.time())))
        return session_id

    def session_owner(self, session_id: str) -> str | None:
        if not session_id:
            return None
        with self._db() as db:
            row = db.execute("SELECT owner_subject FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        return None if row is None else str(row[0])

    def create_device_code(self, device_name: str) -> dict[str, str]:
        code = secrets.token_urlsafe(24)
        user_code = "-".join([secrets.token_hex(2).upper(), secrets.token_hex(2).upper()])
        with self._db() as db:
            db.execute("INSERT INTO device_codes(device_code,user_code,device_name,created_at) VALUES(?,?,?,?)",
                       (code, user_code, device_name[:120], int(time.time())))
        return {"device_code": code, "user_code": user_code}

    def get_device(self, device_code: str) -> dict[str, Any] | None:
        with self._db() as db:
            row = db.execute("SELECT user_code,device_name,created_at,approved,token_hash FROM device_codes WHERE device_code=?", (device_code,)).fetchone()
        if not row:
            return None
        return {"user_code": row[0], "device_name": row[1], "created_at": row[2], "approved": bool(row[3]), "token_hash": row[4]}

    def approve_user_code(self, user_code: str) -> str:
        token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._db() as db:
            row = db.execute("SELECT device_code,device_name FROM device_codes WHERE user_code=?", (user_code.upper(),)).fetchone()
            if not row:
                raise KeyError("unknown user code")
            db.execute("UPDATE device_codes SET approved=1, token_hash=? WHERE user_code=?", (token_hash, user_code.upper()))
            db.execute("INSERT OR REPLACE INTO client_tokens(token_hash,device_name,created_at,revoked) VALUES(?,?,?,0)",
                       (token_hash, row[1], int(time.time())))
        self.put_json(f"device_token_once:{row[0]}", token)
        return row[0]

    def consume_device_token(self, device_code: str) -> str | None:
        key = f"device_token_once:{device_code}"
        token = self.get_json(key)
        if token is None:
            return None
        with self._db() as db:
            db.execute("DELETE FROM kv WHERE key=?", (key,))
        return str(token)

    def validate_client_token(self, token: str) -> bool:
        if not token:
            return False
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._db() as db:
            row = db.execute("SELECT revoked FROM client_tokens WHERE token_hash=?", (token_hash,)).fetchone()
        return bool(row and not row[0])

    def idempotency_get(self, key: str) -> Any:
        with self._db() as db:
            row = db.execute("SELECT response_json FROM idempotency WHERE idempotency_key=?", (key,)).fetchone()
        return None if row is None else json.loads(row[0])

    def idempotency_put(self, key: str, response: Any) -> None:
        with self._db() as db:
            db.execute(
                "INSERT OR IGNORE INTO idempotency(idempotency_key,response_json,created_at) VALUES(?,?,?)",
                (key, json.dumps(response, sort_keys=True, separators=(",", ":")), int(time.time())),
            )
