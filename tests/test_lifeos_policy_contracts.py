from __future__ import annotations

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
        config = __import__("json").loads(self.text("distribution/channels.json"))
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


del _BaseLifeOSPolicyContractTests
del _namespace
