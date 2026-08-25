from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "tools" / "scan_event.py"
spec = importlib.util.spec_from_file_location("scan_event", MODULE)
subject = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(subject)

TAG = "61ac5e8f-9fb2-4e73-af0f-1ebffde34eb7"
ASSET = "33ac3159-bc0d-426c-8137-a0b2cdedc71e"
LOCATION = "79105779-a788-48c2-ad5f-ff9c46b02c15"
SCAN = "f70f13df-18b3-4fa0-97e8-1a25f2a9de03"


class ScanEventTests(unittest.TestCase):
    def test_valid_gtin_is_classified(self):
        result = subject.normalize_scan({
            "raw_value": "036000291452",
            "captured_at": "2026-08-25T12:00:00-04:00",
            "client_id": "android-fixture",
            "symbology": "UPC_A",
        })
        self.assertEqual("product_identifier", result["classification"]["scan_class"])
        self.assertEqual("gtin", result["classification"]["namespace"])

    def test_bad_gtin_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "check digit"):
            subject.normalize_scan({
                "raw_value": "036000291453",
                "captured_at": "2026-08-25T12:00:00-04:00",
                "client_id": "android-fixture",
                "symbology": "UPC_A",
            })

    def test_preprinted_tag_is_unassigned_until_bound(self):
        result = subject.resolve_tag({
            "scan": {
                "raw_value": f"MIRROR-TAG:{TAG}",
                "captured_at": "2026-08-25T12:00:00-04:00",
                "client_id": "android-fixture",
                "symbology": "QR_CODE",
            },
            "tag_registry": [],
        })
        self.assertEqual("unassigned", result["status"])

    def test_tag_binding_is_idempotent_and_cannot_be_recycled(self):
        first = subject.bind_tag({"tag_uuid": TAG, "target_type": "asset", "target_uuid": ASSET, "tag_registry": []})
        second = subject.bind_tag({"tag_uuid": TAG, "target_type": "asset", "target_uuid": ASSET, "tag_registry": first["tag_registry"]})
        self.assertEqual("already_bound", second["status"])
        with self.assertRaisesRegex(ValueError, "different live target"):
            subject.bind_tag({"tag_uuid": TAG, "target_type": "location", "target_uuid": LOCATION, "tag_registry": first["tag_registry"]})

    def test_move_event_is_deterministic(self):
        payload = {
            "asset_uuid": ASSET,
            "location_uuid": LOCATION,
            "moved_at": "2026-08-25T12:05:00-04:00",
            "source_scan_uuid": SCAN,
        }
        first = subject.move_asset(payload)
        second = subject.move_asset(payload)
        self.assertEqual(first["event"]["event_uuid"], second["event"]["event_uuid"])
        self.assertEqual("located_at", first["event"]["relationship_type"])


if __name__ == "__main__":
    unittest.main()
