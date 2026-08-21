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

    def test_missing_key_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing configuration keys"):
            BOOTSTRAP.render("Hello {{NAME}}", {})

    def test_nested_config_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "config.json"
            path.write_text(json.dumps({"BAD": {"nested": True}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be a scalar"):
                BOOTSTRAP.load_config(path)


if __name__ == "__main__":
    unittest.main()
