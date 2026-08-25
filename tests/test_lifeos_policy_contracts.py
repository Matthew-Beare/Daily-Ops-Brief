from __future__ import annotations

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
_LEGACY_PATH = Path(__file__).with_name("test_lifeos_policy_contracts_legacy.inc")
_namespace = runpy.run_path(str(_LEGACY_PATH))
_BaseLifeOSPolicyContractTests = _namespace["LifeOSPolicyContractTests"]


class LifeOSPolicyContractTests(_BaseLifeOSPolicyContractTests):
    def test_canonical_source_and_generated_public_channel_have_state_boundary(self) -> None:
        readme = self.text("README.md")
        channels = self.text("distribution/README.md")
        config = json.loads(self.text("distribution/channels.json"))
        license_text = self.text("LICENSE")

        self.assertIn("M.I.R.R.O.R.", readme)
        self.assertIn("holds the durable reflection of reality", readme)
        self.assertIn("MIRROR Intelligence and Reasoning Assistant", readme)
        self.assertIn("MIRA-Personal-Production", readme)
        self.assertIn("all three onboarding repositories are public", readme.lower())
        self.assertIn("starter/START_HERE.md", readme)
        self.assertIn("mutable operational state", readme.lower())
        self.assertIn("Google Sheets", readme)
        self.assertIn("Google Drive", readme)

        self.assertEqual("Matthew-Beare/MIRA-Personal-Production", config["canonical_source"]["repository"])
        self.assertEqual("public", config["canonical_source"]["required_visibility"])
        by_id = {row["channel_id"]: row for row in config["channels"]}
        self.assertEqual("Matthew-Beare/MIRA-Public-Experimental", by_id["public-experimental"]["repository"])
        self.assertEqual("Matthew-Beare/MIRA-Institutional-Experimental", by_id["institutional-experimental"]["repository"])
        self.assertEqual("public", by_id["public-experimental"]["required_visibility"])
        self.assertEqual("public", by_id["institutional-experimental"]["required_visibility"])
        self.assertFalse(by_id["institutional-experimental"]["regulated_data_allowed_in_git"])

        self.assertIn("remote readback", channels)
        self.assertIn("no PHI/PII", channels)
        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted", license_text)

    def test_starter_separates_git_source_from_mutable_state(self) -> None:
        config = json.loads(self.text("starter/config.example.json"))
        state = self.text("starter/STATE_AUTHORITY_MODEL.md")
        self.assertEqual(
            "CURRENT_STRUCTURED_STATE_AUTHORITY_SELECTED_BY_AUTHORITY_REGISTRY",
            config["STATE_STORE"],
        )
        self.assertIn("POSTGRESQL", config["STATE_BACKEND"])
        self.assertIn("provider", state.lower())
        self.assertIn("storage providers are adapters", state.lower())
        self.assertIn("Git is never the default database", state)
        self.assertIn("one canonical authority per data class", state.lower())

    def test_meal_planning_and_appointment_features_use_external_authority(self) -> None:
        meal = self.text("starter/features/meal-planning/FEATURE.md")
        appointment = self.text("starter/features/appointment-reconciliation/FEATURE.md")
        self.assertIn("structured state authority", meal.lower())
        self.assertIn("readback", meal.lower())
        self.assertIn("structured state authority", appointment.lower())
        self.assertIn("official clinic/provider pages", appointment.lower())
        self.assertIn("cache first, research second", appointment.lower())
        self.assertIn("IANA timezone", appointment)
        self.assertIn("read canonical state back", appointment.lower())
        self.assertIn("Text-to-Speech engine", appointment)


del _BaseLifeOSPolicyContractTests
del _namespace
