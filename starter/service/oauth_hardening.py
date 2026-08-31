from __future__ import annotations

import json
import os
from urllib.parse import urlsplit

from cryptography.fernet import Fernet


def _safe_return_to(public_base_url: str, value: str) -> str:
    candidate = (value or "/").strip()
    if candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    try:
        expected = urlsplit(public_base_url)
        parsed = urlsplit(candidate)
    except ValueError:
        return "/"
    if parsed.scheme == expected.scheme and parsed.netloc == expected.netloc:
        return candidate
    return "/"


def install_oauth_hardening(core_module) -> None:
    original_store_state = core_module.store_oauth_state
    original_save = core_module.save_provider_token

    def safe_store_state(provider: str, verifier: str, return_to: str) -> str:
        return original_store_state(
            provider,
            verifier,
            _safe_return_to(core_module.PUBLIC_BASE_URL, return_to),
        )

    def preserving_save(provider: str, token: dict) -> None:
        merged = dict(token)
        key = os.environ.get("MIRROR_TOKEN_KEY", "").strip()
        if key:
            try:
                cipher = Fernet(key.encode("ascii"))
                with core_module.connect() as db:
                    row = db.execute(
                        "SELECT encrypted_json FROM oauth_tokens WHERE provider=?",
                        (provider,),
                    ).fetchone()
                if row:
                    previous = json.loads(cipher.decrypt(row["encrypted_json"].encode()).decode())
                    if not merged.get("refresh_token") and previous.get("refresh_token"):
                        merged["refresh_token"] = previous["refresh_token"]
            except Exception:
                # The canonical save function will still validate encryption configuration.
                # A malformed old token must not be treated as trusted state.
                pass
        original_save(provider, merged)

    core_module.store_oauth_state = safe_store_state
    core_module.save_provider_token = preserving_save
