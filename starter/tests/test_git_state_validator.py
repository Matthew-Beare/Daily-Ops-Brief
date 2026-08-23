from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_state", ROOT / "tools/validate_state.py")
VALIDATE_STATE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(VALIDATE_STATE)

EVENT_ID = "123e4567-e89b-42d3-a456-426614174000"


def valid_event() -> dict:
    return {
        "event_id": EVENT_ID,
        "domain": "appointments",
        "entity_id": "appointment-001",
        "event_type": "appointment-created",
        "recorded_at": "2026-08-23T15:30:00-06:00",
        "effective_at": "2026-09-02T10:00:00-06:00",
        "schema_version": 1,
        "provenance": {
            "source_type": "user-confirmation",
            "source_id": "conversation-current",
            "captured_at": "2026-08-23T15:29:00-06:00",
        },
        "payload": {"status": "scheduled", "title": "Appointment"},
    }


def valid_snapshot() -> dict:
    return {
        "domain": "appointments",
        "schema_version": 1,
        "updated_at": "2026-08-23T15:30:01-06:00",
        "source_event_ids": [EVENT_ID],
        "items": [{"id": "appointment-001", "status": "scheduled"}],
    }


class GitStateValidatorTests(unittest.TestCase):
    def test_valid_event_and_snapshot_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state = Path(tempdir) / "state"
            event_dir = state / "events" / "appointments" / "2026"
            snapshot_dir = state / "snapshots"
            event_dir.mkdir(parents=True)
            snapshot_dir.mkdir(parents=True)
            (event_dir / f"{EVENT_ID}.json").write_text(json.dumps(valid_event()), encoding="utf-8")
            (snapshot_dir / "appointments.json").write_text(json.dumps(valid_snapshot()), encoding="utf-8")
            self.assertEqual(VALIDATE_STATE.validate_state_tree(state), [])

    def test_event_requires_offset_aware_timestamp(self) -> None:
        event = valid_event()
        event["recorded_at"] = "2026-08-23T15:30:00"
        errors = VALIDATE_STATE.validate_event(event, expected_filename=f"{EVENT_ID}.json")
        self.assertTrue(any("explicit UTC offset" in error for error in errors))

    def test_event_filename_must_match_event_uuid(self) -> None:
        errors = VALIDATE_STATE.validate_event(valid_event(), expected_filename="different.json")
        self.assertTrue(any("event filename must equal" in error for error in errors))

    def test_obvious_credentials_are_forbidden_even_in_private_git(self) -> None:
        event = valid_event()
        event["payload"]["access_token"] = "secret-value"
        errors = VALIDATE_STATE.validate_event(event, expected_filename=f"{EVENT_ID}.json")
        self.assertTrue(any("forbidden credential field" in error for error in errors))

    def test_snapshot_dangling_event_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state = Path(tempdir) / "state"
            (state / "events" / "appointments" / "2026").mkdir(parents=True)
            (state / "snapshots").mkdir(parents=True)
            snapshot = valid_snapshot()
            snapshot["source_event_ids"] = ["123e4567-e89b-42d3-a456-426614174001"]
            (state / "snapshots" / "appointments.json").write_text(json.dumps(snapshot), encoding="utf-8")
            errors = VALIDATE_STATE.validate_state_tree(state)
            self.assertTrue(any("does not exist in state/events" in error for error in errors))

    def test_snapshot_rejects_duplicate_event_references(self) -> None:
        snapshot = valid_snapshot()
        snapshot["source_event_ids"] = [EVENT_ID, EVENT_ID]
        errors = VALIDATE_STATE.validate_snapshot(snapshot, expected_domain="appointments")
        self.assertTrue(any("must not contain duplicates" in error for error in errors))

    def test_uuid_fixture_is_rfc4122_variant(self) -> None:
        parsed = UUID(EVENT_ID)
        self.assertEqual(parsed.variant, "specified in RFC 4122")


if __name__ == "__main__":
    unittest.main()
