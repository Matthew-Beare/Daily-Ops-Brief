#!/usr/bin/env python3
"""Normalize employer/shared run-sheet rows for canonical LifeOS reconciliation.

This tool does not write Google Sheets. It converts source rows into stable evidence
records so connector-driven migrations can upsert Routes/Trips/Mileage without
creating a parallel database.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from typing import Any

PAIR_RE = re.compile(r"^\s*([A-Za-z0-9]{2,8})\s*-\s*([A-Za-z0-9]{2,8})\s*$")


def normalize_code(value: str) -> str:
    return re.sub(r"\s+", "", value or "").upper()


def parse_miles(value: Any) -> int | None:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return None
    try:
        miles = int(round(float(text)))
    except ValueError:
        return None
    return miles if miles > 0 else None


def normalize_row(row: dict[str, Any]) -> dict[str, Any] | None:
    trip = str(row.get("trip") or row.get("TRIP") or "").strip()
    match = PAIR_RE.match(trip)
    miles = parse_miles(row.get("miles") if "miles" in row else row.get("MILES"))
    if not match or miles is None:
        return None
    origin, destination = map(normalize_code, match.groups())
    date_text = str(row.get("date") or row.get("DATE") or "").strip()
    source_tab = str(row.get("source_tab") or "").strip()
    pair = tuple(sorted((origin, destination)))
    raw_key = "|".join((source_tab, date_text, origin, destination, str(miles)))
    source_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:20]
    return {
        "source_key": source_key,
        "source_tab": source_tab,
        "source_date": date_text,
        "origin": origin,
        "destination": destination,
        "pair_a": pair[0],
        "pair_b": pair[1],
        "paid_miles": miles,
    }


def choose_pair_value(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Choose reusable paid miles without rewriting source provenance.

    The current user's standing rule is symmetric. For conflicting historical rows,
    prefer the most recently supplied record when the latest value has appeared more
    than once; otherwise prefer the modal value. Connector migration may still apply
    an explicit user/company correction above this result.
    """
    counts = Counter(int(r["paid_miles"]) for r in records)
    latest = int(records[-1]["paid_miles"])
    modal, modal_count = counts.most_common(1)[0]
    if counts[latest] >= 2:
        chosen = latest
        basis = "latest-repeated"
    else:
        chosen = modal
        basis = "modal" if modal_count > 1 else "latest-singleton"
        if modal_count == 1:
            chosen = latest
    return {
        "paid_miles": chosen,
        "basis": basis,
        "observations": len(records),
        "variants": dict(sorted(counts.items())),
    }


def reconcile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        item = normalize_row(row)
        if not item or item["source_key"] in seen:
            continue
        seen.add(item["source_key"])
        normalized.append(item)

    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in normalized:
        by_pair[(item["pair_a"], item["pair_b"])].append(item)

    routes = []
    for (a, b), records in sorted(by_pair.items()):
        choice = choose_pair_value(records)
        routes.append({
            "pair_a": a,
            "pair_b": b,
            "paid_miles_a_to_b": choice["paid_miles"],
            "paid_miles_b_to_a": choice["paid_miles"],
            "selection_basis": choice["basis"],
            "observation_count": choice["observations"],
            "source_variants": choice["variants"],
        })

    return {
        "status": "ok",
        "symmetric_paid_miles": True,
        "occurrences": normalized,
        "route_upserts": routes,
        "occurrence_count": len(normalized),
        "route_pair_count": len(routes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="JSON list of row objects")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        if args.input == "-":
            rows = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as handle:
                rows = json.load(handle)
        if not isinstance(rows, list):
            raise ValueError("input must be a JSON list")
        output = reconcile([r for r in rows if isinstance(r, dict)])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = {"status": "error", "errors": [str(exc)]}
    json.dump(output, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if output.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
