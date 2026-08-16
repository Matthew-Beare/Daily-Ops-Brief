#!/usr/bin/env python3
"""Prove that the forkable starter cannot affect the production Ops Brief."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "starter"
INSTRUCTION_TOOL_PATH = ROOT / "tools" / "project_instructions.py"
SPEC = importlib.util.spec_from_file_location(
    "project_instructions_for_isolation", INSTRUCTION_TOOL_PATH
)
assert SPEC and SPEC.loader
instructions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(instructions)


class StarterIsolationTests(unittest.TestCase):
    def test_interview_begins_with_ai_usage_question(self):
        first_line = (STARTER / "START_HERE.md").read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(first_line, "How do you currently use AI?")

    def test_starter_is_explicitly_nonproduction(self):
        readme = (STARTER / "README.md").read_text(encoding="utf-8")
        self.assertIn("NON-PRODUCTION", readme)
        self.assertIn("cannot alter the production system", readme)

    def test_production_skill_renderer_does_not_copy_starter(self):
        renderer = (ROOT / "tools" / "render_skill.py").read_text(encoding="utf-8")
        self.assertIn(' / "skill"', renderer)
        self.assertNotIn(' / "starter"', renderer)

    def test_production_policy_fingerprint_excludes_starter(self):
        self.assertTrue(
            all(not pattern.startswith("starter/") for pattern in instructions.POLICY_SOURCE_GLOBS)
        )
        self.assertTrue(
            all(
                not path.is_relative_to(STARTER)
                for path in instructions.policy_sources(ROOT)
            )
        )

    def test_production_skill_does_not_reference_starter(self):
        for path in (ROOT / "skill").rglob("*"):
            if path.is_file() and path.suffix in {".md", ".py", ".yaml"}:
                with self.subTest(path=path.relative_to(ROOT)):
                    self.assertNotIn("starter/", path.read_text(encoding="utf-8"))

    def test_starter_contains_no_local_profile(self):
        self.assertTrue((STARTER / "config" / "profile.example.json").is_file())
        self.assertFalse((STARTER / "config" / "profile.local.json").exists())


if __name__ == "__main__":
    unittest.main()
