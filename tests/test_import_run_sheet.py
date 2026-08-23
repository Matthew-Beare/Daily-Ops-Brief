from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("import_run_sheet", ROOT / "scripts/import_run_sheet.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class RunSheetImportTests(unittest.TestCase):
    def test_opposite_directions_collapse_to_one_symmetric_pair(self) -> None:
        result = MODULE.reconcile([
            {"DATE": "5/17", "TRIP": "PHX - RTO", "MILES": "312", "source_tab": "current"},
            {"DATE": "5/17", "TRIP": "RTO - PHX", "MILES": "312", "source_tab": "current"},
        ])
        self.assertEqual(result["route_pair_count"], 1)
        route = result["route_upserts"][0]
        self.assertEqual(route["paid_miles_a_to_b"], 312)
        self.assertEqual(route["paid_miles_b_to_a"], 312)
        self.assertFalse(result["historical_occurrences_imported"])
        self.assertNotIn("occurrences", result)

    def test_source_occurrence_dedupes_without_creating_trip_rows(self) -> None:
        row = {"DATE": "5/8-10", "TRIP": "MRT - RTO", "MILES": "2,184", "source_tab": "present"}
        result = MODULE.reconcile([row, dict(row)])
        self.assertEqual(result["valid_observation_count"], 1)
        self.assertEqual(result["route_pair_count"], 1)
        self.assertEqual(result["route_upserts"][0]["paid_miles_a_to_b"], 2184)
        self.assertFalse(result["historical_occurrences_imported"])

    def test_proven_source_alias_does_not_create_duplicate_terminal(self) -> None:
        result = MODULE.reconcile([
            {"DATE": "old", "TRIP": "MRT - IRC", "MILES": "2204", "source_tab": "source"},
            {"DATE": "typo", "TRIP": "MRT - I4C", "MILES": "2204", "source_tab": "source"},
        ])
        self.assertEqual(result["route_pair_count"], 1)
        route = result["route_upserts"][0]
        self.assertEqual((route["pair_a"], route["pair_b"]), ("IRC", "MRT"))

    def test_repeated_latest_can_supersede_old_variant(self) -> None:
        result = MODULE.reconcile([
            {"DATE": "old1", "TRIP": "DEN - KCY", "MILES": "581", "source_tab": "old"},
            {"DATE": "new1", "TRIP": "DEN - KCY", "MILES": "582", "source_tab": "new"},
            {"DATE": "new2", "TRIP": "KCY - DEN", "MILES": "582", "source_tab": "new"},
        ])
        route = result["route_upserts"][0]
        self.assertEqual(route["paid_miles_a_to_b"], 582)
        self.assertEqual(route["selection_basis"], "recent-repeated")
        self.assertEqual(route["source_variants"], {581: 1, 582: 2})

    def test_malformed_rows_are_ignored_not_invented(self) -> None:
        result = MODULE.reconcile([
            {"DATE": "x", "TRIP": "NOT A TERMINAL PAIR", "MILES": "871", "source_tab": "source"},
            {"DATE": "x", "TRIP": "PAR - ELP", "MILES": "", "source_tab": "source"},
        ])
        self.assertEqual(result["valid_observation_count"], 0)
        self.assertEqual(result["route_pair_count"], 0)
        self.assertEqual(result["ignored_malformed_count"], 2)


if __name__ == "__main__":
    unittest.main()
