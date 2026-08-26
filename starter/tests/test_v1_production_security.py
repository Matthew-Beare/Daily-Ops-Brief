from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent


class V1ProductionSecurityTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def repo_text(self, relative: str) -> str:
        return (REPO / relative).read_text(encoding="utf-8")

    def load(self, relative: str):
        return json.loads(self.text(relative))

    def test_chatgpt_google_is_stock_serverless_runtime(self):
        contract = self.load("chatgpt-companion-contract.json")
        native = contract["runtime_modes"]["chatgpt_google_native"]
        self.assertTrue(native["default_for_nontechnical_users"])
        self.assertFalse(native["user_managed_server_required"])
        self.assertFalse(native["linux_required"])
        self.assertFalse(native["docker_required"])
        self.assertFalse(native["openai_api_key_required"])
        self.assertFalse(native["stock_use_requires_github"])
        self.assertTrue(native["google_workspace_required"])
        self.assertIn("Google Drive", native["google_apps"])

    def test_google_native_authority_has_uuid_serial_receipt_and_hierarchy_contracts(self):
        schema = self.load("chatgpt-google-native/authority-schema.json")
        self.assertIn("Identifiers", schema["tables"])
        self.assertIn("serial", schema["identifier_namespaces"])
        self.assertTrue(schema["location_rules"]["physical_container_may_be_asset_and_location"])
        self.assertTrue(schema["receipt_rules"]["official_retailer_search_first"])
        self.assertTrue(schema["receipt_rules"]["ambiguous_match_requires_review"])

    def test_hosted_devices_use_one_time_enrollment_and_hashed_credentials(self):
        auth = self.text("service/device_auth.py")
        run = self.text("service/run.py")
        self.assertIn("device_enrollment_codes", auth)
        self.assertIn("token_sha256", auth)
        self.assertIn("secrets.token_urlsafe", auth)
        self.assertIn("revoked_at", auth)
        self.assertNotIn("device_token TEXT", auth)
        self.assertIn("valid_device_token", run)
        self.assertIn('"/v1/devices/enroll"', run)

    def test_receipt_reconciliation_is_provenance_and_ambiguity_safe(self):
        receipts = self.text("service/receipts.py")
        for required in (
            "receipt_line_candidates",
            "official_source",
            "confidence_threshold",
            "minimum_margin",
            "ambiguous_or_unverified",
            "identifier_conflict",
            "allocation",
            "official retailer first",
        ):
            self.assertIn(required, receipts)
        self.assertIn("source_url", receipts)
        self.assertIn("retailer_sku", receipts)
        self.assertIn('("gtin", candidate["gtin"])', receipts)

    def test_serials_and_containers_are_first_class(self):
        hierarchy = self.text("service/inventory_hierarchy.py")
        self.assertIn('/v1/assets/{asset_uuid}/serials', hierarchy)
        self.assertIn("container_location_links", hierarchy)
        self.assertIn("container_location_follows_asset", hierarchy)
        self.assertIn('/v1/assets/{asset_uuid}/where', hierarchy)
        self.assertIn("location hierarchy contains a cycle", hierarchy)

    def test_android_disallows_cleartext_and_backup_and_keeps_rfid_optional(self):
        manifest = self.text("clients/android/app/src/main/AndroidManifest.xml")
        self.assertIn('android:allowBackup="false"', manifest)
        self.assertIn('android:usesCleartextTraffic="false"', manifest)
        self.assertIn('android.permission.NFC', manifest)
        self.assertIn('android.hardware.nfc', manifest)
        self.assertIn('android:required="false"', manifest)

    def test_desktop_csp_does_not_allow_arbitrary_script_or_frames(self):
        tauri = self.load("clients/desktop/src-tauri/tauri.conf.json")
        csp = tauri["app"]["security"]["csp"]
        self.assertIn("script-src 'self'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn("script-src *", csp)
        self.assertNotIn("'unsafe-eval'", csp)

    def test_production_https_keeps_mirror_service_off_host_port(self):
        compose = self.text("service/docker-compose.production.yml")
        caddy = self.text("service/Caddyfile.example")
        self.assertIn("MIRROR_PUBLIC_BASE_URL: https://", compose)
        self.assertIn("expose:\n      - \"8765\"", compose)
        self.assertNotIn('8765:8765', compose)
        self.assertIn("no-new-privileges:true", compose)
        self.assertIn("cap_drop", compose)
        self.assertIn("Strict-Transport-Security", caddy)
        self.assertIn("reverse_proxy mirror:8765", caddy)

    def test_conflict_recovery_is_plain_language_and_never_force_resolves(self):
        reconcile = self.text("tools/reconcile_upstream.py")
        renderer = self.text("tools/render_conflict_report.py")
        workflow = self.repo_text(".github/workflows/upstream-sync.yml")
        self.assertIn("Your current version is safe", renderer)
        self.assertIn("Do not delete", reconcile)
        self.assertIn("keep your behavior", reconcile)
        self.assertIn("combine both", reconcile)
        self.assertIn("render_conflict_report.py", workflow)
        self.assertNotIn("git checkout --theirs", workflow)
        self.assertNotIn("git checkout --ours", workflow)

    def test_visual_qa_captures_real_app_surfaces(self):
        spec = self.text("visual-qa/mira.spec.js")
        workflow = self.repo_text(".github/workflows/visual-qa.yml")
        self.assertIn("desktop-first-run.png", spec)
        self.assertIn("android-first-run.png", spec)
        self.assertIn("android-receipts.png", spec)
        self.assertIn("playwright", workflow)
        self.assertIn("upload-artifact", workflow)


if __name__ == "__main__":
    unittest.main()
