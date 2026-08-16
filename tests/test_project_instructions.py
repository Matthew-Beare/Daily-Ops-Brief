#!/usr/bin/env python3
"""Tests for the versioned project-instructions contract."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "project_instructions.py"
SPEC = importlib.util.spec_from_file_location("project_instructions", MODULE_PATH)
assert SPEC and SPEC.loader
instructions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(instructions)


class ProjectInstructionTests(unittest.TestCase):
    def test_policy_sources_have_reviewed_fingerprint(self):
        self.assertEqual(instructions.check(), instructions.policy_fingerprint())

    def test_renders_complete_copy_paste_contract(self):
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
            output = root / "PROJECT_INSTRUCTIONS.md"
            rendered = instructions.render(config, output)
            text = rendered.read_text(encoding="utf-8")

            self.assertTrue(text.startswith("# DAILY BRIEFS — OPERATING INSTRUCTIONS"))
            self.assertIn("/d/example_ops_123/edit", text)
            self.assertIn("/d/example_miles_456/edit", text)
            self.assertIn("PROJECT INSTRUCTIONS UPDATE", text)
            self.assertIn("Project instructions unchanged.", text)
            self.assertIn(instructions.policy_fingerprint(), text)
            self.assertNotIn("{{", text)

    def test_rejects_stale_review_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "docs").mkdir()
            (root / "project").mkdir()
            (root / "skill" / "references").mkdir(parents=True)
            (root / "skill" / "scripts").mkdir(parents=True)
            (root / "schemas").mkdir()
            (root / "docs" / "OPERATIONS.md").write_text("changed", encoding="utf-8")
            (root / "project" / "INSTRUCTIONS.md.tmpl").write_text(
                "instructions", encoding="utf-8"
            )
            (root / "project" / "POLICY_SOURCE.sha256").write_text(
                "0" * 64, encoding="utf-8"
            )
            (root / "schemas" / "google-sheets.json").write_text("{}", encoding="utf-8")
            (root / "skill" / "SKILL.md.tmpl").write_text("skill", encoding="utf-8")
            (root / "skill" / "references" / "workflow.md").write_text(
                "workflow", encoding="utf-8"
            )
            (root / "skill" / "scripts" / "engine.py").write_text(
                "pass", encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "require policy review"):
                instructions.check(root)


if __name__ == "__main__":
    unittest.main()
