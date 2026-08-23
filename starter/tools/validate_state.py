#!/usr/bin/env python3
"""Validate a LyfeOS private Git state tree without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

DOMAIN_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
EVENT_TYPE_RE = DOMAIN_RE
FORBIDDEN_SECRET_KEYS = {
    "password",
    "passphrase",
    "access_token",
    "refresh_token",
    "oauth_token",
    "oauth_client_secret",
    "client_secret",
    "private_key",
    "api_key",
    "auth_cookie",
    "session_cookie",
    "cvv",
    "cvc",
    "full_card_number",
    "bank_password",
}


def _timestamp(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a nonempty ISO-8601 timestamp")
        return
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        errors.append(f"{field} is not valid ISO-8601")
        return
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{field} must include an explicit UTC offset or Z")


def _uuid(value: Any, field: str, errors: list[str]) -> str | None:
    if not isinstance(value, str):
        errors.append(f"{field} must be an RFC 4122 UUID string")
        return None
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError):
        errors.append(f"{field} must be an RFC 4122 UUID string")
        return None
    canonical = str(parsed)
    if value.lower() != canonical:
        errors.append(f"{field} must use canonical UUID text: {canonical}")
    return canonical


def _secret_key_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in FORBIDDEN_SECRET_KEYS:
                errors.append(f"forbidden credential field at {path}.{key}")
            errors.extend(_secret_key_errors(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_secret_key_errors(item, f"{path}[{index}]"))
    return errors


def validate_event(value: Any, *, expected_filename: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["event root must be an object"]

    required = {
        "event_id",
        "domain",
        "entity_id",
        "event_type",
        "recorded_at",
        "schema_version",
        "provenance",
        "payload",
    }
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"event missing fields: {', '.join(missing)}")
        return errors

    event_id = _uuid(value.get("event_id"), "event_id", errors)
    if expected_filename and event_id and expected_filename != f"{event_id}.json":
        errors.append(f"event filename must equal {event_id}.json")

    domain = value.get("domain")
    if not isinstance(domain, str) or not DOMAIN_RE.fullmatch(domain):
        errors.append("domain must use lowercase hyphen-case")

    entity_id = value.get("entity_id")
    if not isinstance(entity_id, str) or not entity_id.strip():
        errors.append("entity_id must be a nonempty stable identifier")

    event_type = value.get("event_type")
    if not isinstance(event_type, str) or not EVENT_TYPE_RE.fullmatch(event_type):
        errors.append("event_type must use lowercase hyphen-case")

    _timestamp(value.get("recorded_at"), "recorded_at", errors)
    if "effective_at" in value and value["effective_at"] is not None:
        _timestamp(value["effective_at"], "effective_at", errors)

    schema_version = value.get("schema_version")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool) or schema_version < 1:
        errors.append("schema_version must be a positive integer")

    provenance = value.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        source_type = provenance.get("source_type")
        if not isinstance(source_type, str) or not source_type.strip():
            errors.append("provenance.source_type must be nonempty")
        if "source_id" in provenance and not isinstance(provenance["source_id"], str):
            errors.append("provenance.source_id must be a string when present")
        if "captured_at" in provenance:
            _timestamp(provenance["captured_at"], "provenance.captured_at", errors)

    if not isinstance(value.get("payload"), dict):
        errors.append("payload must be an object")

    errors.extend(_secret_key_errors(value))
    return errors


def validate_snapshot(value: Any, *, expected_domain: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["snapshot root must be an object"]

    required = {"domain", "schema_version", "updated_at", "source_event_ids", "items"}
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"snapshot missing fields: {', '.join(missing)}")
        return errors

    domain = value.get("domain")
    if not isinstance(domain, str) or not DOMAIN_RE.fullmatch(domain):
        errors.append("snapshot.domain must use lowercase hyphen-case")
    if expected_domain and domain != expected_domain:
        errors.append(f"snapshot.domain must equal filename domain {expected_domain}")

    schema_version = value.get("schema_version")
    if not isinstance(schema_version, int) or isinstance(schema_version, bool) or schema_version < 1:
        errors.append("snapshot.schema_version must be a positive integer")

    _timestamp(value.get("updated_at"), "snapshot.updated_at", errors)

    source_event_ids = value.get("source_event_ids")
    if not isinstance(source_event_ids, list):
        errors.append("snapshot.source_event_ids must be a list")
    else:
        canonical_ids: list[str] = []
        for index, event_id in enumerate(source_event_ids):
            canonical = _uuid(event_id, f"snapshot.source_event_ids[{index}]", errors)
            if canonical:
                canonical_ids.append(canonical)
        if len(canonical_ids) != len(set(canonical_ids)):
            errors.append("snapshot.source_event_ids must not contain duplicates")

    items = value.get("items")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        errors.append("snapshot.items must be a list of objects")

    errors.extend(_secret_key_errors(value))
    return errors


def _load_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: {exc}")
        return None


def validate_state_tree(state_dir: Path) -> list[str]:
    state_dir = state_dir.resolve()
    errors: list[str] = []
    events_dir = state_dir / "events"
    snapshots_dir = state_dir / "snapshots"

    if not events_dir.is_dir():
        errors.append("state/events directory is required")
    if not snapshots_dir.is_dir():
        errors.append("state/snapshots directory is required")
    if errors:
        return errors

    event_ids: set[str] = set()
    for path in sorted(events_dir.glob("**/*.json")):
        value = _load_json(path, errors)
        if value is None:
            continue
        event_errors = validate_event(value, expected_filename=path.name)
        for error in event_errors:
            errors.append(f"{path}: {error}")
        if not event_errors and isinstance(value, dict):
            event_id = str(value["event_id"]).lower()
            if event_id in event_ids:
                errors.append(f"{path}: duplicate event_id {event_id}")
            event_ids.add(event_id)

    for path in sorted(snapshots_dir.glob("*.json")):
        value = _load_json(path, errors)
        if value is None:
            continue
        expected_domain = path.stem
        snapshot_errors = validate_snapshot(value, expected_domain=expected_domain)
        for error in snapshot_errors:
            errors.append(f"{path}: {error}")
        if isinstance(value, dict) and isinstance(value.get("source_event_ids"), list):
            for event_id in value["source_event_ids"]:
                if isinstance(event_id, str) and event_id.lower() not in event_ids:
                    errors.append(f"{path}: source_event_id does not exist in state/events: {event_id}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state_dir", nargs="?", type=Path, default=Path("state"))
    args = parser.parse_args()
    errors = validate_state_tree(args.state_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Git state tree is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
