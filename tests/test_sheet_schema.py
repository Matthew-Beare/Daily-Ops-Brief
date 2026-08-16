#!/usr/bin/env python3
"""Tests for the machine-readable Google Sheets contract."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skill" / "scripts" / "reconcile_shipments.py"
SPEC = importlib.util.spec_from_file_location("reconcile_shipments_schema", MODULE_PATH)
assert SPEC and SPEC.loader
reconciler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reconciler)


class SheetSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "google-sheets.json").read_text(encoding="utf-8"))
        cls.migration = json.loads(
            (ROOT / "schemas" / "migrations" / "001_add_active_shipments.json").read_text(encoding="utf-8")
        )

    def test_tabs_have_unique_headers_and_primary_keys(self):
        for spreadsheet in self.schema["spreadsheets"].values():
            for name, tab in spreadsheet["tabs"].items():
                with self.subTest(tab=name):
                    self.assertEqual(len(tab["headers"]), len(set(tab["headers"])))
                    self.assertIn(tab["primary_key"], tab["headers"])

    def test_shipments_contract_matches_reconciler(self):
        shipments = self.schema["spreadsheets"]["ops_status_register"]["tabs"]["Shipments"]
        self.assertEqual(shipments["headers"], reconciler.HEADERS)
        self.assertEqual(set(shipments["validation"]["Status"]), reconciler.ACTIVE_STATUSES)
        self.assertNotIn("Delivered", shipments["validation"]["Status"])
        self.assertEqual(shipments["history"], "active_only_delete_delivered")

    def test_shipment_migration_matches_schema(self):
        shipments = self.schema["spreadsheets"]["ops_status_register"]["tabs"]["Shipments"]
        header_operation = next(item for item in self.migration["operations"] if item["type"] == "set_headers")
        validation_operation = next(item for item in self.migration["operations"] if item["type"] == "set_validation")
        self.assertEqual(header_operation["values"], shipments["headers"])
        self.assertEqual(set(validation_operation["allowed_values"]), set(shipments["validation"]["Status"]))
        self.assertEqual(self.migration["schema_version"], self.schema["schema_version"])


if __name__ == "__main__":
    unittest.main()
