#!/usr/bin/env python3

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import financial_resolution as policy


TZ = ZoneInfo("America/New_York")


class FinancialResolutionTests(unittest.TestCase):
    def test_revised_before_settlement_needs_no_refund(self):
        case = {
            "receipt_id": "TR-1",
            "financial_resolution_status": "revised_before_settlement",
        }
        result = policy.resolve_case(case, datetime(2026, 8, 31, 12, tzinfo=TZ))
        self.assertEqual(result["status"], "resolved")
        self.assertFalse(result["action_required"])

    def test_five_business_days_preserve_clock_time(self):
        start = datetime(2026, 8, 21, 14, 15, tzinfo=TZ)  # Friday
        self.assertEqual(
            policy.add_business_days(start, 5),
            datetime(2026, 8, 28, 14, 15, tzinfo=TZ),
        )

    def test_pending_refund_not_actionable_before_deadline(self):
        case = {
            "receipt_id": "TR-2",
            "vendor": "Tire Rack",
            "order_number": "VG00001",
            "financial_resolution_status": "refund_expected",
            "cancellation_confirmed_at": "2026-08-21T14:15:00-04:00",
            "expected_amount": "1540.03",
        }
        result = policy.resolve_case(case, datetime(2026, 8, 28, 14, 14, tzinfo=TZ))
        self.assertEqual(result["status"], "pending")
        self.assertFalse(result["action_required"])

    def test_pending_refund_actionable_at_deadline(self):
        case = {
            "receipt_id": "TR-2",
            "vendor": "Tire Rack",
            "order_number": "VG00001",
            "financial_resolution_status": "refund_expected",
            "cancellation_confirmed_at": "2026-08-21T14:15:00-04:00",
            "expected_amount": "1540.03",
            "missing_evidence": "posted refund/reversal",
        }
        result = policy.resolve_case(case, datetime(2026, 8, 28, 14, 15, tzinfo=TZ))
        self.assertEqual(result["status"], "overdue")
        self.assertTrue(result["action_required"])
        self.assertIn("$1,540.03", result["detail"])
        self.assertIn("posted refund/reversal", result["detail"])

    def test_verified_credit_clears_action(self):
        case = {
            "receipt_id": "TR-3",
            "financial_resolution_status": "verified",
            "cancellation_confirmed_at": "2026-08-01T10:00:00-04:00",
        }
        result = policy.resolve_case(case, datetime(2026, 8, 31, 12, tzinfo=TZ))
        self.assertFalse(result["action_required"])

    def test_non_object_case_fails_closed(self):
        with self.assertRaisesRegex(ValueError, r"cases\[1\]"):
            policy.resolve({
                "now": "2026-08-31T12:00:00-04:00",
                "cases": ["not-a-case"],
            })

    def test_non_finite_expected_amount_is_not_rendered_as_money(self):
        self.assertIsNone(policy.money("NaN"))
        self.assertIsNone(policy.money("Infinity"))


if __name__ == "__main__":
    unittest.main()
