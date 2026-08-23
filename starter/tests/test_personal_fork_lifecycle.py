from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PersonalForkLifecycleTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def manifest(self, feature_id: str) -> dict:
        return json.loads(self.text(f"features/{feature_id}/feature.json"))

    def test_first_boot_uses_private_git_for_personal_state_and_lineage(self) -> None:
        guide = self.text("START_HERE.md")
        lifecycle = self.text("PERSONAL_FORK_LIFECYCLE.md")
        versioning = self.text("VERSIONING.md")
        state = self.text("GIT_STATE_MODEL.md")
        for surface in (guide, lifecycle, versioning, state):
            self.assertIn("private", surface.lower())
            self.assertIn("git", surface.lower())
            self.assertIn("state", surface.lower())
            self.assertIn("upstream", surface.lower())
        self.assertIn("canonical source of truth", lifecycle.lower())
        self.assertIn("first-boot state/config checkpoint", lifecycle.lower())
        self.assertIn("read back", lifecycle.lower())
        self.assertIn("public github fork", versioning.lower())
        self.assertIn("code only", versioning.lower())
        self.assertIn("experimental", versioning)
        self.assertIn("feature/*", versioning)

    def test_git_state_transactions_are_append_validate_push_readback(self) -> None:
        state = self.text("GIT_STATE_MODEL.md")
        lifecycle = self.text("PERSONAL_FORK_LIFECYCLE.md")
        for phrase in (
            "immutable event",
            "snapshot",
            "push by fast-forward only",
            "read back",
            "remote branch moved",
            "Never force-push",
        ):
            self.assertIn(phrase.lower(), state.lower())
        self.assertIn("each coherent state-changing user action", lifecycle.lower())
        self.assertIn("fast-forward only", lifecycle.lower())

    def test_personal_feature_sharing_is_opt_in_and_excludes_state(self) -> None:
        phrase = "Do you want to make this feature available to other people?"
        guide = self.text("START_HERE.md")
        lifecycle = self.text("PERSONAL_FORK_LIFECYCLE.md")
        shared = self.text("SHARED_FEATURE_WORKFLOW.md")
        catalog = self.text("MODULE_CATALOG.md")
        for surface in (guide, lifecycle, shared, catalog):
            self.assertIn(phrase, surface)
        self.assertIn("synthetic fixtures", shared.lower())
        self.assertIn("state/", shared)
        self.assertIn("never publish", guide.lower())
        self.assertIn("publication authority", shared.lower())

    def test_capability_discovery_treats_connectors_as_adapters(self) -> None:
        discovery = self.text("CAPABILITY_DISCOVERY.md")
        deps = self.text("DEPENDENCIES.md")
        interview = self.text("LIFE_INTERVIEW.md")
        self.assertIn("Private deployment Git", discovery)
        self.assertIn("Current conversation", discovery)
        self.assertIn("File Library", discovery)
        self.assertIn("Connected apps/tools/connectors", discovery)
        self.assertIn("Available plugins/apps", discovery)
        self.assertIn("Do not claim global access to arbitrary old ChatGPT conversations", discovery)
        self.assertIn("Before asking the user to connect anything", deps)
        self.assertIn("fitness/wearable", interview.lower())
        self.assertIn("optional evidence", interview.lower())
        self.assertIn("one canonical personal-state authority: private Git", discovery)

    def test_meal_planning_is_first_class_and_git_backed(self) -> None:
        guide = self.text("START_HERE.md")
        interview = self.text("LIFE_INTERVIEW.md")
        catalog = self.text("MODULE_CATALOG.md")
        feature = self.text("features/meal-planning/FEATURE.md")
        manifest = self.manifest("meal-planning")
        for surface in (guide, interview, catalog, feature):
            self.assertIn("meal planning", surface.lower())
        self.assertIn("Do you want help with meal planning?", guide)
        self.assertIn("shopping intent is not purchase history", feature.lower())
        self.assertIn("private Git", feature)
        self.assertFalse(manifest["data_boundary"]["source_contains_personal_data"])
        self.assertEqual(manifest["data_boundary"]["runtime_state"], "deployment-local")

    def test_appointment_email_calendar_git_transaction_is_verified(self) -> None:
        interview = self.text("LIFE_INTERVIEW.md")
        catalog = self.text("MODULE_CATALOG.md")
        feature = self.text("features/appointment-reconciliation/FEATURE.md")
        manifest = self.manifest("appointment-reconciliation")
        for phrase in (
            "read the Calendar event back",
            "event ID",
            "reminder",
            "source linkage",
            "private Git",
            "read the Git state back",
        ):
            self.assertIn(phrase.lower(), feature.lower())
        self.assertIn("appointment email", interview.lower())
        self.assertIn("one ChatGPT automation per appointment", catalog)
        self.assertIn("minimum detail", feature.lower())
        self.assertEqual(manifest["data_boundary"]["runtime_state"], "deployment-local")
        self.assertFalse(manifest["data_boundary"]["source_contains_personal_data"])

    def test_optional_dependency_failures_are_module_scoped(self) -> None:
        discovery = self.text("CAPABILITY_DISCOVERY.md")
        deps = self.text("DEPENDENCIES.md")
        appointment = self.text("features/appointment-reconciliation/FEATURE.md")
        meal = self.text("features/meal-planning/FEATURE.md")
        self.assertIn("blocks only the dependent", deps)
        self.assertIn("Failure of one adapter must not disable basic meal planning", meal)
        self.assertIn("Each adapter fails independently", appointment)
        self.assertIn("one canonical personal-state authority: private Git", discovery)

    def test_interview_discovers_retirement_hobbies_meals_and_medical_event_organization(self) -> None:
        questions = json.loads(self.text("questions.json"))
        rows = [q for section in questions["sections"] for q in section["questions"]]
        ids = {q["id"] for q in rows}
        for required in (
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
        self.assertGreaterEqual(questions["version"], 5)


if __name__ == "__main__":
    unittest.main()
