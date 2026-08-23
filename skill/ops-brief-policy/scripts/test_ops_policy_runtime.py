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
        "routes_values": [["Route ID", "Endpoint A", "Endpoint B", "Route A → B", "Route B → A", "Avg A → B (hrs)", "Avg B → A (hrs)", "Operation Profile", "Status"]],
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
                "2026-08-28T12:00:00-04:00",
                "",
                "Active",
            ]
        )
        result = runtime.resolve(payload)
        self.assertEqual(result["mode"], "HOME")
        self.assertEqual(result["mode_source"], "override")

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
        details = [item.get("detail") for item in result["actions_required"]]
        self.assertIn("Action Required — mileage/pay Sheet unavailable", details)


if __name__ == "__main__":
    unittest.main()
