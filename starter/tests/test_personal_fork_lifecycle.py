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

    def test_first_boot_is_fork_first_and_versions_initial_configuration(self) -> None:
        guide = self.text("START_HERE.md")
        lifecycle = self.text("PERSONAL_FORK_LIFECYCLE.md")
        versioning = self.text("VERSIONING.md")
        for surface in (guide, lifecycle, versioning):
            self.assertIn("fork", surface.lower())
            self.assertIn("commit", surface.lower())
            self.assertIn("upstream", surface.lower())
        self.assertIn("first-boot checkpoint", lifecycle.lower())
        self.assertIn("read back", lifecycle.lower())
        self.assertIn("experimental", versioning)
        self.assertIn("feature/*", versioning)

    def test_personal_feature_sharing_is_opt_in_and_sanitized(self) -> None:
        phrase = "Do you want to make this feature available to other people?"
        guide = self.text("START_HERE.md")
        lifecycle = self.text("PERSONAL_FORK_LIFECYCLE.md")
        shared = self.text("SHARED_FEATURE_WORKFLOW.md")
        catalog = self.text("MODULE_CATALOG.md")
        for surface in (guide, lifecycle, shared, catalog):
            self.assertIn(phrase, surface)
        self.assertIn("synthetic fixtures", shared.lower())
        self.assertIn("never publish", guide.lower())
        self.assertIn("publication authority", shared.lower())

    def test_capability_discovery_precedes_redundant_connection_prompts(self) -> None:
        discovery = self.text("CAPABILITY_DISCOVERY.md")
        deps = self.text("DEPENDENCIES.md")
        interview = self.text("LIFE_INTERVIEW.md")
        self.assertIn("Current conversation", discovery)
        self.assertIn("File Library", discovery)
        self.assertIn("Connected apps/tools/connectors", discovery)
        self.assertIn("Available plugins/apps", discovery)
        self.assertIn("Do not claim global access to arbitrary old ChatGPT conversations", discovery)
        self.assertIn("Before asking the user to connect anything", deps)
        self.assertIn("fitness/wearable", interview.lower())

    def test_meal_planning_is_first_class_and_state_separated(self) -> None:
        guide = self.text("START_HERE.md")
        interview = self.text("LIFE_INTERVIEW.md")
        catalog = self.text("MODULE_CATALOG.md")
        feature = self.text("features/meal-planning/FEATURE.md")
        manifest = self.manifest("meal-planning")
        for surface in (guide, interview, catalog, feature):
            self.assertIn("meal planning", surface.lower())
        self.assertIn("shopping intent is not purchase history", feature.lower())
        self.assertFalse(manifest["data_boundary"]["source_contains_personal_data"])
        self.assertEqual(manifest["data_boundary"]["runtime_state"], "external-authority")

    def test_appointment_email_calendar_transaction_is_verified(self) -> None:
        interview = self.text("LIFE_INTERVIEW.md")
        catalog = self.text("MODULE_CATALOG.md")
        feature = self.text("features/appointment-reconciliation/FEATURE.md")
        manifest = self.manifest("appointment-reconciliation")
        for phrase in (
            "read the event back",
            "event ID",
            "reminder",
            "source linkage",
            "update",
        ):
            self.assertIn(phrase.lower(), feature.lower())
        self.assertIn("appointment email", interview.lower())
        self.assertIn("one ChatGPT automation per appointment", catalog)
        self.assertIn("minimum calendar detail", feature.lower())
        self.assertFalse(manifest["data_boundary"]["source_contains_personal_data"])

    def test_optional_dependency_failures_are_module_scoped(self) -> None:
        discovery = self.text("CAPABILITY_DISCOVERY.md")
        deps = self.text("DEPENDENCIES.md")
        appointment = self.text("features/appointment-reconciliation/FEATURE.md")
        meal = self.text("features/meal-planning/FEATURE.md")
        self.assertIn("blocks only the dependent module", deps)
        self.assertIn("Failure of one adapter must not disable basic meal planning", meal)
        self.assertIn("Each adapter fails independently", appointment)
        self.assertIn("one canonical authority per data class", discovery)


if __name__ == "__main__":
    unittest.main()
