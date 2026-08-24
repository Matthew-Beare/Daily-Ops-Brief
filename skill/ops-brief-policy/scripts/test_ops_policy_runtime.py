#!/usr/bin/env python3

import unittest

import ops_policy_runtime as runtime


def base_payload(now: str) -> dict:
    return {
        "strict_inputs": True,
        "brief_slot": "PM" if "T14:" in now else "AM",
        "now": now,
        "tasks_values": [["Task ID", "Tier", "Classification", "Subsystem", "Task", "Status", "Visibility"]],
        "control_values": [["Record ID", "Type", "Item", "State", "Starts At (ET)", "Expires At (ET)", "Notes", "Status"]],
        "routes_values": [["Route ID", "Endpoint A", "Endpoint B", "Route A → B", "Route B → A", "Avg A → B (hrs)", "Avg B → A (hrs)", "Paid Miles A → B", "Paid Miles B → A", "Miles Source A → B", "Miles Source B → A", "Operation Profile", "Status"]],
        "trips_values": [["Trip ID", "Route ID", "Origin", "Destination", "Departure (ET)", "ETA (ET)", "ETA Source", "Current Location", "Location Time (ET)", "Weather Watch", "Watch Expires (ET)", "Status", "Route Override"]],
        "travel_settings_values": [
            ["Setting ID", "Setting", "Value", "Notes", "Status"],
            ["TRAVEL-014", "Thursday mileage summary", "Enabled", "", "Active"],
        ],
        "mileage_values": [["Entry ID", "Week Ending (Thu)", "Trip ID", "Route ID", "Departure (ET)", "Arrival (ET)", "Origin", "Destination", "Company-Paid Miles", "Rate / Mile", "Gross Pay Estimate", "Miles Source", "Status", "Notes", "Updated (ET)"]],
        "mileage_settings_values": [
            ["Setting", "Value"],
            ["Rate per paid mile", 0.986],
        ],
        "appointments": [],
    }


def add_active_trip(payload: dict) -> None:
    payload["trips_values"].append(
        [
            "TRIP-001",
            "",
            "Morristown, TN",
            "Rialto, CA",
            "2026-08-21T16:30:00-04:00",
            "",
            "Unknown",
            "Tucumcari, NM",
            "2026-08-22T15:20:00-04:00",
            "Off",
            "",
            "Active",
            "I-40 west",
        ]
    )


class RuntimePolicyRegressionTests(unittest.TestCase):
    def test_active_trip_survives_weekly_home_boundary(self):
        payload = base_payload("2026-08-26T16:31:00-04:00")
        add_active_trip(payload)
        result = runtime.resolve(payload)
        self.assertEqual(result["mode"], "ROAD")
        self.assertEqual(result["mode_source"], "active_trip")
        self.assertNotEqual(result["status"], "error")

    def test_live_home_override_beats_active_trip(self):
        payload = base_payload("2026-08-26T16:31:00-04:00")
        add_active_trip(payload)
        payload["control_values"].append(
            [
                "CTRL-HOME",
                "Mode Override",
                "Home early",
                "HOME",
                "2026-08-26T16:00:00-04:00",
                "2026-08-28T15:00:00-04:00",
                "",
                "Active",
            ]
        )
        result = runtime.resolve(payload)
        self.assertEqual(result["mode"], "HOME")
        self.assertEqual(result["mode_source"], "override")

    def test_home_early_covers_friday_pm_brief(self):
        result = runtime.home_early(runtime.base.parse_datetime("2026-08-26T16:00:00-04:00"))
        self.assertEqual(result["expires_at"], "2026-08-28T15:00:00-04:00")
        self.assertEqual(result["work_cycle_close_at"], "2026-08-26T16:00:00-04:00")
        self.assertEqual(result["sheet_fields"]["State"], "HOME")

    def test_home_early_after_friday_boundary_targets_next_week(self):
        result = runtime.home_early(runtime.base.parse_datetime("2026-08-28T15:01:00-04:00"))
        self.assertEqual(result["expires_at"], "2026-09-04T15:00:00-04:00")

    def test_directional_route_miles_are_distinct_fields(self):
        self.assertEqual(runtime.base.ROUTE_KEYS["paidmilesab"], "paid_miles_ab")
        self.assertEqual(runtime.base.ROUTE_KEYS["paidmilesba"], "paid_miles_ba")
        self.assertNotEqual(
            runtime.base.ROUTE_KEYS["paidmilesab"], runtime.base.ROUTE_KEYS["paidmilesba"]
        )

    def test_saturday_bad_mileage_range_does_not_abort(self):
        payload = base_payload("2026-08-22T14:45:00-04:00")
        add_active_trip(payload)
        payload["mileage_values"] = {"bad": "shape"}
        result = runtime.resolve(payload)
        self.assertEqual(result["mode"], "ROAD")
        self.assertNotEqual(result["status"], "error")
        self.assertFalse(
            any("mileage_values is not a readable sheet range" in error for error in result.get("errors", []))
        )

    def test_thursday_home_still_gets_mileage_summary(self):
        payload = base_payload("2026-08-27T14:45:00-04:00")
        payload["mileage_values"].append(
            [
                "MILE-001",
                "2026-08-27",
                "TRIP-001",
                "ROUTE-002",
                "2026-08-21T16:30:00-04:00",
                "",
                "Morristown, TN",
                "Rialto, CA",
                2184,
                0.986,
                "",
                "User",
                "Estimated",
                "",
                "2026-08-22T15:43:44-04:00",
            ]
        )
        result = runtime.resolve(payload)
        self.assertEqual(result["mode"], "HOME")
        self.assertTrue(result["mileage_summary_due"])
        self.assertEqual(result["mileage_summary"]["total_paid_miles"], "2,184")
        self.assertEqual(result["mileage_summary"]["gross_pay_estimate"], "2153.42")

    def test_thursday_bad_mileage_is_degraded_not_error(self):
        payload = base_payload("2026-08-27T14:45:00-04:00")
        payload["mileage_values"] = None
        result = runtime.resolve(payload)
        self.assertEqual(result["mode"], "HOME")
        self.assertEqual(result["status"], "degraded")
        self.assertEqual(result["run_log_fields"]["Status"], "Degraded")
        messages = [item.get("message") for item in result["actions_required"]]
        self.assertIn("Action Required — mileage/pay Sheet unavailable", messages)

    def test_denver_summer_instant_matches_new_york_pm_slot(self):
        moment = runtime.base.parse_datetime("2026-08-23T12:45:00-06:00", "now")
        evidence = runtime.canonical_slot_evidence(moment)
        self.assertEqual(evidence["timezone"], "America/New_York")
        self.assertEqual(evidence["canonical_clock"], "14:45")
        self.assertTrue(evidence["slot_match"])

    def test_denver_summer_1240_does_not_match_new_york_slot(self):
        moment = runtime.base.parse_datetime("2026-08-23T12:40:00-06:00", "now")
        evidence = runtime.canonical_slot_evidence(moment)
        self.assertEqual(evidence["canonical_clock"], "14:40")
        self.assertFalse(evidence["slot_match"])

    def test_denver_winter_uses_iana_dst_rules_not_summer_offset(self):
        moment = runtime.base.parse_datetime("2026-12-15T12:45:00-07:00", "now")
        evidence = runtime.canonical_slot_evidence(moment)
        self.assertEqual(evidence["canonical_clock"], "14:45")
        self.assertTrue(evidence["canonical_now"].endswith("-05:00"))
        self.assertTrue(evidence["slot_match"])

    def test_same_instant_matches_regardless_of_input_offset(self):
        denver = runtime.base.parse_datetime("2026-08-23T12:45:00-06:00", "now")
        utc = runtime.base.parse_datetime("2026-08-23T18:45:00+00:00", "now")
        self.assertEqual(
            runtime.canonical_slot_evidence(denver)["canonical_now"],
            runtime.canonical_slot_evidence(utc)["canonical_now"],
        )

    def test_resolve_exposes_canonical_clock_evidence(self):
        payload = base_payload("2026-08-23T12:45:00-06:00")
        result = runtime.resolve(payload)
        self.assertEqual(result["canonical_clock_evidence"]["canonical_clock"], "14:45")
        self.assertTrue(result["canonical_clock_evidence"]["slot_match"])
        self.assertEqual(result["run_log_fields"]["Canonical Clock (ET)"], "14:45")
        self.assertTrue(result["run_log_fields"]["Canonical Slot Match"])

    def test_naive_current_instant_is_rejected_for_canonical_clock(self):
        with self.assertRaisesRegex(ValueError, "explicit timezone"):
            runtime.canonical_clock(runtime.datetime(2026, 8, 23, 14, 45))


if __name__ == "__main__":
    unittest.main()
