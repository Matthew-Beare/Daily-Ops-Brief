#!/usr/bin/env python3

import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skill" / "scripts"))
import ops_policy as policy


def dt(value: str) -> datetime:
    result = policy.parse_datetime(value)
    assert result is not None
    return result


def task(
    task_id: str,
    tier: str = "High",
    classification: str = "Home",
    label: str = "Do thing",
    status: str = "Active",
    visibility: str = "Home",
    subsystem: str = "",
    active_from: str = "",
    active_through: str = "",
    row: int = 2,
) -> dict:
    return {
        "task_id": task_id,
        "tier": tier,
        "classification": classification,
        "subsystem": subsystem,
        "task": label,
        "status": status,
        "visibility": visibility,
        "active_from": active_from,
        "active_through": active_through,
        "_row": row,
    }


def override(
    record_id: str,
    state: str,
    start: str,
    expiry: str,
    row: int = 2,
) -> dict:
    return {
        "record_id": record_id,
        "type": "Mode Override",
        "item": "Test",
        "state": state,
        "starts_at": start,
        "expires_at": expiry,
        "status": "Active",
        "_row": row,
    }


def route(row: int = 2) -> dict:
    return {
        "route_id": "ROUTE-001",
        "endpoint_a": "El Paso, TX",
        "endpoint_b": "Parsons, KS",
        "route_ab": "US-54 → I-40 → Oklahoma City → I-44 → US-169 → US-400",
        "route_ba": "",
        "avg_ab_hours": 17,
        "avg_ba_hours": "",
        "operation_profile": "Default team truck",
        "status": "Active",
        "_row": row,
    }


def trip(**changes) -> dict:
    result = {
        "trip_id": "TRIP-001",
        "route_id": "ROUTE-001",
        "origin": "El Paso, TX",
        "destination": "Parsons, KS",
        "departure_et": "2026-08-16T05:00:00-04:00",
        "eta_et": "",
        "eta_source": "",
        "current_location": "Tucumcari, NM",
        "location_time_et": "2026-08-16T09:30:00-04:00",
        "weather_watch": "Active",
        "watch_expires_et": "",
        "status": "Active",
        "route_override": "",
        "_row": 2,
    }
    result.update(changes)
    return result


def mileage_entry(**changes) -> dict:
    result = {
        "entry_id": "MILE-001",
        "week_ending": "2026-08-13",
        "trip_id": "TRIP-001",
        "route_id": "ROUTE-001",
        "departure_et": "2026-08-07T16:30:00-04:00",
        "arrival_et": "2026-08-10T08:00:00-04:00",
        "origin": "Morristown, TN",
        "destination": "Rialto, CA",
        "company_paid_miles": "1500",
        "rate_per_mile": "0.986",
        "gross_pay_estimate": "1479.00",
        "miles_source": "Settlement",
        "status": "Final",
        "notes": "",
        "updated_et": "2026-08-13T12:00:00-04:00",
        "_row": 5,
    }
    result.update(changes)
    return result


def mileage_feature_settings() -> list[dict]:
    return [
        {
            "setting_id": "TRAVEL-014",
            "setting": "Thursday mileage summary",
            "value": "Enabled",
            "status": "Active",
        }
    ]


def mileage_rate_settings(rate: str = "0.986") -> list[dict]:
    return [{"setting": "Rate per paid mile", "value": rate, "_row": 4}]


class NormalModeTests(unittest.TestCase):
    def test_weekly_boundaries(self):
        self.assertEqual(policy.normal_mode(dt("2026-08-12T16:29:59-04:00")), "ROAD")
        self.assertEqual(policy.normal_mode(dt("2026-08-12T16:30:00-04:00")), "HOME")
        self.assertEqual(policy.normal_mode(dt("2026-08-13T12:00:00-04:00")), "HOME")
        self.assertEqual(policy.normal_mode(dt("2026-08-14T11:59:59-04:00")), "HOME")
        self.assertEqual(policy.normal_mode(dt("2026-08-14T12:00:00-04:00")), "ROAD")

    def test_dst_keeps_wall_clock_boundaries(self):
        spring = dt("2026-03-11T16:30:00-04:00")
        fall = dt("2026-11-04T16:30:00-05:00")
        self.assertEqual(policy.normal_mode(spring), "HOME")
        self.assertEqual(policy.normal_mode(fall), "HOME")

    def test_google_sheet_serial_datetime_uses_eastern_wall_time(self):
        self.assertEqual(
            policy.parse_datetime(46249.24513888889).isoformat(),
            "2026-08-15T05:53:00-04:00",
        )


class OverrideTests(unittest.TestCase):
    def test_override_is_start_inclusive_expiry_exclusive(self):
        rows, errors = policy.prepare_overrides(
            [override("CTRL-1", "HOME", "2026-08-10T00:00:00-04:00", "2026-08-14T12:00:00-04:00")]
        )
        self.assertEqual(errors, [])
        self.assertEqual(policy.resolve_mode_at(dt("2026-08-10T00:00:00-04:00"), rows)[0], "HOME")
        self.assertEqual(policy.resolve_mode_at(dt("2026-08-14T11:59:59-04:00"), rows)[0], "HOME")
        self.assertEqual(policy.resolve_mode_at(dt("2026-08-14T12:00:00-04:00"), rows)[0], "ROAD")

    def test_latest_start_wins(self):
        rows, _ = policy.prepare_overrides(
            [
                override("CTRL-1", "ROAD", "2026-08-10T00:00:00-04:00", "2026-08-20T00:00:00-04:00", 2),
                override("CTRL-2", "HOME", "2026-08-11T00:00:00-04:00", "2026-08-20T00:00:00-04:00", 3),
            ]
        )
        mode, source, selected, error = policy.resolve_mode_at(dt("2026-08-12T12:00:00-04:00"), rows)
        self.assertEqual((mode, source, error), ("HOME", "override", None))
        self.assertEqual(selected["record_id"], "CTRL-2")

    def test_equal_start_conflict_fails(self):
        rows, _ = policy.prepare_overrides(
            [
                override("CTRL-1", "ROAD", "2026-08-10T00:00:00-04:00", "2026-08-20T00:00:00-04:00", 2),
                override("CTRL-2", "HOME", "2026-08-10T00:00:00-04:00", "2026-08-20T00:00:00-04:00", 3),
            ]
        )
        mode, source, _, error = policy.resolve_mode_at(dt("2026-08-12T12:00:00-04:00"), rows)
        self.assertIsNone(mode)
        self.assertEqual(source, "conflict")
        self.assertIn("CTRL-1", error)

    def test_invalid_expiry_is_rejected(self):
        _, errors = policy.prepare_overrides(
            [override("CTRL-1", "HOME", "2026-08-14T12:00:00-04:00", "2026-08-14T12:00:00-04:00")]
        )
        self.assertEqual(errors, ["CTRL-1 expires at or before it starts."])

    def test_home_early_uses_next_strictly_future_friday(self):
        same_week = policy.home_early(dt("2026-08-12T10:00:00-04:00"))
        next_week = policy.home_early(dt("2026-08-14T12:00:00-04:00"))
        self.assertEqual(same_week["expires_at"], "2026-08-14T12:00:00-04:00")
        self.assertEqual(next_week["expires_at"], "2026-08-21T12:00:00-04:00")


class AppointmentTests(unittest.TestCase):
    def test_home_mode_uses_next_calendar_day(self):
        window, errors = policy.appointment_window(dt("2026-08-13T14:45:00-04:00"), "HOME", [])
        self.assertEqual(errors, [])
        self.assertEqual(window["kind"], "home_day_before")
        self.assertEqual(window["start"], "2026-08-14T00:00:00-04:00")
        self.assertEqual(window["end"], "2026-08-15T00:00:00-04:00")

    def test_normal_transition_friday_previews_until_wednesday_home(self):
        window, errors = policy.appointment_window(dt("2026-08-14T02:45:00-04:00"), "HOME", [])
        self.assertEqual(errors, [])
        self.assertEqual(window["kind"], "friday_road_preview")
        self.assertEqual(window["start"], "2026-08-14T12:00:00-04:00")
        self.assertEqual(window["end"], "2026-08-19T16:30:00-04:00")

    def test_vacation_covering_friday_suppresses_preview(self):
        rows, _ = policy.prepare_overrides(
            [override("CTRL-1", "HOME", "2026-08-12T00:00:00-04:00", "2026-08-21T12:00:00-04:00")]
        )
        window, errors = policy.appointment_window(dt("2026-08-14T02:45:00-04:00"), "HOME", rows)
        self.assertEqual(errors, [])
        self.assertEqual(window["kind"], "home_day_before")

    def test_delayed_friday_transition_uses_override_expiry(self):
        rows, _ = policy.prepare_overrides(
            [override("CTRL-1", "HOME", "2026-08-12T00:00:00-04:00", "2026-08-14T15:00:00-04:00")]
        )
        window, _ = policy.appointment_window(dt("2026-08-14T02:45:00-04:00"), "HOME", rows)
        self.assertEqual(window["start"], "2026-08-14T15:00:00-04:00")

    def test_filter_appointments_uses_half_open_window(self):
        window = {
            "start": "2026-08-17T00:00:00-04:00",
            "end": "2026-08-18T00:00:00-04:00",
        }
        appointments = [
            {"id": "a", "title": "Inside", "start": "2026-08-17T14:00:00-04:00"},
            {"id": "b", "title": "At end", "start": "2026-08-18T00:00:00-04:00"},
        ]
        due, errors = policy.filter_appointments(appointments, window)
        self.assertEqual(errors, [])
        self.assertEqual([item["id"] for item in due], ["a"])


class TaskTests(unittest.TestCase):
    def test_mode_visibility_and_persistent(self):
        rows = [
            task("T1", tier="Persistent", classification="Personal", visibility="", label="Always", row=2),
            task("T2", visibility="Home", label="Home only", row=3),
            task("T3", visibility="Road", label="Road only", row=4),
            task("T4", visibility="Both", label="Both", row=5),
        ]
        home, _, markdown, errors = policy.task_output(rows, dt("2026-08-13T14:45:00-04:00"), "HOME", "PM")
        self.assertEqual(errors, [])
        self.assertEqual([row["task_id"] for row in home], ["T1", "T2", "T4"])
        self.assertIn("- Persistent", markdown)
        road, _, _, _ = policy.task_output(rows, dt("2026-08-10T14:45:00-04:00"), "ROAD", "PM")
        self.assertEqual([row["task_id"] for row in road], ["T1", "T3", "T4"])

    def test_scheduled_window_is_inclusive_and_done_is_hidden(self):
        rows = [
            task("T1", status="Scheduled", active_from="8/14/2026", active_through="8/14/2026"),
            task("T2", status="Done"),
        ]
        eligible, errors = policy.eligible_tasks(rows, dt("2026-08-14T12:00:00-04:00").date())
        self.assertEqual(errors, [])
        self.assertEqual([row["task_id"] for row in eligible], ["T1"])

    def test_saturday_am_next_home_selects_highest_tier(self):
        rows = [
            task("T1", tier="Medium", visibility="Home", label="Medium", row=2),
            task("T2", tier="High", visibility="Home", label="High one", row=3),
            task("T3", tier="High", visibility="Home", label="High two", row=4),
            task("T4", tier="Low", visibility="Both", label="Already visible", row=5),
        ]
        visible, next_home, markdown, errors = policy.task_output(rows, dt("2026-08-15T02:45:00-04:00"), "ROAD", "AM")
        self.assertEqual(errors, [])
        self.assertEqual([row["task_id"] for row in visible], ["T4"])
        self.assertEqual([row["task_id"] for row in next_home], ["T2", "T3"])
        self.assertIn("- Next Home", markdown)

    def test_duplicate_id_is_error(self):
        _, errors = policy.eligible_tasks([task("T1", row=2), task("T1", row=3)], dt("2026-08-14").date())
        self.assertEqual(errors, ["Duplicate Task ID T1."])


class RouteTests(unittest.TestCase):
    def test_route_matches_both_directions(self):
        routes, errors = policy.prepare_routes([route()])
        self.assertEqual(errors, [])
        direct, error = policy.find_route(
            routes, "El Paso, TX", "Parsons, KS"
        )
        self.assertIsNone(error)
        self.assertEqual(direct["direction"], "A_TO_B")
        self.assertEqual(direct["average_hours"], 17)
        reverse, error = policy.find_route(
            routes, "Parsons, KS", "El Paso, TX"
        )
        self.assertIsNone(error)
        self.assertEqual(reverse["direction"], "B_TO_A")
        self.assertEqual(reverse["average_hours"], 17)
        self.assertEqual(reverse["eta_source"], "Reverse Average Fallback")
        self.assertEqual(
            reverse["route_overview"],
            "US-400 → US-169 → I-44 → Oklahoma City → I-40 → US-54",
        )

    def test_user_eta_wins_over_route_average(self):
        result = policy.resolve(
            {
                "now": "2026-08-16T10:00:00-04:00",
                "brief_slot": "AM",
                "tasks": [],
                "controls": [],
                "routes": [route()],
                "trips": [
                    trip(
                        eta_et="2026-08-16T23:30:00-04:00",
                        eta_source="User",
                    )
                ],
                "travel_settings": [],
            }
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["trip_status"]["eta"], "2026-08-16T23:30:00-04:00")
        self.assertEqual(result["trip_status"]["eta_source"], "User")


class TravelPolicyTests(unittest.TestCase):
    def test_known_route_computes_eta_and_arms_watch_to_eta(self):
        result = policy.resolve(
            {
                "now": "2026-08-16T10:00:00-04:00",
                "brief_slot": "AM",
                "tasks": [],
                "controls": [],
                "routes": [route()],
                "trips": [trip()],
                "travel_settings": [],
            }
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "ROAD")
        self.assertEqual(result["trip_status"]["eta"], "2026-08-16T22:00:00-04:00")
        self.assertEqual(result["trip_status"]["eta_source"], "Route Average")
        self.assertTrue(result["route_weather_allowed"])
        self.assertEqual(
            result["route_weather_watches"][0]["watch_expires"],
            "2026-08-16T22:00:00-04:00",
        )
        self.assertEqual(
            result["route_weather_watches"][0]["watch_expiry_source"],
            "ETA",
        )

    def test_route_weather_is_road_only(self):
        result = policy.resolve(
            {
                "now": "2026-08-13T10:00:00-04:00",
                "brief_slot": "AM",
                "tasks": [],
                "controls": [],
                "routes": [route()],
                "trips": [trip(departure_et="2026-08-13T05:00:00-04:00")],
                "travel_settings": [],
            }
        )
        self.assertEqual(result["mode"], "HOME")
        self.assertFalse(result["route_weather_allowed"])
        self.assertEqual(result["route_weather_watches"], [])
        self.assertIsNone(result["trip_status"])
        self.assertEqual(result["actions_required"], [])

    def test_watch_expiry_is_exclusive_and_silently_deactivates(self):
        result = policy.resolve(
            {
                "now": "2026-08-16T22:00:00-04:00",
                "brief_slot": "PM",
                "tasks": [],
                "controls": [],
                "routes": [route()],
                "trips": [trip()],
                "travel_settings": [],
            }
        )
        self.assertFalse(result["route_weather_allowed"])
        self.assertEqual(result["expired_watch_trip_ids"], ["TRIP-001"])

    def test_corridor_watch_without_expiry_repeats_action(self):
        result = policy.resolve(
            {
                "now": "2026-08-16T10:00:00-04:00",
                "brief_slot": "AM",
                "tasks": [],
                "controls": [],
                "routes": [],
                "trips": [
                    trip(
                        route_id="",
                        origin="",
                        destination="",
                        departure_et="",
                        eta_et="",
                        current_location="",
                        location_time_et="",
                        route_override="I-80 across Wyoming",
                    )
                ],
                "travel_settings": [],
            }
        )
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["route_weather_allowed"])
        self.assertIn(
            "watch_expiry_required",
            [item["code"] for item in result["actions_required"]],
        )

    def test_inactive_feature_is_hidden(self):
        result = policy.resolve(
            {
                "now": "2026-08-17T14:45:00-04:00",
                "brief_slot": "PM",
                "tasks": [],
                "controls": [],
                "routes": [route()],
                "trips": [],
                "travel_settings": [],
            }
        )
        self.assertFalse(result["route_weather_allowed"])
        self.assertEqual(result["route_weather_watches"], [])
        self.assertIsNone(result["trip_status"])
        self.assertEqual(result["actions_required"], [])

    def test_friday_pm_prompts_for_terminal_destination(self):
        settings = [
            {
                "setting_id": "TRAVEL-009",
                "setting": "Friday PM destination confirmation",
                "value": "Enabled",
                "status": "Active",
            },
            {
                "setting_id": "TRAVEL-002",
                "setting": "Default terminal origin",
                "value": "Morristown, TN",
                "status": "Active",
            },
            {
                "setting_id": "TRAVEL-003",
                "setting": "Default Friday departure",
                "value": "Friday 16:30 ET",
                "status": "Active",
            },
            {
                "setting_id": "TRAVEL-004",
                "setting": "Common terminal destination",
                "value": "Rialto / Southern California",
                "status": "Active",
            },
        ]
        result = policy.resolve(
            {
                "now": "2026-08-14T14:45:00-04:00",
                "brief_slot": "PM",
                "tasks": [],
                "controls": [],
                "routes": [],
                "trips": [],
                "travel_settings": settings,
            }
        )
        actions = result["actions_required"]
        self.assertEqual(actions[0]["code"], "terminal_destination_confirmation")
        self.assertIn("Morristown", actions[0]["message"])
        self.assertIn("Rialto", actions[0]["message"])

    def test_friday_prompt_is_suppressed_by_planned_trip(self):
        settings = [
            {
                "setting_id": "TRAVEL-009",
                "setting": "Friday PM destination confirmation",
                "value": "Enabled",
                "status": "Active",
            }
        ]
        result = policy.resolve(
            {
                "now": "2026-08-14T14:45:00-04:00",
                "brief_slot": "PM",
                "tasks": [],
                "controls": [],
                "routes": [],
                "trips": [
                    trip(
                        route_id="",
                        origin="Morristown, TN",
                        destination="Rialto, CA",
                        departure_et="2026-08-14T16:30:00-04:00",
                        eta_et="2026-08-17T00:30:00-04:00",
                        current_location="",
                        location_time_et="",
                        weather_watch="Off",
                        status="Planned",
                        route_override="I-40 west",
                    )
                ],
                "travel_settings": settings,
            }
        )
        self.assertNotIn(
            "terminal_destination_confirmation",
            [item["code"] for item in result["actions_required"]],
        )

    def test_saturday_am_requests_fresh_location_for_active_trip(self):
        result = policy.resolve(
            {
                "now": "2026-08-15T02:45:00-04:00",
                "brief_slot": "AM",
                "tasks": [],
                "controls": [],
                "routes": [route()],
                "trips": [
                    trip(
                        departure_et="2026-08-14T16:30:00-04:00",
                        current_location="Knoxville, TN",
                        location_time_et="2026-08-14T22:00:00-04:00",
                    )
                ],
                "travel_settings": [],
            }
        )
        self.assertIn(
            "saturday_location_update_requested",
            [item["code"] for item in result["actions_required"]],
        )

    def test_mowing_season_boundaries(self):
        self.assertFalse(policy.mowing_season(dt("2026-03-31T23:59:59-04:00")))
        self.assertTrue(policy.mowing_season(dt("2026-04-01T00:00:00-04:00")))
        self.assertTrue(policy.mowing_season(dt("2026-10-31T23:59:59-04:00")))
        self.assertFalse(policy.mowing_season(dt("2026-11-01T00:00:00-04:00")))


class MileageTests(unittest.TestCase):
    def payload(self, **changes) -> dict:
        result = {
            "now": "2026-08-13T14:45:00-04:00",
            "brief_slot": "PM",
            "tasks": [],
            "controls": [],
            "routes": [],
            "trips": [],
            "travel_settings": mileage_feature_settings(),
            "mileage": [mileage_entry()],
            "mileage_settings": mileage_rate_settings(),
        }
        result.update(changes)
        return result

    def test_thursday_totals_company_paid_miles_and_gross(self):
        result = policy.resolve(self.payload())
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["mileage_summary_due"])
        self.assertEqual(result["mileage_summary"]["total_paid_miles"], "1,500")
        self.assertEqual(result["mileage_summary"]["gross_pay_estimate"], "1479.00")
        self.assertTrue(result["mileage_summary"]["data_complete"])
        self.assertIn("$1,479.00", result["mileage_summary_markdown"])

    def test_non_thursday_summary_is_hidden(self):
        result = policy.resolve(
            self.payload(now="2026-08-12T14:45:00-04:00")
        )
        self.assertFalse(result["mileage_summary_due"])
        self.assertIsNone(result["mileage_summary"])
        self.assertEqual(result["mileage_summary_markdown"], "")

    def test_pay_week_is_friday_inclusive_to_next_friday_exclusive(self):
        start, end, start_at, next_at = policy.pay_week(
            dt("2026-08-14T00:00:00-04:00")
        )
        self.assertEqual(start.isoformat(), "2026-08-14")
        self.assertEqual(end.isoformat(), "2026-08-20")
        self.assertEqual(start_at.isoformat(), "2026-08-14T00:00:00-04:00")
        self.assertEqual(next_at.isoformat(), "2026-08-21T00:00:00-04:00")

    def test_voided_entry_is_excluded_and_row_rate_is_preserved(self):
        result = policy.resolve(
            self.payload(
                mileage=[
                    mileage_entry(company_paid_miles="1000", rate_per_mile="0.986"),
                    mileage_entry(
                        entry_id="MILE-002",
                        trip_id="TRIP-002",
                        company_paid_miles="500",
                        rate_per_mile="0.950",
                    ),
                    mileage_entry(
                        entry_id="MILE-003",
                        trip_id="TRIP-003",
                        company_paid_miles="999",
                        status="Voided",
                    ),
                ]
            )
        )
        self.assertEqual(result["mileage_summary"]["total_paid_miles"], "1,500")
        self.assertEqual(result["mileage_summary"]["gross_pay_estimate"], "1461.00")

    def test_missing_tracker_inputs_fail_closed(self):
        payload = self.payload()
        payload.pop("mileage")
        payload.pop("mileage_settings")
        result = policy.resolve(payload)
        self.assertEqual(result["status"], "error")
        self.assertIn("Mileage tracker inputs are unavailable", result["errors"][0])

    def test_known_trip_without_mileage_creates_thursday_action(self):
        result = policy.resolve(
            self.payload(
                trips=[
                    trip(
                        departure_et="2026-08-08T16:30:00-04:00",
                        status="Arrived",
                    )
                ],
                mileage=[],
            )
        )
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["mileage_summary"]["data_complete"])
        self.assertIn(
            "trip_mileage_entry_required",
            [item["code"] for item in result["actions_required"]],
        )

    def test_empty_week_is_explicit_zero_and_complete(self):
        result = policy.resolve(self.payload(mileage=[]))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mileage_summary"]["total_paid_miles"], "0")
        self.assertEqual(result["mileage_summary"]["gross_pay_estimate"], "0.00")
        self.assertTrue(result["mileage_summary"]["data_complete"])

    def test_raw_values_skip_preformatted_blank_rows(self):
        result = policy.resolve(
            {
                "now": "2026-08-13T02:45:00-04:00",
                "brief_slot": "AM",
                "tasks": [],
                "controls": [],
                "routes": [],
                "trips": [],
                "travel_settings": mileage_feature_settings(),
                "mileage_values": [
                    [
                        "Entry ID", "Week Ending (Thu)", "Trip ID", "Route ID",
                        "Departure (ET)", "Arrival (ET)", "Origin", "Destination",
                        "Company-Paid Miles", "Rate / Mile", "Gross Pay Estimate",
                        "Miles Source", "Status", "Notes", "Updated (ET)",
                    ],
                    [
                        "MILE-001", 46247, "TRIP-001", "ROUTE-001",
                        46241.6875, 46244.3333333333, "Morristown, TN",
                        "Rialto, CA", 1500, 0.986, 1479, "Settlement", "Final", "", 46247.5,
                    ],
                    ["", "", "", "", "", "", "", "", "", 0.986, "", "", "", "", ""],
                ],
                "mileage_settings_values": [
                    ["Setting", "Value"],
                    ["Rate per paid mile", 0.986],
                ],
            }
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mileage_summary"]["entry_count"], 1)
        self.assertEqual(result["mileage_summary"]["gross_pay_estimate"], "1479.00")

    def test_status_splits_and_default_rate_fallback(self):
        result = policy.resolve(
            self.payload(
                mileage=[
                    mileage_entry(
                        company_paid_miles="1000",
                        rate_per_mile="",
                        status="Final",
                    ),
                    mileage_entry(
                        entry_id="MILE-002",
                        trip_id="TRIP-002",
                        company_paid_miles="500",
                        status="Estimated",
                    ),
                ]
            )
        )
        summary = result["mileage_summary"]
        self.assertEqual(summary["final_paid_miles"], "1,000")
        self.assertEqual(summary["estimated_paid_miles"], "500")
        self.assertEqual(summary["gross_pay_estimate"], "1479.00")

    def test_blank_nonvoid_miles_requests_company_value(self):
        for status in ("Planned", "Estimated", "Final"):
            with self.subTest(status=status):
                result = policy.resolve(
                    self.payload(
                        mileage=[
                            mileage_entry(
                                company_paid_miles="",
                                status=status,
                            )
                        ]
                    )
                )
                self.assertFalse(result["mileage_summary"]["data_complete"])
                self.assertIn(
                    "company_paid_miles_required",
                    [item["code"] for item in result["actions_required"]],
                )


class InputHealthTests(unittest.TestCase):
    def strict_payload(self) -> dict:
        return {
            "now": "2026-08-15T02:45:00-04:00",
            "brief_slot": "AM",
            "strict_inputs": True,
            "tasks_values": [["Task ID", "Tier"]],
            "control_values": [["Record ID", "Type"]],
            "routes_values": [["Route ID", "Endpoint A"]],
            "trips_values": [["Trip ID", "Status"]],
            "travel_settings_values": [["Setting ID", "Setting", "Value", "Status"]],
            "mileage_values": [["Entry ID", "Status"]],
            "mileage_settings_values": [["Setting", "Value"]],
            "appointments": [],
        }

    def test_strict_inputs_and_run_log_are_healthy(self):
        result = policy.resolve(self.strict_payload())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["input_health"]["status"], "ok")
        self.assertEqual(result["run_log_fields"]["Run ID"], "OPS-2026-08-15-AM")
        self.assertEqual(result["run_log_fields"]["Status"], "OK")

    def test_strict_missing_range_fails_closed(self):
        payload = self.strict_payload()
        payload.pop("mileage_values")
        result = policy.resolve(payload)
        self.assertEqual(result["status"], "error")
        self.assertIn("missing mileage_values", result["input_health"]["issues"])
        self.assertEqual(result["run_log_fields"]["Status"], "Error")

    def test_invalid_brief_slot_is_rejected(self):
        payload = self.strict_payload()
        payload["brief_slot"] = "NOON"
        result = policy.resolve(payload)
        self.assertEqual(result["status"], "error")
        self.assertIn("Brief slot must be AM or PM.", result["errors"])


class IntegrationTests(unittest.TestCase):
    def test_raw_route_trip_and_settings_values_resolve(self):
        result = policy.resolve(
            {
                "now": "2026-08-16T10:00:00-04:00",
                "brief_slot": "AM",
                "tasks_values": [["Task ID", "Tier"]],
                "control_values": [["Record ID", "Type"]],
                "routes_values": [
                    [
                        "Route ID",
                        "Endpoint A",
                        "Endpoint B",
                        "Route A → B",
                        "Route B → A",
                        "Avg A → B (hrs)",
                        "Avg B → A (hrs)",
                        "Operation Profile",
                        "Status",
                        "Notes",
                        "Created (ET)",
                        "Updated (ET)",
                    ],
                    [
                        "ROUTE-001",
                        "El Paso, TX",
                        "Parsons, KS",
                        "US-54 → I-40 → Oklahoma City → I-44 → US-169 → US-400",
                        "",
                        17,
                        "",
                        "Default team truck",
                        "Active",
                    ],
                ],
                "trips_values": [
                    [
                        "Trip ID",
                        "Route ID",
                        "Origin",
                        "Destination",
                        "Departure (ET)",
                        "ETA (ET)",
                        "ETA Source",
                        "Current Location",
                        "Location Time (ET)",
                        "Weather Watch",
                        "Watch Expires (ET)",
                        "Status",
                        "Route Override",
                        "Notes",
                        "Updated (ET)",
                    ],
                    [
                        "TRIP-001",
                        "ROUTE-001",
                        "El Paso, TX",
                        "Parsons, KS",
                        "8/16/2026 5:00:00",
                        "",
                        "",
                        "Tucumcari, NM",
                        "8/16/2026 9:30:00",
                        "Active",
                        "",
                        "Active",
                    ],
                ],
                "travel_settings_values": [
                    ["Setting ID", "Setting", "Value", "Notes", "Status", "Updated (ET)"],
                    [
                        "TRAVEL-009",
                        "Friday PM destination confirmation",
                        "Enabled",
                        "",
                        "Active",
                    ],
                ],
                "appointments": [],
            }
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["trip_status"]["eta"], "2026-08-16T22:00:00-04:00")
        self.assertTrue(result["route_weather_allowed"])

    def test_raw_sheet_values_resolve_current_vacation(self):
        payload = {
            "now": "2026-08-14T14:45:00-04:00",
            "brief_slot": "PM",
            "tasks_values": [
                ["Task ID", "Tier", "Classification", "Subsystem", "Task", "Status", "Visibility", "Active From", "Active Through", "Recurrence / State Rule", "Notes", "Updated (ET)"],
                ["TASK-017", "Low", "Personal", "", "Test local GUPPI/AI model on RTX 4090", "Active", "Both", "", "", "", "", "8/14/2026"],
            ],
            "control_values": [
                ["Record ID", "Type", "Item", "State", "Starts At (ET)", "Expires At (ET)", "Notes", "Status", "Updated (ET)"],
                ["CTRL-001", "Mode Override", "Vacation override", "HOME", "8/12/2026 0:00:00", "8/21/2026 12:00:00", "", "Active", "8/14/2026"],
            ],
            "appointments": [],
        }
        result = policy.resolve(payload)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["mode"], "HOME")
        self.assertEqual(result["mode_source"], "override")
        self.assertTrue(result["weather_allowed"])
        self.assertEqual(result["visible_task_ids"], ["TASK-017"])
        self.assertIn("GUPPI", result["ops_status_markdown"])
        self.assertEqual(result["appointment_window"]["kind"], "home_day_before")

    def test_conflict_returns_error_status(self):
        payload = {
            "now": "2026-08-14T14:45:00-04:00",
            "tasks": [],
            "controls": [
                override("C1", "HOME", "2026-08-14T00:00:00-04:00", "2026-08-15T00:00:00-04:00", 2),
                override("C2", "ROAD", "2026-08-14T00:00:00-04:00", "2026-08-15T00:00:00-04:00", 3),
            ],
        }
        result = policy.resolve(payload)
        self.assertEqual(result["status"], "error")
        self.assertIsNone(result["mode"])

    def test_weather_is_allowed_only_in_home_mode(self):
        home = policy.resolve({
            "now": "2026-08-13T14:45:00-04:00",
            "brief_slot": "PM",
            "tasks": [],
            "controls": [],
            "appointments": [],
        })
        road = policy.resolve({
            "now": "2026-08-15T14:45:00-04:00",
            "brief_slot": "PM",
            "tasks": [],
            "controls": [],
            "appointments": [],
        })
        self.assertTrue(home["weather_allowed"])
        self.assertFalse(road["weather_allowed"])


if __name__ == "__main__":
    unittest.main()
