from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FullInventoryUiTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_shared_gui_exposes_inventory_ingress_relocation_and_labels(self):
        html = self.text("clients/pwa/index.html")
        app = self.text("clients/pwa/app.js")
        for phrase in ("Inventory", "Add item", "Add category", "Add location", "Photos & files", "Print QR label", "Print barcode"):
            self.assertIn(phrase, html)
        for command in ("inventory.asset.create", "inventory.asset.update", "inventory.asset.relocate", "inventory.identifier.assign"):
            self.assertIn(command, app)
        self.assertIn("drag", app)
        self.assertIn("/v1/labels/", app)
        self.assertIn("/v1/compatibility", app)

    def test_windows_and_linux_share_the_exact_pwa(self):
        config = self.text("clients/desktop/src-tauri/tauri.conf.json")
        self.assertIn('"frontendDist": "../../pwa"', config)

    def test_android_packages_same_pwa_and_keeps_native_bridges(self):
        gradle = self.text("clients/android/app/build.gradle")
        activity = self.text("clients/android/app/src/main/java/org/mirror/mira/MainActivity.java")
        self.assertIn('main.assets.srcDirs += ["../../pwa"]', gradle)
        self.assertIn("WebViewAssetLoader", activity)
        self.assertIn('addJavascriptInterface(new NativeBridge(), "MirrorNative")', activity)
        self.assertIn("scanBarcode", activity)
        self.assertIn("GmsBarcodeScanning", activity)
        self.assertIn("SpeechService.start", activity)
        self.assertIn("ReminderScheduler.schedule", activity)
        self.assertIn("openExternal", activity)

    def test_cloud_provider_choices_are_real_and_apple_is_not_faked(self):
        html = self.text("clients/pwa/index.html")
        defaults = self.text("provider-defaults.json")
        self.assertIn("Continue with Google", html)
        self.assertIn("Use Microsoft 365", html)
        self.assertIn('"default_profile": "google_workspace"', defaults)
        self.assertIn("no_claim_of_general_icloud_drive_access", defaults)


if __name__ == "__main__":
    unittest.main()
