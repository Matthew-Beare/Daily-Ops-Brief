from __future__ import annotations

import json
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

    def test_pants_filling_with_shit_report_is_fail_fast_and_module_scoped(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        self.assertIn("# Pants Filling With Shit Report", policy)
        self.assertIn("Default budget is the initial attempt plus at most one retry", policy)
        self.assertIn("Retry is **not mandatory**", policy)
        self.assertIn("same external operation fails twice", policy)
        self.assertIn("Stop writes for the affected module", policy)
        self.assertIn("Continue unrelated modules", policy)
        self.assertIn("never blind-rerun", policy)
        self.assertIn("pants-filling-with-shit-report.md", skill)
        self.assertIn("never create hidden retry jobs", skill)

    def test_scheduler_timezone_requires_provider_execution_readback(self) -> None:
        maintenance = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        pants = self.text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
        docs = self.text("docs/automation-contracts.md")
        deps = self.text("starter/DEPENDENCIES.md")
        for text in (maintenance, pants, docs, deps):
            self.assertIn("stored/default/execution timezone", text)
        self.assertIn("travel/device timezone", maintenance)
        self.assertIn("Do **not** report a timezone repair successful from VEVENT text alone", maintenance)
        self.assertIn("subsequent actual run/Run Log timestamp", pants)
        self.assertIn("fail closed", deps)

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
        self.assertIn("A reusable route pair may be learned even when the user does not want a current Trip occurrence created", maintenance)

    def test_shopping_procurement_is_active_list_not_purchase_history(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        receipt = self.text("skill/ops-brief-policy/references/receipt-ingestion.md")
        catalog = self.text("starter/MODULE_CATALOG.md")
        for text in (skill, receipt, catalog):
            self.assertIn("active shopping list", text)
            self.assertIn("remove the fulfilled shopping row", text)
        self.assertIn("explicit owner", receipt)
        self.assertIn("separate reconciliation task", receipt)
        self.assertIn("Purchased` tombstone", receipt)
        self.assertIn("cancellation with no supported replacement", receipt)

    def test_life_planning_supports_accountability_study_and_context_variants(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/life-planning-accountability.md")
        interview = self.text("starter/LIFE_INTERVIEW.md")
        catalog = self.text("starter/MODULE_CATALOG.md")
        self.assertIn("Routine accountability", policy)
        self.assertIn("Exercise / fitness organization", policy)
        self.assertIn("School / study workflow", policy)
        self.assertIn("Next-action planner", policy)
        self.assertIn("Do you regularly work away from home", interview)
        self.assertIn("minimum viable version", interview)
        self.assertIn("home versus away/on the road", interview)
        self.assertIn("Personal accountability and routines", catalog)
        self.assertIn("Education and study coach", catalog)

    def test_starter_guides_nontechnical_users_auto_versions_and_fails_fast(self) -> None:
        guide = self.text("starter/START_HERE.md")
        deps = self.text("starter/DEPENDENCIES.md")
        self.assertIn("non-technical user", guide)
        self.assertIn("exactly what to click", guide)
        self.assertIn("automatically update validation, commit, and push", guide)
        self.assertIn("Pants Filling With Shit Report", guide)
        self.assertIn("same operation fails twice", guide)
        self.assertIn("GitHub side", deps)
        self.assertIn("ChatGPT side", deps)
        self.assertIn("Do I ever work away from home or sleep away for work?", guide)
        self.assertIn("whole-life interview", guide)

    def test_starter_questions_have_adaptive_whole_life_depth(self) -> None:
        questions = json.loads(self.text("starter/questions.json"))
        rows = [q for section in questions["sections"] for q in section["questions"]]
        ids = {q["id"] for q in rows}
        for required in (
            "works_away_from_home",
            "accountability_domains",
            "routine_progression",
            "education_active",
            "study_home_away",
            "study_next_action_rule",
            "scheduler_timezone_integrity",
        ):
            self.assertIn(required, ids)
        self.assertGreaterEqual(len(rows), 80)


if __name__ == "__main__":
    unittest.main()
