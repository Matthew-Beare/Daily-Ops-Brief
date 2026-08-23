from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LifeOSPolicyContractTests(unittest.TestCase):
    def text(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_public_upstream_has_license_and_explicit_two_state_models(self) -> None:
        readme = self.text("README.md")
        license_text = self.text("LICENSE")
        self.assertIn("intentionally public", readme)
        self.assertIn("starter/START_HERE.md", readme)
        self.assertIn("Mutable operational state", readme)
        self.assertIn("private Git", readme)
        self.assertIn("reference deployment", readme)
        self.assertIn("public-source audit", readme)
        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted", license_text)

    def test_starter_requires_private_git_for_personal_state(self) -> None:
        guide = self.text("starter/START_HERE.md")
        deps = self.text("starter/DEPENDENCIES.md")
        versioning = self.text("starter/VERSIONING.md")
        template = self.text("starter/INSTRUCTIONS.md.tmpl")
        state = self.text("starter/GIT_STATE_MODEL.md")
        config = json.loads(self.text("starter/config.example.json"))
        for surface in (guide, deps, versioning, template, state):
            self.assertIn("private", surface.lower())
            self.assertIn("git", surface.lower())
            self.assertIn("state", surface.lower())
        self.assertIn("public-source audit", guide.lower())
        self.assertIn("Public GitHub fork path", versioning)
        self.assertIn("code only", versioning.lower())
        self.assertIn("{{REPOSITORY_VISIBILITY}}", template)
        self.assertEqual(config["STATE_STORE"], "PRIVATE_GIT_REPOSITORY/state")
        self.assertEqual(config["REPOSITORY_VISIBILITY"], "PRIVATE_REQUIRED_WHEN_PERSONAL_STATE_IS_ENABLED")
        self.assertIn("IMMUTABLE_EVENTS_PLUS_DERIVED_SNAPSHOTS", config["GIT_STATE_MODEL"])

    def test_git_state_model_is_transactional_and_share_safe(self) -> None:
        state = self.text("starter/GIT_STATE_MODEL.md")
        shared = self.text("starter/SHARED_FEATURE_WORKFLOW.md")
        for phrase in (
            "canonical personal state authority",
            "Event files are immutable",
            "push by fast-forward only",
            "read back",
            "Never force-push",
            "state/",
        ):
            self.assertIn(phrase.lower(), state.lower())
        self.assertIn("exclude the entire private `state/` surface", shared)
        self.assertIn("synthetic fixtures", shared.lower())

    def test_public_source_audit_and_ci_are_release_gates(self) -> None:
        audit = self.text("scripts/audit_public_source.py")
        ci = self.text(".github/workflows/ci.yml")
        gitignore = self.text(".gitignore")
        self.assertIn("audit_history", audit)
        self.assertIn("CARD_CANDIDATE", audit)
        self.assertIn("BLOCKED_FILENAMES", audit)
        self.assertIn("SCAN_EXEMPT_PATHS", audit)
        self.assertIn("fetch-depth: 0", ci)
        self.assertIn("scripts/audit_public_source.py . --history", ci)
        self.assertIn("scripts/audit_starter_privacy.py starter", ci)
        self.assertIn("scripts/validate_repo.py .", ci)
        self.assertIn(".env", gitignore)
        self.assertIn("*.sqlite", gitignore)

    def test_project_bootstrap_is_stable_and_git_indirected(self) -> None:
        project = self.text("project/INSTRUCTIONS.md.tmpl")
        self.assertIn("BOOTSTRAP_CONTRACT_VERSION: 2", project)
        self.assertIn("project/POLICY_FINGERPRINT.txt", project)
        self.assertNotIn("POLICY_SOURCE_FINGERPRINT:", project)

    def test_scheduler_uses_evidence_chain_and_entry_run_log(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        maintenance = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        brief = self.text("skill/ops-brief-policy/references/brief-run.md")
        docs = self.text("docs/automation-contracts.md")
        deps = self.text("starter/DEPENDENCIES.md")
        interview = self.text("starter/LIFE_INTERVIEW.md")
        for surface in (skill, maintenance, docs, deps, interview):
            lower = surface.lower()
            self.assertIn("notification", lower)
            self.assertIn("duplicate", lower)
            self.assertTrue(
                any(term in lower for term in ("actual firing", "actual scheduled firing", "observed firing", "observed execution")),
                "scheduler surface lacks observed execution evidence",
            )
            self.assertTrue(
                "provider contract" in lower or "provider/tool contract" in lower,
                "scheduler surface does not condition provider metadata on documented semantics",
            )
        self.assertIn("default_timezone", skill)
        self.assertIn("default_timezone", maintenance)
        self.assertIn("first external", skill.lower())
        self.assertIn("`Running`", skill)
        self.assertIn("Before Gmail", brief)
        self.assertIn("`Running`", brief)

    def test_pants_circuit_breaker_is_fail_fast_and_module_scoped(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        self.assertIn("# Pants Filling With Shit Report", policy)
        self.assertIn("Retry is **not mandatory**", policy)
        self.assertIn("same external operation fails twice", policy)
        self.assertIn("Stop writes for the affected module", policy)
        self.assertIn("Continue unrelated modules", policy)
        self.assertIn("never blind-rerun", policy)
        self.assertIn("never create hidden retry jobs", skill)

    def test_terminal_paid_miles_are_symmetric_in_reference_deployment(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        maintenance = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        brief = self.text("skill/ops-brief-policy/references/brief-run.md")
        compatibility = self.text("policy/ops-brief-policy.yaml")
        platform = self.text("docs/data-platform-grafana.md")
        self.assertIn("Paid terminal mileage is symmetric", skill)
        self.assertIn("same paid-mile value", maintenance)
        self.assertIn("symmetric by canonical terminal pair", brief)
        self.assertIn("terminal_paid_miles_symmetric_by_pair: true", compatibility)
        self.assertIn("terminal_paid_miles_directional: false", compatibility)
        self.assertNotIn("never mirrors automatically", platform.lower())

    def test_carrier_retention_is_narrow_and_includes_usps(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/email-reconciliation.md")
        self.assertIn("90 calendar days", policy)
        self.assertIn("FedEx, UPS, DHL and USPS", policy)
        self.assertIn("carrier-originated FedEx/UPS/DHL/USPS", policy)
        self.assertIn("merchant order confirmation", policy.lower())
        self.assertIn("open return, claim, dispute", policy)

    def test_asset_and_knowledge_identity_are_immutable_uuid_based(self) -> None:
        asset = self.text("skill/ops-brief-policy/references/asset-acquisition.md")
        manual = self.text("skill/ops-brief-policy/references/knowledge-manual-ingestion.md")
        schema = self.text("docs/household-financial-reconciliation.md")
        self.assertIn("immutable RFC 4122 UUID", asset)
        self.assertIn("collision-resistant across deployments/family members", asset)
        self.assertIn("immutable RFC 4122 UUID", manual)
        self.assertIn("Knowledge Index", manual)
        self.assertIn("Entity UUID", schema)
        self.assertIn("Friendly", schema)

    def test_calendar_projection_updates_in_place_without_task_fanout(self) -> None:
        calendar = self.text("skill/ops-brief-policy/references/calendar-projection.md")
        design = self.text("docs/automation-design.md")
        self.assertIn("Google Calendar event ID", calendar)
        self.assertIn("update the linked event in place", calendar)
        self.assertIn("order delivery dates/windows", calendar)
        self.assertIn("not a per-order automation", design.lower())
        self.assertIn("never creates per-order scheduled tasks", design.lower())

    def test_shopping_procurement_is_active_list_not_purchase_history(self) -> None:
        skill = self.text("skill/ops-brief-policy/SKILL.md")
        receipt = self.text("skill/ops-brief-policy/references/receipt-ingestion.md")
        catalog = self.text("starter/MODULE_CATALOG.md")
        for surface in (skill, receipt, catalog):
            self.assertIn("active shopping list", surface)
            self.assertIn("remove the fulfilled shopping row", surface)
        self.assertIn("explicit owner", receipt)
        self.assertIn("separate reconciliation task", receipt)
        self.assertIn("Purchased` tombstone", receipt)
        self.assertIn("cancellation with no supported replacement", receipt)

    def test_payment_and_reimbursement_semantics_remain_separate(self) -> None:
        payment = self.text("skill/ops-brief-policy/references/payment-reconciliation.md")
        reimbursement = self.text("skill/ops-brief-policy/references/household-reimbursement.md")
        self.assertIn("Awaiting Settlement", payment)
        self.assertIn("Overcharged", payment)
        self.assertIn("unmatched", payment.lower())
        self.assertIn("A reimbursement is not a merchant refund", reimbursement)
        self.assertIn("Net Household Cost", reimbursement)

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

    def test_starter_is_bounded_nontechnical_deep_and_discovery_driven(self) -> None:
        guide = self.text("starter/START_HERE.md")
        questions = json.loads(self.text("starter/questions.json"))
        rows = [q for section in questions["sections"] for q in section["questions"]]
        ids = {q["id"] for q in rows}
        self.assertIn("non-technical user", guide)
        self.assertIn("Minimum Useful Setup", guide)
        self.assertIn("Start now by asking only the four kickoff questions", guide)
        self.assertIn("mark HOME/ROAD bypassed", guide)
        self.assertIn("driving/trucking", guide.lower())
        self.assertIn("Do you want help with meal planning?", guide)
        self.assertLess(len(guide), 12000)
        self.assertGreaterEqual(len(rows), 100)
        self.assertGreaterEqual(questions["version"], 5)
        for required in (
            "works_away_from_home",
            "accountability_domains",
            "routine_progression",
            "education_active",
            "study_home_away",
            "study_next_action_rule",
            "scheduler_timezone_integrity",
            "repository_visibility",
            "public_source_policy",
            "employment_status",
            "retired_support",
            "hiking_outdoors",
            "vacation_planning",
            "meal_planning_help",
            "existing_meal_plans",
            "fitness_wearable",
            "medical_event_tracking",
            "appointment_email_auto_update",
            "git_state_commit_policy",
        ):
            self.assertIn(required, ids)

    def test_reference_contamination_blocklist_is_substantial(self) -> None:
        markers = [
            line.strip()
            for line in self.text("privacy/starter-blocklist.txt").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertGreaterEqual(len(markers), 15)
        self.assertIn("America/New_York", markers)
        self.assertTrue(any("Subaru" in marker for marker in markers))


if __name__ == "__main__":
    unittest.main()
