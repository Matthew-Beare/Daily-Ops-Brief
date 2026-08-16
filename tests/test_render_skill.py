#!/usr/bin/env python3
"""Tests for the reproducible skill renderer."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "render_skill.py"
SPEC = importlib.util.spec_from_file_location("render_skill", MODULE_PATH)
assert SPEC and SPEC.loader
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class RenderSkillTests(unittest.TestCase):
    def test_renders_sheet_urls_without_copying_live_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "ops.json"
            config.write_text(
                json.dumps(
                    {
                        "ops_status_register_id": "example_ops_123",
                        "mileage_pay_tracker_id": "example_miles_456",
                    }
                ),
                encoding="utf-8",
            )
            output = root / "rendered"
            skill_path = renderer.render(config, output)
            text = skill_path.read_text(encoding="utf-8")
            self.assertIn("/d/example_ops_123/edit", text)
            self.assertIn("/d/example_miles_456/edit", text)
            self.assertNotIn("{{", text)
            self.assertTrue((output / "scripts" / "ops_policy.py").exists())
            self.assertTrue((output / "references" / "email-reconciliation.md").exists())
            self.assertFalse((output / "SKILL.md.tmpl").exists())

    def test_refuses_unconfigured_sheet_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / "ops.json"
            config.write_text(
                json.dumps(
                    {
                        "ops_status_register_id": "SET_ME",
                        "mileage_pay_tracker_id": "example_miles_456",
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "ops_status_register_id"):
                renderer.render(config, root / "rendered")


if __name__ == "__main__":
    unittest.main()
