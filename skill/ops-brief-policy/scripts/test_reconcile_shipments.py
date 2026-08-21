#!/usr/bin/env python3
"""Tests for deterministic shipment reconciliation."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("reconcile_shipments.py")
SPEC = importlib.util.spec_from_file_location("reconcile_shipments", MODULE_PATH)
assert SPEC and SPEC.loader
reconciler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reconciler)


def row(
    shipment_id: str = "SHIP-001",
    vendor: str = "Example Vendor",
    order: str = "ORDER-1",
    item: str = "Example part",
    tracking: str = "TRACK-1",
    status: str = "Shipped",
) -> dict[str, str]:
    return {
        "Shipment ID": shipment_id,
        "Vendor": vendor,
        "Order Number": order,
        "Item": item,
        "Carrier": "FedEx",
        "Tracking Number": tracking,
        "Package Count": "1",
        "Order Date": "8/1/2026",
        "Shipped Date": "8/2/2026",
        "ETA (ET)": "8/5/2026",
        "Status": status,
        "Last Progress (ET)": "8/3/2026 9:00 AM ET",
        "Notes": "",
        "Updated (ET)": "8/3/2026 9:05 AM ET",
    }


def payload(rows: list[dict[str, str]], evidence: list[dict[str, object]]) -> dict[str, object]:
    return {
        "now": "2026-08-16T05:00:00-04:00",
        "shipments": rows,
        "evidence": evidence,
    }


class ReconcileShipmentTests(unittest.TestCase):
    def test_exact_tracking_delivery_deletes_active_row(self):
        result = reconciler.reconcile(
            payload(
                [row()],
                [
                    {
                        "source": "FedEx",
                        "event": "delivered",
                        "tracking_number": "TRACK-1",
                        "event_at": "2026-08-15T14:04:00-04:00",
                    }
                ],
            )
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["delete_ids"], ["SHIP-001"])
        self.assertEqual(result["active_rows"], [])

    def test_explicit_user_delivery_beats_newer_vendor_shipped_status(self):
        result = reconciler.reconcile(
            payload(
                [row(tracking="")],
                [
                    {
                        "source": "user",
                        "event": "delivered",
                        "vendor": "Example Vendor",
                        "order_number": "ORDER-1",
                        "observed_at": "2026-08-15T08:00:00-04:00",
                    },
                    {
                        "source": "vendor",
                        "event": "shipped",
                        "vendor": "Example Vendor",
                        "order_number": "ORDER-1",
                        "observed_at": "2026-08-16T08:00:00-04:00",
                    },
                ],
            )
        )
        self.assertEqual(result["delete_ids"], ["SHIP-001"])
        self.assertEqual(result["active_rows"], [])

    def test_carrier_delivery_beats_later_vendor_status(self):
        result = reconciler.reconcile(
            payload(
                [row()],
                [
                    {
                        "source": "carrier",
                        "event": "delivered",
                        "tracking_number": "TRACK-1",
                        "observed_at": "2026-08-15T12:00:00-04:00",
                    },
                    {
                        "source": "vendor",
                        "event": "shipped",
                        "vendor": "Example Vendor",
                        "order_number": "ORDER-1",
                        "observed_at": "2026-08-16T12:00:00-04:00",
                    },
                ],
            )
        )
        self.assertEqual(result["delete_ids"], ["SHIP-001"])
        self.assertEqual(result["active_rows"], [])

    def test_split_tracking_numbers_create_one_active_row_each(self):
        result = reconciler.reconcile(
            payload(
                [],
                [
                    {
                        "source": "vendor",
                        "event": "shipped",
                        "vendor": "Split Vendor",
                        "order_number": "SPLIT-9",
                        "item": "Wheel set",
                        "carrier": "UPS",
                        "tracking_numbers": ["1Z-A", "1Z-B"],
                        "shipped_date": "8/14/2026",
                    }
                ],
            )
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual([item["shipment_id"] for item in result["active_rows"]], ["SHIP-001", "SHIP-002"])
        self.assertEqual(
            [item["tracking_number"] for item in result["active_rows"]],
            ["1Z-A", "1Z-B"],
        )
        self.assertTrue(all(item["package_count"] == "1" for item in result["active_rows"]))

    def test_ambiguous_order_without_tracking_changes_nothing(self):
        rows = [
            row(shipment_id="SHIP-001", tracking="TRACK-A"),
            row(shipment_id="SHIP-002", tracking="TRACK-B"),
        ]
        result = reconciler.reconcile(
            payload(
                rows,
                [
                    {
                        "source": "vendor",
                        "event": "delayed",
                        "vendor": "Example Vendor",
                        "order_number": "ORDER-1",
                    }
                ],
            )
        )
        self.assertEqual(len(result["active_rows"]), 2)
        self.assertEqual(result["upserts"], [])
        self.assertEqual(result["unresolved"][0]["reason"], "Ambiguous match; no active row was changed.")

    def test_exact_tracking_updates_eta_and_progress(self):
        result = reconciler.reconcile(
            payload(
                [row()],
                [
                    {
                        "source": "carrier",
                        "event": "in_transit",
                        "tracking_number": "TRACK-1",
                        "eta": "8/17/2026, 9:50 AM–1:50 PM ET",
                        "event_at": "8/16/2026 12:46 AM ET",
                        "notes": "Scheduled for delivery tomorrow.",
                    }
                ],
            )
        )
        active = result["active_rows"][0]
        self.assertEqual(active["eta_et"], "8/17/2026, 9:50 AM–1:50 PM ET")
        self.assertEqual(active["last_progress_et"], "8/16/2026 12:46 AM ET")
        self.assertEqual(active["status"], "Shipped")
        self.assertEqual([item["shipment_id"] for item in result["upserts"]], ["SHIP-001"])

    def test_delivery_without_active_row_does_not_create_history(self):
        result = reconciler.reconcile(
            payload(
                [],
                [
                    {
                        "source": "carrier",
                        "event": "delivered",
                        "tracking_number": "OLD-TRACKING",
                    }
                ],
            )
        )
        self.assertEqual(result["active_rows"], [])
        self.assertEqual(result["delete_ids"], [])
        self.assertEqual(result["ignored"][0]["reason"], "Delivered with no active row.")

    def test_raw_sheet_schema_round_trips_in_canonical_order(self):
        values = [reconciler.HEADERS, list(row().values())]
        result = reconciler.reconcile(
            {
                "now": "2026-08-16T05:00:00-04:00",
                "shipments_values": values,
                "evidence": [],
            }
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["active_values"][0], reconciler.HEADERS)
        self.assertEqual(result["active_values"][1][0], "SHIP-001")

    def test_delivered_is_not_a_valid_active_sheet_status(self):
        result = reconciler.reconcile(payload([row(status="Delivered")], []))
        self.assertEqual(result["status"], "error")
        self.assertIn("invalid active status Delivered", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
