from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "feature_manifest_validator", ROOT / "tools" / "validate_feature_manifest.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(VALIDATOR)


class FeatureIsolationContractTests(unittest.TestCase):
    def load(self, feature_id: str) -> dict:
        return json.loads((ROOT / "features" / feature_id / "feature.json").read_text(encoding="utf-8"))

    def test_live_features_use_manifest_v2_runtime_isolation_contract(self) -> None:
        for feature_id in ("meal-planning", "appointment-reconciliation"):
            manifest = self.load(feature_id)
            self.assertEqual(manifest["manifest_version"], 2)
            runtime = manifest["runtime_contract"]
            self.assertTrue(runtime["failure_domain"])
            self.assertIn("structured-state-authority", runtime["required_capabilities"])
            self.assertEqual(runtime["on_required_failure"], "block-module-only")
            self.assertEqual(runtime["on_optional_failure"], "degrade-capability-and-continue")
            self.assertTrue(runtime["idempotency_scope"])
            self.assertTrue(runtime["canonical_state_classes"])

        meal = self.load("meal-planning")["runtime_contract"]
        appointment = self.load("appointment-reconciliation")["runtime_contract"]
        self.assertEqual(meal["cross_module_writes"], ["shopping-procurement:upsert-meal-plan-intent"])
        self.assertEqual(appointment["cross_module_writes"], [])

    def test_required_and_optional_capabilities_cannot_overlap(self) -> None:
        manifest = self.load("meal-planning")
        manifest["runtime_contract"]["optional_capabilities"].append("structured-state-authority")
        errors = VALIDATOR.validate_manifest(manifest)
        self.assertTrue(any("both required and optional" in error for error in errors))

    def test_conditional_capability_must_be_declared_optional(self) -> None:
        manifest = self.load("appointment-reconciliation")
        manifest["runtime_contract"]["conditional_capabilities"]["undeclared-adapter"] = "required when selected"
        errors = VALIDATOR.validate_manifest(manifest)
        self.assertTrue(any("conditional capabilities" in error for error in errors))

    def test_self_dependency_is_rejected(self) -> None:
        manifest = self.load("meal-planning")
        manifest["dependencies"] = [{"id": "meal-planning", "version_range": ">=0.1.0"}]
        errors = VALIDATOR.validate_manifest(manifest)
        self.assertIn("feature cannot depend on itself", errors)

    def test_dependency_graph_rejects_cycle(self) -> None:
        meal = self.load("meal-planning")
        appointment = self.load("appointment-reconciliation")
        meal["dependencies"] = [{"id": "appointment-reconciliation", "version_range": ">=0.1.0"}]
        appointment["dependencies"] = [{"id": "meal-planning", "version_range": ">=0.1.0"}]
        errors = VALIDATOR.validate_dependency_graph(
            [(Path("meal/feature.json"), meal), (Path("appointment/feature.json"), appointment)]
        )
        self.assertTrue(any("dependency cycle" in error for error in errors))

    def test_dependency_graph_rejects_missing_bundled_feature(self) -> None:
        meal = self.load("meal-planning")
        meal["dependencies"] = [{"id": "missing-feature", "version_range": ">=0.1.0"}]
        errors = VALIDATOR.validate_dependency_graph([(Path("meal/feature.json"), meal)])
        self.assertIn("feature meal-planning depends on missing bundled feature missing-feature", errors)

    def test_file_check_detects_missing_live_entrypoint(self) -> None:
        manifest = self.load("meal-planning")
        manifest["entrypoints"]["scripts"] = ["scripts/does-not-exist.py"]
        with tempfile.TemporaryDirectory() as tempdir:
            errors = VALIDATOR.validate_manifest(manifest, Path(tempdir))
        self.assertTrue(any("references missing file" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
