#!/usr/bin/env python3
"""Run the real Ops policy at any time without claiming a scheduled firing.

A live manual smoke run omits --now so this executable captures its own system
clock. The default AUTO slot selects the current canonical Eastern AM/PM brief
semantics so the smoke test is independent of whatever wall-clock time it runs.
--now exists only for deterministic diagnostics/tests.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ops_policy


MANUAL_MODE = "manual_smoke"


def _read_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _manual_run_id(local: datetime, slot: str) -> str:
    return f"OPS-MANUAL-{local.strftime('%Y%m%d-%H%M%S-%f')}-{slot}"


def _automatic_slot(local: datetime) -> str:
    return "AM" if local.hour < 12 else "PM"


def run_manual_smoke(
    payload: Any,
    *,
    slot: str = "AUTO",
    diagnostic_now: datetime | None = None,
) -> dict[str, Any]:
    """Resolve one actual brief payload outside the scheduler slot gate.

    This uses the same ``ops_policy.resolve`` engine as scheduled briefs. It
    changes only invocation identity/evidence so a manual test cannot be
    mistaken for proof that the 02:45/14:45 dispatcher fired. ``AUTO`` selects
    the current canonical Eastern AM/PM semantics after the runtime clock has
    been captured, making the live smoke path callable at any time.
    """
    requested_slot = str(slot or "AUTO").strip().upper()
    if requested_slot not in {"AUTO", "AM", "PM"}:
        raise ValueError("Manual brief slot must be AUTO, AM, or PM.")
    if not isinstance(payload, dict):
        raise ValueError("Input JSON root must be an object.")

    if diagnostic_now is None:
        captured = datetime.now(timezone.utc)
        clock_source = "runtime_system_clock_manual"
    else:
        if diagnostic_now.tzinfo is None or diagnostic_now.utcoffset() is None:
            raise ValueError("Diagnostic current instant must include a timezone/UTC offset.")
        captured = diagnostic_now.astimezone(timezone.utc)
        clock_source = "explicit_diagnostic_input"

    local = captured.astimezone(ops_policy.TZ)
    selected_slot = _automatic_slot(local) if requested_slot == "AUTO" else requested_slot

    effective = copy.deepcopy(payload)
    effective["now"] = captured.isoformat()
    effective["brief_slot"] = selected_slot
    effective.setdefault("strict_inputs", True)

    output = ops_policy.resolve(effective)
    run_id = _manual_run_id(local, selected_slot)

    output["invocation_mode"] = MANUAL_MODE
    output["run_id"] = run_id
    evidence = output.get("canonical_clock_evidence")
    if isinstance(evidence, dict):
        evidence["clock_source"] = clock_source
        evidence["manual_slot_bypass"] = True
        evidence["scheduled_firing_evidence"] = False

    fields = output.get("run_log_fields")
    if isinstance(fields, dict):
        fields["Run ID"] = run_id
        fields["Phase"] = "manual_smoke_policy_resolved"
        fields["Dispatch State"] = "manual_smoke"
        fields["Logical Slot"] = f"MANUAL-{selected_slot}"
        fields["Effective Scheduled Instant"] = ""
        fields["Dispatch Delay (s)"] = ""
        note = (
            "Manual brief smoke test; real brief pipeline, but not evidence of a "
            "scheduled 02:45/14:45 firing."
        )
        existing = str(fields.get("Error / Notes") or "").strip()
        fields["Error / Notes"] = f"{note} | {existing}" if existing else note

    output["manual_smoke"] = {
        "actual_brief_pipeline": True,
        "slot_gate_bypassed": True,
        "scheduled_firing_evidence": False,
        "clock_source": clock_source,
        "requested_slot_semantics": requested_slot,
        "selected_slot_semantics": selected_slot,
        "slot_selection": "automatic_current_eastern_half_day" if requested_slot == "AUTO" else "explicit",
    }
    return output


def _emit(value: dict[str, Any], pretty: bool) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2 if pretty else None)
    sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="Real/synthetic authority payload JSON, or - for stdin")
    parser.add_argument(
        "--slot",
        default="AUTO",
        choices=("AUTO", "AM", "PM"),
        help="AUTO (default) selects current canonical Eastern AM/PM semantics.",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="Diagnostic only: offset-aware timestamp. Omit for a real manual smoke run.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        diagnostic_now = (
            ops_policy.parse_aware_instant(args.now, "diagnostic current instant")
            if args.now is not None
            else None
        )
        output = run_manual_smoke(
            _read_json(args.input), slot=args.slot, diagnostic_now=diagnostic_now
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = {
            "policy_version": ops_policy.POLICY_VERSION,
            "status": "error",
            "invocation_mode": MANUAL_MODE,
            "errors": [str(exc)],
        }

    _emit(output, args.pretty)
    return 0 if output.get("status") in {"ok", "degraded"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
