from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent


class ShipReadinessContractTests(unittest.TestCase):
    def load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def repo_text(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_google_workspace_is_default_but_not_architectural_dependency(self):
        providers = self.load("provider-defaults.json")
        self.assertEqual("google_workspace", providers["default_profile"])
        self.assertTrue(providers["profiles"]["google_workspace"]["default"])
        self.assertFalse(providers["profiles"]["google_workspace"]["broad_scopes_by_default"])
        self.assertIn("microsoft_365", providers["profiles"])
        self.assertIn("apple_manual", providers["profiles"])
        self.assertIn("no_claim_of_general_icloud_drive_access", providers["profiles"]["apple_manual"]["oauth"])

    def test_one_release_contract_governs_every_client_and_enforces_minimum(self):
        release = self.load("clients/release.json")
        self.assertEqual(1, release["api_major"])
        self.assertEqual({"web", "windows", "linux", "android", "cli"}, set(release["clients"]))
        self.assertEqual(1, len(set(release["clients"].values())))
        self.assertEqual(release["product_version"], release["compatibility"]["minimum_client_version"])
        self.assertTrue(release["compatibility"]["clients_must_preflight_before_mutation"])
        guard = self.text("service/release_guard.py")
        self.assertIn("minimum_client_version", guard)
        self.assertIn("X-Mirror-Client", guard)
        self.assertIn("status_code=426", guard)

    def test_docker_service_has_inventory_evidence_labels_compatibility_and_oauth(self):
        service = self.text("service/app.py")
        dockerfile = self.text("service/Dockerfile")
        for endpoint in (
            "/v1/health", "/v1/compatibility", "/v1/inventory/tree", "/v1/assets",
            "/v1/commands", "/v1/evidence", "/v1/labels/{asset_uuid}.svg",
            "/v1/auth/providers", "/v1/auth/google/start", "/v1/auth/microsoft/start",
        ):
            self.assertIn(endpoint, service)
        for command in (
            "inventory.category.create", "inventory.location.create", "inventory.asset.create",
            "inventory.asset.update", "inventory.asset.relocate", "inventory.identifier.assign",
            "capture.barcode_qr_scan",
        ):
            self.assertIn(command, service)
        self.assertIn("MIRROR_TOKEN_KEY", service)
        self.assertIn("code_challenge_method", service)
        for packaged in ("provider_extensions.py", "platform_foundations.py", "product_v1.py", "enrichment.py", "oauth_hardening.py", "idempotency.py", "release_guard.py", "signed_media.py"):
            self.assertIn(packaged, dockerfile)
        self.assertIn("USER mirror", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)

    def test_cloud_evidence_is_real_and_requires_provider_readback(self):
        adapters = self.text("service/provider_extensions.py")
        self.assertIn("https://www.googleapis.com/upload/drive/v3/files", adapters)
        self.assertIn("https://graph.microsoft.com/v1.0/me/drive", adapters)
        self.assertIn("evidence_replication", adapters)
        self.assertIn("Google Drive readback failed after upload", adapters)
        self.assertIn("OneDrive readback failed after upload", adapters)
        self.assertIn("readback_verified", adapters)
        self.assertIn("/v1/integrations/provider-health", adapters)
        self.assertIn("No general iCloud Drive server API is claimed", adapters)

    def test_customer_api_defaults_to_authenticated_mutations(self):
        run = self.text("service/run.py")
        compose = self.text("service/docker-compose.example.yml")
        self.assertIn('MIRROR_AUTH_MODE", "required"', run)
        self.assertIn("MIRROR_ACCESS_TOKEN", run)
        self.assertIn("hmac.compare_digest", run)
        self.assertIn("Idempotency-Key", run)
        self.assertIn("MIRROR_AUTH_MODE: required", compose)
        self.assertIn("MIRROR_ACCESS_TOKEN", compose)
        self.assertIn("MIRROR_TOKEN_KEY", compose)

    def test_oauth_preserves_refresh_tokens_and_rejects_external_return_targets(self):
        hardening = self.text("service/oauth_hardening.py")
        self.assertIn("refresh_token", hardening)
        self.assertIn("previous", hardening)
        self.assertIn("parsed.netloc == expected.netloc", hardening)
        self.assertIn("install_oauth_hardening", self.text("service/run.py"))

    def test_official_clients_use_server_replay_protection(self):
        middleware = self.text("service/idempotency.py")
        gui = self.text("clients/pwa/client-hardening.js")
        cli = self.text("clients/desktop/src-tauri/src/bin/mira-cli.rs")
        self.assertIn("command_idempotency", middleware)
        self.assertIn("X-Mirror-Idempotent-Replay", middleware)
        self.assertIn('"Idempotency-Key"', gui)
        self.assertIn('"Idempotency-Key"', cli)

    def test_plus_companion_never_claims_subscription_as_external_compute(self):
        companion = self.load("chatgpt-companion-contract.json")
        self.assertFalse(companion["model_access"]["embedded_openai_model_backend"])
        self.assertFalse(companion["model_access"]["openai_api_key_required_for_companion"])
        self.assertEqual("ChatGPT", companion["model_access"]["chat_surface"])
        self.assertIn("MCP", companion["model_access"]["transport"])
        self.assertTrue(companion["feature_delivery"]["unreviewed_dynamic_code_execution_in_customer_runtime"] is False)

    def test_feature_rfid_home_assistant_and_google_migration_are_live_service_surfaces(self):
        foundations = self.text("service/platform_foundations.py")
        for endpoint in (
            "/v1/features/requests", "/v1/rfid/tags/bind", "/v1/rfid/observations",
            "/v1/integrations/home-assistant/status", "/v1/integrations/home-assistant/events",
            "/v1/integrations/home-assistant/service", "/v1/migrations/export", "/v1/migrations/stage",
            "/v1/migrations/google/auth/start", "/v1/migrations/google/discover", "/v1/migrations/google/stage-sheet",
        ):
            self.assertIn(endpoint, foundations)
        self.assertIn('namespace = f"rfid:{protocol}"', foundations)
        self.assertIn("location_promoted\": False", foundations)
        self.assertIn("drive.readonly", foundations)
        self.assertIn("spreadsheets.readonly", foundations)
        self.assertIn("canonical_state_changed\": False", foundations)

    def test_storage_migration_preserves_uuid_and_clients_do_not_depend_on_database(self):
        portability = self.load("storage-portability-contract.json")
        self.assertTrue(portability["canonical_identity"]["preserve_across_migration"])
        self.assertEqual("implemented_single_node_starter", portability["structured_state_adapters"]["sqlite"]["status"])
        self.assertIn("postgresql", portability["structured_state_adapters"])
        self.assertIn("sql_server", portability["structured_state_adapters"])
        self.assertIn("clients talk only to the MIRROR API", portability["client_rule"])

    def test_shared_client_has_commercial_feature_and_migration_studios(self):
        hardening = self.text("clients/pwa/client-hardening.js")
        ui = self.text("clients/pwa/platform-ui.js")
        css = self.text("clients/pwa/commercial.css")
        worker = self.text("clients/pwa/sw.js")
        self.assertIn("commercial.css", hardening)
        self.assertIn("platform-ui.js", hardening)
        self.assertIn("smart-capture.js", hardening)
        self.assertIn("Feature Studio", ui)
        self.assertIn("RFID / NFC identity", ui)
        self.assertIn("Import existing Google Sheets", ui)
        self.assertIn("mirror-client-shell-v5", worker)
        self.assertIn("product-v1.js", worker)
        self.assertIn("smart-capture.js", worker)
        self.assertIn("--mira-accent", css)

    def test_client_contract_exposes_ship_ready_inventory_surface(self):
        contract = self.load("client-api-contract.json")
        self.assertEqual("1.1", contract["api_contract"])
        self.assertIn("inventory.asset.relocate", contract["inventory_commands"])
        self.assertIn("arbitrary_asset_attachment", contract["capture_surface"])
        self.assertIn("asset_label", contract["http_reference"])
        self.assertTrue(contract["security"]["provider_oauth_uses_pkce"])

    def test_android_has_release_apk_aab_external_signing_and_current_play_target(self):
        gradle = self.text("clients/android/app/build.gradle")
        root_gradle = self.text("clients/android/build.gradle")
        self.assertIn("compileSdk 36", gradle)
        self.assertIn("targetSdk 36", gradle)
        self.assertIn('version "8.10.1"', root_gradle)
        self.assertIn("MIRA_ANDROID_KEYSTORE_PATH", gradle)
        self.assertIn("signingConfigs", gradle)
        self.assertIn("android.permission.NFC", self.text("clients/android/app/src/main/AndroidManifest.xml"))
        workflow_path = REPO_ROOT / ".github/workflows/android-client.yml"
        if not workflow_path.is_file():
            self.skipTest("canonical-only Android workflow is not part of generated distribution")
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn('platforms;android-36', workflow)
        self.assertIn('gradle-version: "8.11.1"', workflow)
        self.assertIn(":app:assembleRelease", workflow)
        self.assertIn(":app:bundleRelease", workflow)
        self.assertIn("MIRA_ANDROID_KEYSTORE_BASE64", workflow)
        self.assertIn("apksigner", workflow)
        self.assertIn("jarsigner", workflow)
        self.assertIn("mira-android-release.aab", workflow)
        self.assertIn("mira-android-release", workflow)

    def test_desktop_builds_installable_packages_not_only_raw_binaries(self):
        tauri = self.load("clients/desktop/src-tauri/tauri.conf.json")
        self.assertTrue(tauri["bundle"]["active"])
        workflow_path = REPO_ROOT / ".github/workflows/desktop-clients.yml"
        if not workflow_path.is_file():
            self.skipTest("canonical-only desktop workflow is not part of generated distribution")
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("cargo tauri build --bundles appimage,deb,rpm", workflow)
        self.assertIn("cargo tauri build --bundles nsis", workflow)
        self.assertIn("mira-linux-installers", workflow)
        self.assertIn("mira-windows-installer", workflow)


if __name__ == "__main__":
    unittest.main()
