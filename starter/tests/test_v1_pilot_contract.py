from __future__ import annotations

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent


class V1PilotContractTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def repo_text(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_v1_brand_and_guided_shell_load_on_every_shared_client(self):
        index = self.text("clients/pwa/index.html")
        product = self.text("clients/pwa/product-v1.js")
        self.assertIn("MIRA // MIRROR", index)
        self.assertIn("Reality, reconciled.", index)
        self.assertIn('src="product-v1.js"', index)
        self.assertIn("Set up MIRA", product)
        self.assertIn("Setup & Settings", product)
        self.assertIn("Continue with Google", product)
        self.assertIn("Create GitHub account", product)

    def test_feature_studio_is_all_platform_by_default_and_server_enforces_it(self):
        product = self.text("service/product_v1.py")
        ui = self.text("clients/pwa/product-v1.js")
        companion = self.load("chatgpt-companion-contract.json")
        for surface in ("web", "windows", "linux", "android"):
            self.assertIn(surface, product)
            self.assertIn(surface, companion["feature_delivery"]["default_target_surfaces"])
        self.assertIn("feature_requests_force_all_platforms_insert", product)
        self.assertIn("feature_requests_force_all_platforms_update", product)
        self.assertTrue(companion["feature_delivery"]["all_supported_surfaces_required_by_default"])
        self.assertIn("Every feature targets web, Windows, Linux and Android automatically", ui)

    def test_settings_are_one_mirror_authority_for_clients_and_chatgpt(self):
        product = self.text("service/product_v1.py")
        companion = self.load("chatgpt-companion-contract.json")
        self.assertIn('/v1/settings', product)
        self.assertIn("user_settings", product)
        self.assertTrue(companion["settings"]["client_and_chatgpt_bidirectional"])
        self.assertIn("settings.read", companion["mirror_tools"])
        self.assertIn("settings.update", companion["mirror_tools"])

    def test_426_update_experience_and_verified_release_feed_are_present(self):
        release_guard = self.text("service/release_guard.py")
        product_service = self.text("service/product_v1.py")
        product_ui = self.text("clients/pwa/product-v1.js")
        self.assertIn("status_code=426", release_guard)
        self.assertIn("/v1/updates/status", product_service)
        self.assertIn("releases/latest", product_service)
        self.assertIn("response.status === 426", product_ui)
        self.assertIn("MIRA needs an update", product_ui)
        self.assertIn("Custom-feature collisions", product_ui)

    def test_android_nfc_is_optional_and_binds_tag_to_asset_uuid(self):
        manifest = self.text("clients/android/app/src/main/AndroidManifest.xml")
        activity = self.text("clients/android/app/src/main/java/org/mirror/mira/MainActivity.java")
        ui = self.text("clients/pwa/product-v1.js")
        self.assertIn("android.permission.NFC", manifest)
        self.assertIn('android.hardware.nfc', manifest)
        self.assertIn('android:required="false"', manifest)
        self.assertIn("enableReaderMode", activity)
        self.assertIn("scanNfcTag", activity)
        self.assertIn("onMirrorNativeNfcResult", activity)
        self.assertIn("/v1/rfid/tags/bind", ui)
        self.assertIn("state.selectedAsset.uuid", ui)

    def test_location_qr_identity_and_move_flow_exist(self):
        service = self.text("service/product_v1.py")
        ui = self.text("clients/pwa/product-v1.js")
        self.assertIn("MIRROR:LOCATION:", service)
        self.assertIn("/v1/locations/resolve-code", service)
        self.assertIn("/v1/locations/{location_uuid}/label.svg", service)
        self.assertIn("inventory.asset.relocate", ui)

    def test_linux_packages_cover_debian_ubuntu_and_red_hat_family(self):
        cargo = self.text("clients/desktop/src-tauri/Cargo.toml")
        workflow = self.repo_text(".github/workflows/desktop-clients.yml")
        security = self.repo_text("docs/red-hat-security.md")
        self.assertIn('default-run = "mira-desktop"', cargo)
        self.assertIn("appimage,deb,rpm", workflow)
        self.assertIn("*.rpm", workflow)
        self.assertIn("RHEL 9", security)
        self.assertIn("RHEL 10", security)
        self.assertIn("removed WebKitGTK", security)
        self.assertIn(":Z", security)
        self.assertIn("rootless Podman", security)

    def test_container_packages_v1_service(self):
        dockerfile = self.text("service/Dockerfile")
        run = self.text("service/run.py")
        self.assertIn("product_v1.py", dockerfile)
        self.assertIn("install_product_v1", run)
        self.assertIn("/v1/product/info", run)

    def test_nontechnical_first_run_guide_preserves_safety_boundaries(self):
        guide = self.repo_text("docs/first-run-and-updates.md")
        self.assertIn("all supported platforms automatically", guide)
        self.assertIn("Create GitHub account", guide)
        self.assertIn("Continue with Google", guide)
        self.assertIn("HTTP 426 Upgrade Required", guide)
        self.assertIn("Full automatic mapping/apply", guide)
        self.assertIn("does not", guide.lower())


if __name__ == "__main__":
    unittest.main()
