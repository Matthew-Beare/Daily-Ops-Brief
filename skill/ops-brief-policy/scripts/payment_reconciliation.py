#!/usr/bin/env python3
"""Reconcile expected merchant charges against pending/posted account observations."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from typing import Any

POLICY_VERSION = "1.0.0"
CENT = Decimal("0.01")


def dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value).replace("$", "").replace(",", "")).quantize(CENT)
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"invalid money value: {value!r}") from exc


def money(value: Decimal) -> str:
    return f"${value.quantize(CENT):,.2f}"


def reconcile_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case.get("payment_case_id") or "").strip()
    receipt_id = str(case.get("receipt_id") or "").strip()
    expected = dec(case.get("expected_amount"))
    merchant_resolution = str(case.get("merchant_resolution") or "").strip().lower()

    if merchant_resolution in {"no_settlement", "revised_before_settlement", "cancelled_before_settlement"}:
        return {
            "payment_case_id": case_id,
            "receipt_id": receipt_id,
            "status": "Resolved No Settlement",
            "expected_amount": money(expected),
            "observed_posted_amount": "$0.00",
            "difference": "$0.00",
            "action_required": False,
        }

    observations = case.get("observations") or []
    if not isinstance(observations, list):
        raise ValueError(f"observations must be a list for {case_id or receipt_id}")

    posted_debits: list[Decimal] = []
    pending_debits: list[Decimal] = []
    posted_credits: list[Decimal] = []

    for row in observations:
        if not isinstance(row, dict):
            continue
        amount = dec(row.get("amount"))
        pending = bool(row.get("pending", False))
        direction = str(row.get("direction") or ("credit" if amount < 0 else "debit")).lower()
        absolute = abs(amount)
        if direction == "credit":
            if not pending:
                posted_credits.append(absolute)
            continue
        if pending:
            pending_debits.append(absolute)
        else:
            posted_debits.append(absolute)

    posted = sum(posted_debits, Decimal("0.00")).quantize(CENT)
    pending = sum(pending_debits, Decimal("0.00")).quantize(CENT)
    credits = sum(posted_credits, Decimal("0.00")).quantize(CENT)
    net_posted = (posted - credits).quantize(CENT)
    difference = (net_posted - expected).quantize(CENT)

    if not posted_debits and not pending_debits:
        status = "Awaiting Settlement"
        action = False
    elif net_posted == expected:
        status = "Split Settlement" if len(posted_debits) > 1 or credits else "Matched"
        action = False
    elif not posted_debits and pending == expected:
        status = "Pending Match"
        action = False
    elif net_posted > expected:
        status = "Overcharged"
        action = True
    elif case.get("settlement_window_complete"):
        status = "Undercharged"
        action = True
    else:
        status = "Awaiting Settlement"
        action = False

    detail = None
    if status == "Overcharged":
        detail = (
            f"possible merchant overcharge: expected {money(expected)}, "
            f"posted {money(net_posted)}, difference {money(difference)}"
        )
    elif status == "Undercharged":
        detail = (
            f"merchant settlement mismatch: expected {money(expected)}, "
            f"posted {money(net_posted)}, difference {money(difference)}"
        )

    return {
        "payment_case_id": case_id,
        "receipt_id": receipt_id,
        "status": status,
        "expected_amount": money(expected),
        "observed_posted_amount": money(net_posted),
        "observed_pending_amount": money(pending),
        "difference": money(difference),
        "action_required": action,
        "detail": detail,
    }


def reconcile(payload: dict[str, Any]) -> dict[str, Any]:
    raw_cases = payload.get("cases") or []
    if not isinstance(raw_cases, list):
        raise ValueError("cases must be a list")
    results = [reconcile_case(row) for row in raw_cases if isinstance(row, dict)]
    return {
        "policy_version": POLICY_VERSION,
        "status": "ok",
        "cases": results,
        "actions_required": [
            {
                "code": "merchant_charge_mismatch",
                "payment_case_id": row["payment_case_id"],
                "receipt_id": row["receipt_id"],
                "detail": row["detail"],
            }
            for row in results
            if row["action_required"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        if args.input == "-":
            payload = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        output = reconcile(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = {"policy_version": POLICY_VERSION, "status": "error", "errors": [str(exc)]}
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0 if output.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
