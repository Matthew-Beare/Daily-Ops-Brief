from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bootstrap", ROOT / "scripts/bootstrap.py")
BOOTSTRAP = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(BOOTSTRAP)


class BootstrapTests(unittest.TestCase):
    def test_example_renders_without_tokens(self) -> None:
        config = BOOTSTRAP.load_config(ROOT / "starter/config.example.json")
        template = (ROOT / "starter/INSTRUCTIONS.md.tmpl").read_text(encoding="utf-8")
        rendered = BOOTSTRAP.render(template, config)
        self.assertNotIn("{{", rendered)
        self.assertIn("$my-ops-policy", rendered)
        self.assertIn("PRIVATE_REQUIRED_WHEN_PERSONAL_STATE_IS_ENABLED", rendered)
        self.assertIn("PRIVATE_GIT_REPOSITORY/state", rendered)

    def test_missing_key_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing configuration keys"):
            BOOTSTRAP.render("Hello {{NAME}}", {})

    def test_nested_config_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "config.json"
            path.write_text(json.dumps({"BAD": {"nested": True}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be a scalar"):
                BOOTSTRAP.load_config(path)

    def test_human_first_boot_is_safe_bounded_and_git_state_native(self) -> None:
        guide = (ROOT / "starter/START_HERE.md").read_text(encoding="utf-8")
        lower = guide.lower()
        self.assertIn("Minimum Useful Setup", guide)
        self.assertIn("Start now by asking only the four kickoff questions", guide)
        self.assertIn("explicit approval", lower)
        self.assertIn("partial cancellation", lower)
        self.assertIn("timezone is permanently authoritative", lower)
        self.assertIn("exact local times", lower)
        self.assertIn("recipe library", lower)
        self.assertIn("job title", lower)
        self.assertIn("mark HOME/ROAD bypassed", guide)
        self.assertIn("driving/trucking", lower)
        self.assertIn("true replacement", lower)
        self.assertIn("automatically validates, commits, pushes", guide)
        self.assertIn("private Git", guide)
        self.assertIn("Do you want help with meal planning?", guide)
        self.assertIn("public-source audit", lower)
        self.assertNotIn("1pHkTdCx", guide)
        self.assertNotIn("jbeare92", guide)
        self.assertLess(len(guide), 12000)


if __name__ == "__main__":
    unittest.main()
