from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LifeOSPolicyContractTests(unittest.TestCase):
    def text(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_project_bootstrap_is_stable_and_git_indirected(self) -> None:
        project = self.text("project/INSTRUCTIONS.md.tmpl")
        self.assertIn("BOOTSTRAP_CONTRACT_VERSION: 2", project)
        self.assertIn("project/POLICY_FINGERPRINT.txt", project)
        self.assertNotIn("POLICY_SOURCE_FINGERPRINT:", project)

    def test_carrier_retention_includes_usps_and_stays_narrow(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/email-reconciliation.md")
        self.assertIn("90 calendar days", policy)
        self.assertIn("FedEx, UPS, DHL and USPS", policy)
        self.assertIn("carrier-originated FedEx/UPS/DHL/USPS", policy)
        self.assertIn("merchant order confirmation", policy.lower())
        self.assertIn("open return, claim, dispute", policy)
        self.assertNotIn("USPS and any carrier not named above remain retention-only", policy)

    def test_asset_acquisition_requires_global_uuid_dedupe_and_evidence(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/asset-acquisition.md")
        self.assertIn("immutable RFC 4122 UUID", policy)
        self.assertIn("collision-resistant across deployments/family members", policy)
        self.assertIn("serial number", policy)
        self.assertIn("manufacturer/OEM", policy)
        self.assertIn("search existing canonical asset/tool/inventory records", policy)
        self.assertIn("PostgreSQL", policy)

    def test_manual_library_is_durable_queryable_and_asset_linked(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/knowledge-manual-ingestion.md")
        self.assertIn("Manuals & Reference", policy)
        self.assertIn("Knowledge Index", policy)
        self.assertIn("immutable RFC 4122 UUID", policy)
        self.assertIn("canonical Drive link", policy)
        self.assertIn("asset UUID", policy)
        self.assertIn("PostgreSQL", policy)

    def test_emergency_ripcord_is_fail_fast_and_module_scoped(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/failure-ripcord.md")
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        self.assertIn("Default retry budget is one retry after the initial attempt", policy)
        self.assertIn("same external operation fails twice", policy)
        self.assertIn("Stop writes for the affected module", policy)
        self.assertIn("Continue unrelated modules", policy)
        self.assertIn("do not blind-rerun", policy)
        self.assertIn("failure-ripcord.md", skill)
        self.assertIn("never create hidden retry jobs", skill)

    def test_calendar_projection_updates_in_place(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/calendar-projection.md")
        self.assertIn("Google Calendar event ID", policy)
        self.assertIn("update the linked event in place", policy)
        self.assertIn("order delivery dates/windows", policy)
        self.assertIn("Inviting other people", policy)

    def test_terminal_paid_miles_are_symmetric_and_historical_import_is_pair_only(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        maintenance = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        self.assertIn("Paid terminal mileage is symmetric", skill)
        self.assertIn("unique canonical terminal pairs", skill)
        self.assertIn("do not manufacture hundreds of historical `Trips`", skill)
        self.assertIn("same paid-mile value", maintenance)

    def test_starter_guides_nontechnical_users_auto_versions_and_fails_fast(self) -> None:
        guide = self.text("starter/START_HERE.md")
        deps = self.text("starter/DEPENDENCIES.md")
        self.assertIn("non-technical user", guide)
        self.assertIn("exactly what to click", guide)
        self.assertIn("automatically update validation, commit, and push", guide)
        self.assertIn("Emergency Ripcord", guide)
        self.assertIn("same operation fails twice", guide)
        self.assertIn("GitHub side", deps)
        self.assertIn("ChatGPT side", deps)


if __name__ == "__main__":
    unittest.main()
