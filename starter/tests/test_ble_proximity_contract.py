from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class BleProximityContractTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_android_ble_is_optional_and_permission_scoped(self):
        manifest = self.text("clients/android/app/src/main/AndroidManifest.xml")
        activity = self.text("clients/android/app/src/main/java/org/mirror/mira/MainActivity.java")
        self.assertIn("android.permission.BLUETOOTH_SCAN", manifest)
        self.assertIn("android.permission.BLUETOOTH_CONNECT", manifest)
        self.assertIn('android.hardware.bluetooth_le', manifest)
        self.assertIn('android:required="false"', manifest)
        self.assertIn("requestBlePermissions", activity)
        self.assertIn("startBleScan", activity)
        self.assertIn("result.getRssi()", activity)
        self.assertIn("stable_identifier_hint", activity)

    def test_ble_ui_does_not_treat_rssi_or_rotating_address_as_canonical_identity(self):
        ui = self.text("clients/pwa/ble-proximity.js")
        self.assertIn("warmer/colder", ui)
        self.assertIn("RSSI is not a tape measure", ui)
        self.assertIn("address may rotate", ui)
        self.assertIn("stable_identifier_hint", ui)
        self.assertIn('protocol: "ble_advertisement"', ui)
        self.assertIn("state.selectedAsset.uuid", ui)

    def test_ble_ui_is_in_shared_offline_shell(self):
        hardening = self.text("clients/pwa/client-hardening.js")
        worker = self.text("clients/pwa/sw.js")
        self.assertIn("ble-proximity.js", hardening)
        self.assertIn("ble-proximity.js", worker)


if __name__ == "__main__":
    unittest.main()
