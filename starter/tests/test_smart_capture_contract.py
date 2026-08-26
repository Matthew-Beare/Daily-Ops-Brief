from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SmartCaptureContractTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_shared_clients_load_smart_capture(self):
        hardening = self.text("clients/pwa/client-hardening.js")
        capture = self.text("clients/pwa/smart-capture.js")
        self.assertIn("smart-capture.js", hardening)
        self.assertIn("const baseCapture = capture", capture)
        self.assertIn("MIRROR:LOCATION:", capture)
        self.assertIn("inventory.asset.relocate", capture)

    def test_unmatched_gtin_can_be_enriched_without_auto_authority(self):
        capture = self.text("clients/pwa/smart-capture.js")
        enrichment = self.text("service/enrichment.py")
        self.assertIn("/v1/enrichment/gtin/", capture)
        self.assertIn("Create asset from this suggestion", capture)
        self.assertIn("product_lookup_verified: false", capture)
        self.assertIn("MIRROR_GTIN_LOOKUP_URL_TEMPLATE", enrichment)
        self.assertIn("candidate only", enrichment)
        self.assertIn("will not fabricate product metadata", enrichment)

    def test_enrichment_is_packaged(self):
        dockerfile = self.text("service/Dockerfile")
        run = self.text("service/run.py")
        self.assertIn("enrichment.py", dockerfile)
        self.assertIn("install_enrichment", run)


if __name__ == "__main__":
    unittest.main()
