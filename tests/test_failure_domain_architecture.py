from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FailureDomainArchitectureTests(unittest.TestCase):
    def text(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def manifest(self, feature_id: str) -> dict:
        return json.loads(self.text(f"starter/features/{feature_id}/feature.json"))

    def test_state_model_separates_canonical_identity_from_physical_failure_domains(self) -> None:
        state = self.text("starter/STATE_AUTHORITY_MODEL.md")
        self.assertIn("One canonical authority per data class does not mean one giant workbook", state)
        self.assertIn("Recommended production resource boundaries", state)
        self.assertIn("Core Ops authority", state)
        self.assertIn("Commerce authority", state)
        self.assertIn("Mileage/Pay authority", state)
        self.assertIn("provider-wide outage", state.lower())
        self.assertIn("Recovery snapshots", state)
        self.assertIn("never a second writable master", state)

    def test_dependency_contract_is_machine_readable_and_acyclic_by_policy(self) -> None:
        deps = self.text("starter/DEPENDENCIES.md")
        self.assertIn("manifest contract v2", deps)
        self.assertIn("failure_domain", deps)
        self.assertIn("required_capabilities", deps)
        self.assertIn("optional_capabilities", deps)
        self.assertIn("cross_module_writes", deps)
        self.assertIn("acyclic graph", deps)
        self.assertIn("block-module-only", deps)
        self.assertIn("degrade-capability-and-continue", deps)

    def test_ci_checks_declared_live_feature_files(self) -> None:
        ci = self.text(".github/workflows/ci.yml")
        self.assertIn("validate_feature_manifest.py --check-files", ci)

    def test_live_features_have_no_undeclared_cross_module_writes(self) -> None:
        domains: set[str] = set()
        for feature_id in ("meal-planning", "appointment-reconciliation"):
            manifest = self.manifest(feature_id)
            runtime = manifest["runtime_contract"]
            self.assertEqual(manifest["manifest_version"], 2)
            self.assertEqual(runtime["cross_module_writes"], [])
            self.assertFalse(set(runtime["required_capabilities"]) & set(runtime["optional_capabilities"]))
            self.assertEqual(runtime["on_required_failure"], "block-module-only")
            self.assertEqual(runtime["on_optional_failure"], "degrade-capability-and-continue")
            domains.add(runtime["failure_domain"])
        self.assertEqual(domains, {"meal-planning", "appointments"})

    def test_reference_deployment_has_separate_core_commerce_and_mileage_authorities(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        brief = self.text("skill/ops-brief-policy/references/brief-run.md")
        self.assertIn("Ops Status Register", skill)
        self.assertIn("Mileage & Pay Tracker", skill)
        self.assertIn("Purchase & Receipt Archive", skill)
        self.assertIn("Mileage/pay is section-scoped", brief)
        self.assertIn("If the receipt workbook is unavailable", brief)
        self.assertIn("Calendar is non-authoritative evidence", brief)

    def test_circuit_breaker_continues_unrelated_modules(self) -> None:
        pants = self.text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
        self.assertIn("Stop writes for the affected module", pants)
        self.assertIn("Continue unrelated modules", pants)
        self.assertIn("Never create child/retry automations", pants)


if __name__ == "__main__":
    unittest.main()
