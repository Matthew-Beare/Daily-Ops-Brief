#!/usr/bin/env python3
"""Deterministic first-boot life-profile, context-mode, and stock-service router."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

SCHEMA_VERSION = 1
STOCK_SERVICES = ("briefs", "order_lifecycle", "recipe_library")


def boolish(value: Any, field: str) -> bool | None:
    """Parse explicit boolean-like input; None/blank means unresolved."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "enabled"}:
        return True
    if text in {"0", "false", "no", "off", "disabled"}:
        return False
    raise ValueError(f"invalid boolean for {field}: {value!r}")


def text(value: Any) -> str:
    return str(value or "").strip()


def classify_life_profile(payload: dict[str, Any]) -> str:
    status = text(payload.get("employment_status")).lower()
    if any(token in status for token in ("retired", "not working", "nonworking")):
        return "retired_nonworking"
    flags = {
        "working": any(token in status for token in ("working", "employed", "self-employed", "self employed")),
        "student": any(token in status for token in ("student", "studying", "school")),
        "caregiving": "caregiv" in status,
    }
    active = [name for name, enabled in flags.items() if enabled]
    if len(active) > 1 or "mixed" in status:
        return "mixed"
    if active:
        return active[0]
    return "custom"


def role_family(job_title: str) -> str:
    role = job_title.lower()
    if any(token in role for token in ("truck", "driver", "courier", "delivery", "road")):
        return "driver"
    if any(token in role for token in ("field", "lineman", "technician", "service tech", "construction", "traveling", "travelling", "flight crew", "crew")):
        return "field"
    if any(token in role for token in ("student", "campus")):
        return "campus"
    return "generic"


def custom_modes(payload: dict[str, Any]) -> list[str] | None:
    raw = payload.get("context_mode_names")
    if raw in (None, ""):
        return None
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("context_mode_names must be a two-item list")
    values = [text(value).upper() for value in raw]
    if not all(values) or values[0] == values[1]:
        raise ValueError("context_mode_names must contain two distinct nonblank labels")
    return values


def context_route(payload: dict[str, Any], profile: str) -> dict[str, Any]:
    explicit = boolish(payload.get("works_away_from_home"), "works_away_from_home")
    selected = custom_modes(payload)
    role = role_family(text(payload.get("job_title")))

    if selected:
        return {
            "status": "selected",
            "primary_modes": selected,
            "alternatives": [],
            "reason": "explicit user-selected context labels",
        }

    if profile == "retired_nonworking" and explicit is not True:
        return {
            "status": "bypassed",
            "primary_modes": [],
            "alternatives": [],
            "reason": "retired/nonworking profile has no confirmed recurring away-work context",
        }

    if explicit is False:
        return {
            "status": "bypassed",
            "primary_modes": [],
            "alternatives": [],
            "reason": "user explicitly reported no recurring away-work context",
        }

    suggestions = {
        "driver": (["HOME", "ROAD"], [["HOME", "TRUCK"]]),
        "field": (["HOME", "FIELD"], [["HOME", "AWAY"]]),
        "campus": (["HOME", "CAMPUS"], [["HOME", "AWAY"]]),
        "generic": (["HOME", "AWAY"], []),
    }
    primary, alternatives = suggestions[role]

    if explicit is True:
        return {
            "status": "recommended",
            "primary_modes": primary,
            "alternatives": alternatives,
            "reason": "recurring away-work context confirmed; labels still require user confirmation",
        }

    if role in {"driver", "field"}:
        return {
            "status": "needs_confirmation",
            "primary_modes": primary,
            "alternatives": alternatives,
            "reason": "job duties suggest a context split but recurring away-work evidence is unresolved",
        }

    return {
        "status": "unresolved",
        "primary_modes": [],
        "alternatives": [],
        "reason": "insufficient evidence to justify a context split",
    }


def activation(value: Any, field: str) -> str:
    parsed = boolish(value, field)
    if parsed is None:
        return "unresolved"
    return "enabled" if parsed else "disabled"


def resolve(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    profile = classify_life_profile(payload)
    alias = text(payload.get("profile_alias")) or None
    context = context_route(payload, profile)

    service_inputs = {
        "briefs": "briefs_enabled",
        "order_lifecycle": "order_lifecycle_enabled",
        "recipe_library": "recipe_library_enabled",
    }
    services = {
        name: {
            "provisioned": True,
            "activation": activation(payload.get(field), field),
        }
        for name, field in service_inputs.items()
    }

    appointment_tracking = boolish(payload.get("appointment_tracking"), "appointment_tracking")
    brief_focus: list[str] = []
    if profile == "retired_nonworking":
        brief_focus.extend(["household_admin", "family_commitments", "hobbies_projects"])
        if appointment_tracking is True:
            brief_focus.insert(0, "appointments")
    elif profile in {"working", "mixed"}:
        brief_focus.extend(["next_actions", "work_context"])
    elif profile == "student":
        brief_focus.extend(["deadlines", "study_next_actions"])
    elif profile == "caregiving":
        brief_focus.extend(["appointments", "responsibilities", "next_actions"])
    else:
        brief_focus.append("next_actions")

    return {
        "schema_version": SCHEMA_VERSION,
        "life_profile": profile,
        "profile_alias": alias,
        "profile_alias_storage": "private-mutable-state",
        "context": context,
        "stock_services": services,
        "brief_focus": brief_focus,
        "canonical_timezone_rule": "context-never-overrides-canonical-iana-timezone",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON input file; stdin when omitted")
    args = parser.parse_args()
    try:
        raw = open(args.input, encoding="utf-8").read() if args.input else sys.stdin.read()
        payload = json.loads(raw)
        print(json.dumps(resolve(payload), indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
