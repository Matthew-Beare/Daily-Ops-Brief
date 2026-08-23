#!/usr/bin/env python3
"""Normalize employer/shared run-sheet evidence into unique canonical Route upserts.

Historical run sheets are evidence for reusable terminal-pair paid mileage. They do
NOT create one historical Trip/Mileage row per source occurrence. Actual LifeOS
Trips remain the separately audited work occurrences created from live/company
evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from typing import Any

PAIR_RE = re.compile(r"^\s*([A-Za-z0-9]{2,8})\s*-\s*([A-Za-z0-9]{2,8})\s*$")

# Proven source typo/alias corrections. Extend only with evidence; never fuzzy-merge
# terminal codes merely because they look similar.
TERMINAL_ALIASES = {
    "I4C": "IRC",
}


def normalize_code(value: str) -> str:
    code = re.sub(r"\s+", "", value or "").upper()
    return TERMINAL_ALIASES.get(code, code)


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
    """Return one normalized terminal-pair observation or None.

    Accept conventional TRIP/MILES keys. Connector adapters should normalize odd
    column layouts into those keys before calling this contract.
    """
    trip = str(row.get("trip") or row.get("TRIP") or "").strip()
    match = PAIR_RE.match(trip)
    miles = parse_miles(row.get("miles") if "miles" in row else row.get("MILES"))
    if not match or miles is None:
        return None
    origin, destination = (normalize_code(part) for part in match.groups())
    if not origin or not destination or origin == destination:
        return None
    pair = tuple(sorted((origin, destination)))
    return {
        "origin": origin,
        "destination": destination,
        "pair_a": pair[0],
        "pair_b": pair[1],
        "paid_miles": miles,
        "source_tab": str(row.get("source_tab") or "").strip(),
        "source_date": str(row.get("date") or row.get("DATE") or "").strip(),
    }


def choose_pair_value(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Choose reusable paid miles while retaining variant counts as provenance."""
    values = [int(record["paid_miles"]) for record in records]
    counts = Counter(values)
    max_count = max(counts.values())
    modes = {value for value, count in counts.items() if count == max_count}
    latest = values[-1]

    # A repeated current value can supersede an older modal value after a company
    # mileage-table revision. Otherwise use the unique modal value; ties use the
    # latest observation rather than inventing an average.
    if len(values) >= 3 and values[-3:].count(latest) >= 2:
        chosen = latest
        basis = "recent-repeated"
    elif len(modes) == 1:
        chosen = next(iter(modes))
        basis = "modal"
    else:
        chosen = latest
        basis = "modal-tie-latest"

    return {
        "paid_miles": chosen,
        "selection_basis": basis,
        "observation_count": len(records),
        "source_variants": dict(sorted(counts.items())),
    }


def reconcile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []
    seen_observations: set[tuple[str, str, int, str, str]] = set()
    malformed = 0

    for row in rows:
        item = normalize_row(row)
        if item is None:
            malformed += 1
            continue
        evidence_key = (
            item["origin"],
            item["destination"],
            int(item["paid_miles"]),
            item["source_tab"],
            item["source_date"],
        )
        if evidence_key in seen_observations:
            continue
        seen_observations.add(evidence_key)
        observations.append(item)

    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        by_pair[(item["pair_a"], item["pair_b"])].append(item)

    route_upserts = []
    for (a, b), records in sorted(by_pair.items()):
        choice = choose_pair_value(records)
        route_upserts.append({
            "pair_a": a,
            "pair_b": b,
            "paid_miles_a_to_b": choice["paid_miles"],
            "paid_miles_b_to_a": choice["paid_miles"],
            "selection_basis": choice["selection_basis"],
            "observation_count": choice["observation_count"],
            "source_variants": choice["source_variants"],
        })

    return {
        "status": "ok",
        "symmetric_paid_miles": True,
        "source_row_count": len(rows),
        "valid_observation_count": len(observations),
        "ignored_malformed_count": malformed,
        "route_pair_count": len(route_upserts),
        "historical_occurrences_imported": False,
        "route_upserts": route_upserts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="JSON list of normalized source row objects")
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
        output = reconcile([row for row in rows if isinstance(row, dict)])
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        output = {"status": "error", "errors": [str(exc)]}
    json.dump(output, sys.stdout, indent=2 if args.pretty else None, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if output.get("status") == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
