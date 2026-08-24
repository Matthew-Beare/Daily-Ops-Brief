#!/usr/bin/env python3
"""Runtime compatibility layer for the Daily Ops Brief policy engine.

This keeps the mature 3.1.x engine intact while enforcing reliability
contracts that scheduled runs require:

1. an active trip forces ROAD when no live explicit Mode Override exists;
2. mileage/pay is section-scoped, never a global strict-input prerequisite;
3. Home early keeps the Friday 2:45 PM brief in HOME mode and closes the
   current work-cycle accrual immediately;
4. canonical brief-slot checks convert the current instant into the configured
   IANA timezone instead of trusting travel/device timezone or static offsets.

Delete this layer once the same behavior is folded into ops_policy.py and its
full regression suite.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, time, timedelta
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import ops_policy as base


POLICY_VERSION = "3.1.3"
MILEAGE_KEYS = {"mileage_values", "mileage_settings_values"}
CANONICAL_BRIEF_TIMEZONE = base.TZ_NAME
CANONICAL_BRIEF_SLOTS: tuple[tuple[int, int], ...] = ((2, 45), (14, 45))

# The live Routes sheet retains two physical paid-mile columns so the schema can
# represent an explicit directional exception. The current deployment's standing
# policy is symmetric by terminal pair: a verified A↔B paid-mile value is written
# to and used in both columns unless the owner explicitly records an exception.
# Route geometry and runtime remain legitimately directional.
base.ROUTE_KEYS.update(
    {
        "paidmilesab": "paid_miles_ab",
        "paidmilesba": "paid_miles_ba",
        "milessourceab": "miles_source_ab",
        "milessourceba": "miles_source_ba",
    }
)


def _truthy(value: Any) -> bool:
    return base._truthy(value)


def canonical_clock(moment: datetime, timezone_name: str = CANONICAL_BRIEF_TIMEZONE) -> datetime:
    """Return *moment* represented in the authoritative IANA timezone.

    The input may carry any real offset/timezone. It represents an instant, not
    execution authority. Naive datetimes are rejected because guessing their
    offset would recreate the scheduler bug this guard exists to prevent.
    """
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("Current instant must include an explicit timezone/UTC offset.")
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown IANA timezone: {timezone_name}") from exc
    return moment.astimezone(timezone)


def _normalize_slots(slots: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    normalized: list[tuple[int, int]] = []
    for hour, minute in slots:
        if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
            raise ValueError(f"Invalid canonical slot: {hour:02d}:{minute:02d}")
        slot = (int(hour), int(minute))
        if slot not in normalized:
            normalized.append(slot)
    if not normalized:
        raise ValueError("At least one canonical slot is required.")
    return tuple(normalized)


def canonical_slot_evidence(
    moment: datetime,
    *,
    timezone_name: str = CANONICAL_BRIEF_TIMEZONE,
    slots: Iterable[tuple[int, int]] = CANONICAL_BRIEF_SLOTS,
) -> dict[str, Any]:
    """Return deterministic evidence for canonical-time scheduled-entry checks."""
    normalized_slots = _normalize_slots(slots)
    local = canonical_clock(moment, timezone_name)
    clock = (local.hour, local.minute)
    return {
        "timezone": timezone_name,
        "canonical_now": local.isoformat(),
        "canonical_date": local.date().isoformat(),
        "canonical_clock": local.strftime("%H:%M"),
        "configured_slots": [f"{hour:02d}:{minute:02d}" for hour, minute in normalized_slots],
        "slot_match": clock in normalized_slots,
    }


def _parse_slot(value: str) -> tuple[int, int]:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour, minute = int(hour_text), int(minute_text)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid slot {value!r}; expected HH:MM") from exc
    return _normalize_slots(((hour, minute),))[0]


def _dataset_available(payload: dict[str, Any], values_key: str, object_key: str) -> bool:
    if values_key in payload:
        value = payload.get(values_key)
        return isinstance(value, list) and bool(value) and isinstance(value[0], list)
    if object_key in payload:
        return isinstance(payload.get(object_key), list)
    return False


def _active_trip_present(payload: dict[str, Any]) -> bool:
    rows = base._load_records(payload, "trips", "trips_values", base.TRIP_KEYS)
    return any(base._key(row.get("status")) == "active" for row in rows)


def _mileage_enabled(travel_settings: dict[str, dict[str, Any]]) -> bool:
    return base._key(
        base._setting_value(travel_settings, "Thursday mileage summary")
    ) in {"enabled", "true", "yes", "on", "1"}


def _isolated_mileage_output(
    raw_mileage: list[dict[str, Any]],
    raw_mileage_settings: list[dict[str, Any]],
    raw_trips: list[dict[str, Any]],
    travel_settings: dict[str, dict[str, Any]],
    moment,
    inputs_present: bool,
):
    """Return a non-fatal empty mileage section when its authority is unreadable."""
    due = _mileage_enabled(travel_settings) and moment.astimezone(base.TZ).weekday() == 3
    return {
        "mileage_summary_allowed": due,
        "mileage_summary_due": due,
        "mileage_summary": None,
        "mileage_summary_markdown": "",
        "actions_required": [],
    }, []


def resolve(payload: dict[str, Any]) -> dict[str, Any]:
    """Resolve policy while enforcing section-scoped mileage and active-trip mode."""
    try:
        moment = base.parse_datetime(payload.get("now"), "now")
    except ValueError:
        moment = None

    active_trip = _active_trip_present(payload)
    mileage_available = (
        _dataset_available(payload, "mileage_values", "mileage")
        and _dataset_available(
            payload, "mileage_settings_values", "mileage_settings"
        )
    )

    original_strict_keys = base.STRICT_INPUT_KEYS
    original_normal_mode = base.normal_mode
    original_mileage_output = base.mileage_output

    # Mileage/pay is not a global health prerequisite. The Thursday section
    # handles its own degraded state below.
    base.STRICT_INPUT_KEYS = tuple(
        key for key in original_strict_keys if key not in MILEAGE_KEYS
    )

    # resolve_mode_at() calls normal_mode() only when there is no active
    # explicit override, so this preserves the rule: live override > active
    # trip > weekly window.
    if active_trip:
        base.normal_mode = lambda _moment: "ROAD"

    if not mileage_available:
        base.mileage_output = _isolated_mileage_output

    try:
        result = base.resolve(payload)
    finally:
        base.STRICT_INPUT_KEYS = original_strict_keys
        base.normal_mode = original_normal_mode
        base.mileage_output = original_mileage_output

    result["policy_version"] = POLICY_VERSION
    if isinstance(result.get("run_log_fields"), dict):
        result["run_log_fields"]["Policy Version"] = POLICY_VERSION

    # Scheduled/manual callers can inspect the same canonical-clock evidence.
    # It is diagnostic in resolve(); the scheduled brief workflow decides
    # whether a slot mismatch should stop downstream module work.
    if moment is not None:
        evidence = canonical_slot_evidence(moment)
        result["canonical_clock_evidence"] = evidence
        if isinstance(result.get("run_log_fields"), dict):
            result["run_log_fields"]["Canonical Clock (ET)"] = evidence["canonical_clock"]
            result["run_log_fields"]["Canonical Slot Match"] = evidence["slot_match"]

    # Make the real precedence visible instead of calling an active-trip
    # decision merely "normal".
    if active_trip and not result.get("active_override") and result.get("mode") == "ROAD":
        result["mode_source"] = "active_trip"

    if moment is not None and not mileage_available:
        settings_rows = base._load_records(
            payload,
            "travel_settings",
            "travel_settings_values",
            base.SETTING_KEYS,
        )
        settings, _ = base.prepare_settings(settings_rows)
        thursday_due = _mileage_enabled(settings) and moment.astimezone(base.TZ).weekday() == 3
        if thursday_due:
            action = base._action(
                "mileage_pay_sheet_unavailable",
                "Action Required — mileage/pay Sheet unavailable",
            )
            actions = list(result.get("actions_required") or [])
            if action not in actions:
                actions.append(action)
            result["actions_required"] = actions
            result["mileage_summary_allowed"] = True
            result["mileage_summary_due"] = True

            # A missing section authority is degraded, not fatal, unless some
            # unrelated core error already made the run invalid.
            if result.get("status") == "ok":
                result["status"] = "degraded"
                run_log = result.get("run_log_fields") or {}
                run_log["Status"] = "Degraded"
                health = str(run_log.get("Input Health") or "OK")
                run_log["Input Health"] = (
                    health
                    if "mileage/pay" in health.lower()
                    else f"{health}; mileage/pay unavailable"
                )
                run_log["Action Count"] = len(actions)
                result["run_log_fields"] = run_log

    return result


def _next_friday_1500(moment: datetime) -> datetime:
    """Return the next strictly-future Friday 3:00 PM Eastern boundary."""
    local = moment.astimezone(base.TZ)
    days_ahead = (4 - local.weekday()) % 7
    candidate = datetime.combine(
        local.date() + timedelta(days=days_ahead), time(15, 0), base.TZ
    )
    if candidate <= local:
        candidate += timedelta(days=7)
    return candidate


def home_early(moment: datetime) -> dict[str, Any]:
    """Create a HOME override that covers the next Friday 2:45 PM brief."""
    local = moment.astimezone(base.TZ)
    expiry = _next_friday_1500(local)
    return {
        "policy_version": POLICY_VERSION,
        "status": "ok",
        "timezone": base.TZ_NAME,
        "starts_at": local.isoformat(),
        "expires_at": expiry.isoformat(),
        "work_cycle_close_at": local.isoformat(),
        "sheet_fields": {
            "Type": "Mode Override",
            "Item": "Home early",
            "State": "HOME",
            "Starts At (ET)": local.strftime("%-m/%-d/%Y %-H:%M:%S"),
            "Expires At (ET)": expiry.strftime("%-m/%-d/%Y %-H:%M:%S"),
            "Notes": (
                "Force HOME through the next Friday 2:45 PM brief; expiry is "
                "Friday 3:00 PM Eastern and exclusive. Close the current work-"
                "cycle mileage accrual at the confirmed home-arrival time."
            ),
            "Status": "Active",
            "Updated (ET)": local.strftime("%-m/%-d/%Y"),
        },
    }


def _read_json(path: str) -> dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _emit(value: dict[str, Any], pretty: bool) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2 if pretty else None)
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--input", default="-")
    resolve_parser.add_argument("--pretty", action="store_true")

    home_parser = subparsers.add_parser("home-early")
    home_parser.add_argument("--now", required=True)
    home_parser.add_argument("--pretty", action="store_true")

    slot_parser = subparsers.add_parser("slot-check")
    slot_parser.add_argument("--now", required=True)
    slot_parser.add_argument("--timezone", default=CANONICAL_BRIEF_TIMEZONE)
    slot_parser.add_argument(
        "--slot",
        action="append",
        default=None,
        help="Canonical local slot HH:MM; repeat for multiple slots. Defaults to 02:45 and 14:45.",
    )
    slot_parser.add_argument("--pretty", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "resolve":
            output = resolve(_read_json(args.input))
        elif args.command == "home-early":
            now = base.parse_datetime(args.now, "now")
            if now is None:
                raise ValueError("Missing required current timestamp.")
            output = home_early(now)
        else:
            now = base.parse_datetime(args.now, "now")
            if now is None:
                raise ValueError("Missing required current timestamp.")
            slots = (
                tuple(_parse_slot(value) for value in args.slot)
                if args.slot
                else CANONICAL_BRIEF_SLOTS
            )
            output = {
                "policy_version": POLICY_VERSION,
                "status": "ok",
                **canonical_slot_evidence(now, timezone_name=args.timezone, slots=slots),
            }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = {
            "policy_version": POLICY_VERSION,
            "status": "error",
            "errors": [str(exc)],
        }

    _emit(output, args.pretty)
    return 0 if output.get("status") in {"ok", "degraded"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
