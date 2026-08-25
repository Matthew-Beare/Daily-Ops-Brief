from __future__ import annotations

import unittest
from datetime import datetime, timezone

import manual_brief_smoke


class ManualBriefSmokeTests(unittest.TestCase):
    def test_off_slot_manual_run_uses_real_policy_without_claiming_scheduler_firing(self) -> None:
        diagnostic_now = datetime(2026, 8, 25, 16, 12, 34, tzinfo=timezone.utc)
        output = manual_brief_smoke.run_manual_smoke(
            {"strict_inputs": False},
            slot="PM",
            diagnostic_now=diagnostic_now,
        )

        self.assertIn(output["status"], {"ok", "degraded"})
        self.assertEqual("manual_smoke", output["invocation_mode"])
        self.assertTrue(output["run_id"].startswith("OPS-MANUAL-20260825-121234-"))
        self.assertTrue(output["run_id"].endswith("-PM"))
        self.assertFalse(output["manual_smoke"]["scheduled_firing_evidence"])
        self.assertTrue(output["manual_smoke"]["slot_gate_bypassed"])
        self.assertEqual("explicit_diagnostic_input", output["manual_smoke"]["clock_source"])

        evidence = output["canonical_clock_evidence"]
        self.assertFalse(evidence["slot_match"])
        self.assertTrue(evidence["manual_slot_bypass"])
        self.assertFalse(evidence["scheduled_firing_evidence"])

        fields = output["run_log_fields"]
        self.assertEqual(output["run_id"], fields["Run ID"])
        self.assertEqual("manual_smoke_policy_resolved", fields["Phase"])
        self.assertEqual("manual_smoke", fields["Dispatch State"])
        self.assertEqual("MANUAL-PM", fields["Logical Slot"])
        self.assertEqual("", fields["Effective Scheduled Instant"])
        self.assertIn("not evidence of a scheduled 02:45/14:45 firing", fields["Error / Notes"])

    def test_live_manual_run_captures_runtime_clock(self) -> None:
        output = manual_brief_smoke.run_manual_smoke(
            {"strict_inputs": False},
            slot="AM",
        )
        self.assertIn(output["status"], {"ok", "degraded"})
        self.assertEqual("runtime_system_clock_manual", output["manual_smoke"]["clock_source"])
        self.assertEqual(
            "runtime_system_clock_manual",
            output["canonical_clock_evidence"]["clock_source"],
        )
        self.assertFalse(output["canonical_clock_evidence"]["scheduled_firing_evidence"])

    def test_slot_is_explicit(self) -> None:
        with self.assertRaisesRegex(ValueError, "AM or PM"):
            manual_brief_smoke.run_manual_smoke(
                {"strict_inputs": False},
                slot="NOON",
                diagnostic_now=datetime(2026, 8, 25, 16, 12, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
