from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent


class ClientVersionLockstepTests(unittest.TestCase):
    def canonical_workflow(self, name: str) -> str:
        path = REPO_ROOT / ".github/workflows" / name
        if not path.is_file():
            self.skipTest("canonical-only build workflow is not part of generated distribution")
        return path.read_text(encoding="utf-8")

    def test_wrappers_match_single_release_version(self):
        release = json.loads((ROOT / "clients/release.json").read_text(encoding="utf-8"))
        version = release["product_version"]
        self.assertEqual({version}, set(release["clients"].values()))

        tauri = json.loads((ROOT / "clients/desktop/src-tauri/tauri.conf.json").read_text(encoding="utf-8"))
        self.assertEqual(version, tauri["version"])

        cargo = (ROOT / "clients/desktop/src-tauri/Cargo.toml").read_text(encoding="utf-8")
        self.assertRegex(cargo, rf'(?m)^version = "{re.escape(version)}"$')

        gradle = (ROOT / "clients/android/app/build.gradle").read_text(encoding="utf-8")
        self.assertIn(f'versionName "{version}"', gradle)

        app = (ROOT / "clients/pwa/app.js").read_text(encoding="utf-8")
        self.assertIn(f'const CLIENT_VERSION = "{version}";', app)
        self.assertIn(f'const API_CONTRACT = "{release["api_contract"]}";', app)

        cli = (ROOT / "clients/desktop/src-tauri/src/bin/mira-cli.rs").read_text(encoding="utf-8")
        self.assertIn(f'const CLIENT_VERSION: &str = "{version}";', cli)
        self.assertIn(f'const API_CONTRACT: &str = "{release["api_contract"]}";', cli)

    def test_android_build_reacts_to_shared_ui_changes(self):
        workflow = self.canonical_workflow("android-client.yml")
        self.assertIn('starter/clients/pwa/**', workflow)
        self.assertIn('starter/clients/release.json', workflow)

    def test_docker_build_is_a_required_pr_surface_for_service_changes(self):
        workflow = self.canonical_workflow("docker-service.yml")
        self.assertIn("docker build", workflow)
        self.assertIn("/v1/health", workflow)
        self.assertIn("inventory.category.create", workflow)


if __name__ == "__main__":
    unittest.main()
