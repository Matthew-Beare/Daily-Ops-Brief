from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent


class IntegrationPlatformContractTests(unittest.TestCase):
    def load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def repo_text(self, relative: str) -> str:
        return (REPO / relative).read_text(encoding="utf-8")

    def test_stock_mode_requires_google_but_not_linux_or_server(self):
        modes = self.load("deployment-modes.json")
        stock = modes["modes"][modes["stock_mode"]]
        self.assertEqual("google_native", modes["stock_mode"])
        self.assertTrue(stock["google_required"])
        self.assertFalse(stock["linux_required"])
        self.assertFalse(stock["docker_required"])
        self.assertFalse(stock["server_required"])
        self.assertEqual("Google Drive", stock["evidence_default"])
        skill = self.text("chatgpt-google-native/SKILL.md")
        self.assertIn("Google Workspace is required", skill)
        self.assertIn("Do not require Linux", skill)
        self.assertIn("Action Required — Connect Google Workspace", skill)

    def test_self_hosted_catalog_is_capability_based_and_extensible(self):
        catalog = self.load("integration-catalog.json")
        for name in ("paperless_ngx", "home_assistant", "plex", "sonarr", "radarr", "node_red", "mqtt"):
            self.assertIn(name, catalog["services"])
        self.assertEqual("reserved_contract_only", catalog["services"]["solar_telemetry"]["status"])
        self.assertIn("local_bridge", catalog["connection_modes"])
        self.assertIn("Integrations expose capabilities", catalog["authority_rule"])
        self.assertIn("workflow.deploy", catalog["services"]["node_red"]["dangerous_capabilities"])
        self.assertEqual(["mqtt.subscribe"], catalog["services"]["mqtt"]["default_enabled_capabilities"])

    def test_google_native_local_bridge_never_exports_local_service_secrets(self):
        bridge = self.load("local-bridge-contract.json")
        self.assertIn("OS-protected client storage", bridge["transport"]["local_credentials"])
        self.assertTrue(bridge["safety"]["local_secrets_never_leave_bridge_device"])
        self.assertTrue(bridge["safety"]["external_services_are_never_canonical_authority_by_accident"])
        schema = self.load("chatgpt-google-native/authority-schema.json")
        self.assertIn("IntegrationActions", schema["tables"])
        self.assertIn("IntegrationResults", schema["tables"])
        self.assertTrue(schema["integration_rules"]["local_service_credentials_never_stored_in_google"])

    def test_backup_defaults_are_boomer_safe_and_honest(self):
        policy = self.load("backup-policy.json")
        self.assertEqual(7, policy["defaults"]["full_interval_days"])
        self.assertEqual(1, policy["defaults"]["incremental_interval_days"])
        self.assertEqual("google_drive", policy["defaults"]["destination"])
        self.assertTrue(policy["safety"]["successful_backup_requires_readback"])
        self.assertEqual("create and label a full_fallback snapshot instead", policy["safety"]["fallback_when_incremental_not_provable"])
        scheduler = self.text("service/backup_scheduler.py")
        self.assertIn('effective_type = "full" if requested_type == "full" else "full_fallback"', scheduler)
        self.assertIn("PRAGMA integrity_check", scheduler)
        self.assertIn("readback_verified", scheduler)

    def test_receipts_have_stable_merchants_and_maintenance_fitment(self):
        merchants = self.text("service/merchants.py")
        self.assertIn("receipt_merchant_links", merchants)
        self.assertIn("merchant_link_queue", merchants)
        self.assertIn("queue_receipt_merchant_insert", merchants)
        self.assertIn("walmart.com", merchants)
        maintenance = self.text("service/maintenance.py")
        self.assertIn("asset_meters", maintenance)
        self.assertIn("maintenance_events", maintenance)
        self.assertIn("Is this purchase for a vehicle, mower, or other equipment?", maintenance)
        schema = self.load("chatgpt-google-native/authority-schema.json")
        self.assertIn("Merchants", schema["tables"])
        self.assertIn("MaintenanceEvents", schema["tables"])

    def test_media_identity_is_provider_neutral(self):
        media = self.text("service/media.py")
        self.assertIn("media_uuid", media)
        self.assertIn("media_provider_bindings", media)
        self.assertIn("media.playback.control", media)
        self.assertIn("readback_verified", media)
        schema = self.load("chatgpt-google-native/authority-schema.json")
        self.assertIn("Media", schema["tables"])
        self.assertIn("MediaProviderBindings", schema["tables"])

    def test_every_asset_supports_photo_first_ui(self):
        contract = self.load("asset-media-contract.json")
        universal = contract["universality"]
        self.assertTrue(universal["photo_support_required_for_every_asset_type"])
        self.assertTrue(universal["primary_photo_supported_for_every_asset"])
        self.assertTrue(universal["gallery_supported_for_every_asset"])
        self.assertTrue(universal["asset_creation_without_photo_allowed"])
        ui = contract["ui_contract"]
        self.assertTrue(ui["beautiful_ui_requirement"])
        self.assertIn("primary photo", ui["asset_card"])
        self.assertIn("Add photo / Take photo", ui["photo_action"])
        self.assertTrue(contract["derived_variants"]["original_preserved"])

    def test_rfid_wand_is_inventory_hardware_not_radio_programming(self):
        contract = self.load("rfid-wand-hardware-contract.json")
        hardware = contract["hardware_concept"]
        self.assertEqual("handheld_rfid_inventory_wand", hardware["device_role"])
        self.assertTrue(hardware["baofeng_or_similar_chassis_may_be_donor"])
        self.assertFalse(hardware["radio_transmit_required"])
        self.assertFalse(hardware["radio_receive_required"])
        self.assertFalse(hardware["frequency_programming_required"])
        self.assertTrue(contract["event_contract"]["uses_existing_rfid_asset_tracking_contract"])
        self.assertTrue(contract["inventory_behavior"]["passive_read_never_silently_moves_asset"])
        self.assertTrue(contract["ui"]["show_last_scan_asset_photo_when_available"])
        self.assertNotIn("chirp", json.dumps(contract).lower())

    def test_integration_runtime_is_actually_wired_and_packaged(self):
        run = self.text("service/run.py")
        docker = self.text("service/Dockerfile")
        for installer in (
            "install_receipts", "install_merchants", "install_integrations", "install_media",
            "install_maintenance", "install_migration_apply", "install_backup_scheduler", "install_device_auth",
        ):
            self.assertIn(installer, run)
        for module in (
            "receipts.py", "merchants.py", "integrations.py", "media.py", "maintenance.py",
            "migration_apply.py", "backup_scheduler.py", "device_auth.py",
        ):
            self.assertIn(module, docker)
        client = self.text("clients/pwa/client-hardening.js")
        worker = self.text("clients/pwa/sw.js")
        self.assertIn("integrations-v1.js", client)
        self.assertIn("integrations-v1.js", worker)

    def test_updates_preserve_old_personal_production_revision(self):
        workflow = self.repo_text(".github/workflows/upstream-sync.yml")
        self.assertIn("mira-rollback/", workflow)
        self.assertIn("git tag -a", workflow)
        self.assertIn("git push origin", workflow)
        self.assertIn("previous main revision was preserved", workflow)
        reconciler = self.text("tools/reconcile_upstream.py")
        self.assertIn("fail closed", reconciler)


if __name__ == "__main__":
    unittest.main()
