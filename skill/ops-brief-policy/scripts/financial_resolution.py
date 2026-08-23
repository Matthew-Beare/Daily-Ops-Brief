#!/usr/bin/env python3
"""Resolve pending cancellation/refund financial exceptions deterministically."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo


TZ = ZoneInfo("America/New_York")
POLICY_VERSION = "1.0.0"
RESOLVED = {"verified", "no_refund_required", "revised_before_settlement"}
PENDING = {"pending", "refund_expected", "reversal_expected", "unknown"}


def parse_time(value: Any) -> datetime:
    if not value:
        raise ValueError("missing expected financial-resolution start time")
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TZ)
    return parsed.astimezone(TZ)


def add_business_days(moment: datetime, count: int) -> datetime:
    """Add Monday-Friday business days, preserving local clock time."""
    current = moment.astimezone(TZ)
    remaining = count
    while remaining:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def money(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        amount = Decimal(str(value).replace("$", "").replace(",", ""))
    except InvalidOperation:
        return None
    return f"${amount.quantize(Decimal('0.01')):,.2f}"


def resolve_case(case: dict[str, Any], now: datetime) -> dict[str, Any]:
    receipt_id = str(case.get("receipt_id") or "").strip()
    vendor = str(case.get("vendor") or "").strip()
    order_number = str(case.get("order_number") or "").strip()
    status = str(case.get("financial_resolution_status") or "unknown").strip().lower()

    if status in RESOLVED:
        return {
            "receipt_id": receipt_id,
            "status": "resolved",
            "action_required": False,
        }
    if status not in PENDING:
        raise ValueError(f"invalid financial_resolution_status for {receipt_id or order_number}: {status}")

    start = parse_time(
        case.get("resolution_expected_at")
        or case.get("cancellation_confirmed_at")
        or case.get("return_accepted_at")
    )
    deadline = add_business_days(start, 5)
    due = now.astimezone(TZ) >= deadline
    expected = money(case.get("expected_amount"))
    missing = str(case.get("missing_evidence") or "posted refund/reversal or confirmed revised charge").strip()
    label = " / ".join(part for part in (vendor, order_number, receipt_id) if part)

    detail = None
    if due:
        amount_text = f" {expected}" if expected else ""
        detail = (
            f"{label} — financial correction{amount_text} still unverified after "
            f"five business days; missing {missing}."
        )

    return {
        "receipt_id": receipt_id,
        "status": "overdue" if due else "pending",
        "action_required": due,
        "deadline_et": deadline.isoformat(),
        "detail": detail,
    }


def resolve(payload: dict[str, Any]) -> dict[str, Any]:
    now = parse_time(payload.get("now"))
    raw_cases = payload.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError("cases must be a list")
    results = [resolve_case(case, now) for case in raw_cases if isinstance(case, dict)]
    return {
        "policy_version": POLICY_VERSION,
        "status": "ok",
        "now": now.isoformat(),
        "cases": results,
        "actions_required": [
            {
                "code": "financial_resolution_overdue",
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
        output = resolve(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = {"policy_version": POLICY_VERSION, "status": "error", "errors": [str(exc)]}
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0 if output.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
