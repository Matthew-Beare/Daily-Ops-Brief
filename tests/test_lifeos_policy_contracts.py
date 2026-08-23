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

    def test_asset_and_manual_identity_use_immutable_uuid(self) -> None:
        asset = self.text("skill/ops-brief-policy/references/asset-acquisition.md")
        manual = self.text("skill/ops-brief-policy/references/knowledge-manual-ingestion.md")
        schema = self.text("docs/household-financial-reconciliation.md")
        self.assertIn("immutable RFC 4122 UUID", asset)
        self.assertIn("collision-resistant across deployments/family members", asset)
        self.assertIn("immutable RFC 4122 UUID", manual)
        self.assertIn("canonical Drive link", manual)
        self.assertIn("Entity UUID", schema)
        self.assertIn("Friendly", schema)

    def test_pants_filling_with_shit_report_is_fail_fast_and_module_scoped(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        self.assertIn("# Pants Filling With Shit Report", policy)
        self.assertIn("Retry is **not mandatory**", policy)
        self.assertIn("same external operation fails twice", policy)
        self.assertIn("Stop writes for the affected module", policy)
        self.assertIn("Continue unrelated modules", policy)
        self.assertIn("never blind-rerun", policy)
        self.assertIn("never create hidden retry jobs", skill)

    def test_scheduler_integrity_uses_evidence_chain_not_travel_metadata(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        maintenance = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        docs = self.text("docs/automation-contracts.md")
        deps = self.text("starter/DEPENDENCIES.md")
        first_boot = self.text("starter/START_HERE.md")
        for surface in (skill, maintenance, docs, deps, first_boot):
            lowered = surface.lower()
            self.assertIn("notification", lowered)
            self.assertIn("duplicate", lowered)
            self.assertIn("actual firing", lowered)
            self.assertIn("provider contract", lowered)
        self.assertIn("default_timezone", skill)
        self.assertIn("default_timezone", docs)
        self.assertIn("default_timezone", deps)
        self.assertIn("travel/device", skill)
        self.assertNotIn("provider stored/default/execution timezone equals", first_boot.lower())

    def test_entered_scheduled_brief_logs_running_before_downstream_mutations(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        brief = self.text("skill/ops-brief-policy/references/brief-run.md")
        self.assertIn("first external state mutation", skill)
        self.assertIn("`Running`", skill)
        self.assertIn("Before Gmail", brief)
        self.assertIn("`Running`", brief)
        self.assertIn("same", brief.lower())

    def test_calendar_projection_updates_in_place_without_per_order_automation(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/calendar-projection.md")
        design = self.text("docs/automation-design.md")
        self.assertIn("Google Calendar event ID", policy)
        self.assertIn("update the linked event in place", policy)
        self.assertIn("order delivery dates/windows", policy)
        self.assertIn("not a per-order automation", design.lower())
        self.assertIn("never creates per-order scheduled tasks", design.lower())

    def test_terminal_paid_miles_are_symmetric_everywhere(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        maintenance = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        brief = self.text("skill/ops-brief-policy/references/brief-run.md")
        runtime = self.text("skill/ops-brief-policy/scripts/ops_policy_runtime.py")
        compat = self.text("policy/ops-brief-policy.yaml")
        platform = self.text("docs/data-platform-grafana.md")
        self.assertIn("Paid terminal mileage is symmetric", skill)
        self.assertIn("same paid-mile value", maintenance)
        self.assertIn("symmetric by canonical terminal pair", brief)
        self.assertIn("standing policy is symmetric by terminal pair", runtime)
        self.assertIn("terminal_paid_miles_symmetric_by_pair: true", compat)
        self.assertIn("terminal_paid_miles_directional: false", compat)
        self.assertIn("for the current deployment it is symmetric", platform)
        self.assertNotIn("never mirrors automatically", platform.lower())
        self.assertNotIn("Directional terminal paid-mile fields are learned evidence only", brief)

    def test_historical_audit_does_not_copy_mutable_runtime_state(self) -> None:
        audit = self.text("docs/feature-audit-2026-08-22.md")
        self.assertIn("Status: superseded", audit)
        self.assertNotIn("TRIP-", audit)
        self.assertNotIn("MILE-", audit)
        self.assertIn("live canonical", audit.lower())

    def test_repository_privacy_is_verified_from_provider_state(self) -> None:
        readme = self.text("README.md")
        deps = self.text("starter/DEPENDENCIES.md")
        template = self.text("starter/INSTRUCTIONS.md.tmpl")
        self.assertIn("must be private", readme)
        self.assertIn("provider metadata", readme)
        self.assertNotIn("This repository is private", readme)
        self.assertIn("provider metadata", deps)
        self.assertIn("must actually be private", template)

    def test_starter_has_real_pre_release_installation_path(self) -> None:
        versioning = self.text("starter/VERSIONING.md")
        self.assertIn("standalone", versioning.lower())
        self.assertIn("brand-new private", versioning.lower())
        self.assertIn("pinned", versioning.lower())
        self.assertIn("snapshot", versioning.lower())
        self.assertTrue("do not fork" in versioning.lower() or "never fork" in versioning.lower())

    def test_shopping_procurement_is_active_list_not_purchase_history(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        receipt = self.text("skill/ops-brief-policy/references/receipt-ingestion.md")
        catalog = self.text("starter/MODULE_CATALOG.md")
        for text in (skill, receipt, catalog):
            self.assertIn("active shopping list", text)
            self.assertIn("remove the fulfilled shopping row", text)
        self.assertIn("explicit owner", receipt)
        self.assertIn("separate reconciliation task", receipt)

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
        scheduler_prompts = " ".join(q["prompt"] for q in rows if "scheduler" in q["id"] or "scheduled" in q["id"])
        self.assertIn("notification", scheduler_prompts.lower())
        self.assertIn("actual", scheduler_prompts.lower())


if __name__ == "__main__":
    unittest.main()