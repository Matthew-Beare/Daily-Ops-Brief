#!/usr/bin/env python3
"""Tests for the portable feature-module contract."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate_feature_manifest.py"
SPEC = importlib.util.spec_from_file_location("validate_feature_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class FeatureManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "fixtures" / "features" / "meal-planning.feature.json").read_text(encoding="utf-8"))
        cls.schema = json.loads((ROOT / "schemas" / "feature-manifest.schema.json").read_text(encoding="utf-8"))

    def test_synthetic_portable_feature_is_valid(self):
        self.assertEqual(validator.validate_manifest(self.fixture), [])

    def test_validator_and_schema_require_the_same_top_level_fields(self):
        self.assertEqual(set(self.schema["required"]), validator.REQUIRED_FIELDS)
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(self.schema["properties"]["manifest_version"]["const"], 2)

    def test_validator_and_schema_require_the_same_runtime_fields(self):
        runtime = self.schema["properties"]["runtime_contract"]
        self.assertEqual(set(runtime["required"]), validator.RUNTIME_CONTRACT_FIELDS)
        self.assertFalse(runtime["additionalProperties"])
        self.assertEqual(runtime["properties"]["on_required_failure"]["const"], "block-module-only")
        self.assertEqual(runtime["properties"]["on_optional_failure"]["const"], "degrade-capability-and-continue")

    def test_personal_data_in_shared_source_is_rejected(self):
        manifest = copy.deepcopy(self.fixture)
        manifest["data_boundary"]["source_contains_personal_data"] = True
        self.assertIn("source_contains_personal_data must be false", validator.validate_manifest(manifest))

    def test_unsafe_entrypoint_path_is_rejected(self):
        manifest = copy.deepcopy(self.fixture)
        manifest["entrypoints"]["scripts"] = ["../../private/config.json"]
        errors = validator.validate_manifest(manifest)
        self.assertTrue(any("unsafe path" in error for error in errors))

    def test_unknown_fields_are_rejected(self):
        manifest = copy.deepcopy(self.fixture)
        manifest["personal_notes"] = "must not be portable"
        self.assertIn("unknown fields: personal_notes", validator.validate_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
