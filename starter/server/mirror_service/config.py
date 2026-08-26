from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    public_base_url: str
    provider_default: str
    state_backend: str
    google_client_id: str
    google_client_secret: str
    token_encryption_key: str
    meta_db: str
    file_store: str
    web_root: str
    session_secure: bool
    postgres_dsn: str

    @classmethod
    def from_env(cls) -> "Settings":
        provider = os.getenv("MIRROR_PROVIDER_DEFAULT", "google").strip().lower() or "google"
        backend = os.getenv("MIRROR_STATE_BACKEND", provider).strip().lower() or provider
        if provider not in {"google", "microsoft", "manual"}:
            raise ValueError(f"unsupported MIRROR_PROVIDER_DEFAULT: {provider}")
        if backend not in {"google", "postgres", "memory"}:
            raise ValueError(f"unsupported MIRROR_STATE_BACKEND: {backend}")
        return cls(
            public_base_url=os.getenv("MIRROR_PUBLIC_BASE_URL", "http://localhost:8080").rstrip("/"),
            provider_default=provider,
            state_backend=backend,
            google_client_id=os.getenv("MIRROR_GOOGLE_CLIENT_ID", "").strip(),
            google_client_secret=os.getenv("MIRROR_GOOGLE_CLIENT_SECRET", "").strip(),
            token_encryption_key=os.getenv("MIRROR_TOKEN_ENCRYPTION_KEY", "").strip(),
            meta_db=os.getenv("MIRROR_META_DB", "/data/mirror-meta.sqlite3"),
            file_store=os.getenv("MIRROR_FILE_STORE", "/data/evidence"),
            web_root=os.getenv("MIRROR_WEB_ROOT", "/app/pwa"),
            session_secure=os.getenv("MIRROR_SESSION_SECURE", "false").strip().lower() in {"1", "true", "yes"},
            postgres_dsn=os.getenv("MIRROR_POSTGRES_DSN", "").strip(),
        )

    @property
    def google_oauth_ready(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret and self.token_encryption_key)
