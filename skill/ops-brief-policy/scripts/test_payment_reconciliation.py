from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("payment_reconciliation", ROOT / "payment_reconciliation.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PaymentReconciliationTests(unittest.TestCase):
    def test_missing_charge_stays_open(self) -> None:
        row = MODULE.reconcile_case({
            "payment_case_id": "PAY-1",
            "receipt_id": "R-1",
            "expected_amount": "1479.93",
            "observations": [],
        })
        self.assertEqual("Awaiting Settlement", row["status"])
        self.assertFalse(row["action_required"])

    def test_exact_posted_charge_matches(self) -> None:
        row = MODULE.reconcile_case({
            "payment_case_id": "PAY-2",
            "receipt_id": "R-2",
            "expected_amount": "660.86",
            "observations": [{"amount": "660.86", "pending": False}],
        })
        self.assertEqual("Matched", row["status"])
        self.assertEqual("$0.00", row["difference"])

    def test_split_charge_matches(self) -> None:
        row = MODULE.reconcile_case({
            "payment_case_id": "PAY-3",
            "receipt_id": "R-3",
            "expected_amount": "100.00",
            "observations": [
                {"amount": "60.00", "pending": False},
                {"amount": "40.00", "pending": False},
            ],
        })
        self.assertEqual("Split Settlement", row["status"])

    def test_pending_exact_amount_is_not_final(self) -> None:
        row = MODULE.reconcile_case({
            "payment_case_id": "PAY-4",
            "receipt_id": "R-4",
            "expected_amount": "1692.22",
            "observations": [{"amount": "1692.22", "pending": True}],
        })
        self.assertEqual("Pending Match", row["status"])
        self.assertFalse(row["action_required"])

    def test_overcharge_is_actionable(self) -> None:
        row = MODULE.reconcile_case({
            "payment_case_id": "PAY-5",
            "receipt_id": "R-5",
            "expected_amount": "100.00",
            "observations": [{"amount": "125.00", "pending": False}],
        })
        self.assertEqual("Overcharged", row["status"])
        self.assertTrue(row["action_required"])
        self.assertEqual("$25.00", row["difference"])

    def test_same_order_removed_before_settlement_resolves_without_refund(self) -> None:
        row = MODULE.reconcile_case({
            "payment_case_id": "PAY-6",
            "receipt_id": "R-6",
            "expected_amount": "1540.03",
            "merchant_resolution": "revised_before_settlement",
            "observations": [],
        })
        self.assertEqual("Resolved No Settlement", row["status"])
        self.assertFalse(row["action_required"])


if __name__ == "__main__":
    unittest.main()
