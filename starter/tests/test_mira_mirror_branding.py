from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


class MiraMirrorBrandingTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_brand_contract_is_explicit(self) -> None:
        branding = (REPO / "docs/BRANDING.md").read_text(encoding="utf-8")
        self.assertIn("MIRROR is the reality layer. MIRA is the intelligence layer.", branding)
        self.assertIn("MIRA is the assistant. MIRROR is the system.", branding)
        self.assertIn("MIRA, MIRROR on the wall", branding)

    def test_default_front_door_is_boomer_safe(self) -> None:
        flow = json.loads(self.text("install-flow.json"))
        self.assertEqual("MIRROR", flow["brand_product_name"])
        self.assertEqual("MIRA", flow["assistant_default_name"])
        self.assertEqual("QUICK_START.md", flow["entry_document"])
        self.assertEqual("MIRROR", flow["first_boot_defaults"]["system_name"])
        self.assertEqual("MIRA", flow["first_boot_defaults"]["assistant_name"])
        self.assertFalse(flow["first_boot_defaults"]["ask_system_name_on_first_boot"])
        guide = self.text("QUICK_START.md")
        self.assertIn("Git is version history.", guide)
        self.assertIn("GitHub is the website", guide)
        self.assertIn("No Command Prompt", guide)
        self.assertNotIn("git clone ", guide.lower())
        self.assertNotIn("gh repo create", guide.lower())

    def test_portable_skill_keeps_compatibility_id_but_uses_mira(self) -> None:
        skill = self.text("life-planner/SKILL.md")
        agent = self.text("life-planner/agents/openai.yaml")
        self.assertIn("name: life-planner", skill)
        self.assertIn("MIRROR is the reality layer. MIRA is the intelligence layer.", skill)
        self.assertIn("ask the user to invent a system name: **false**", skill)
        self.assertIn('display_name: "MIRA | MIRROR"', agent)

    def test_release_channels_share_one_code_line(self) -> None:
        config = json.loads((REPO / "distribution/channels.json").read_text(encoding="utf-8"))
        self.assertEqual("MIRROR", config["brand_product_name"])
        self.assertEqual("MIRA", config["assistant_default_name"])
        self.assertEqual("Matthew-Beare/MIRROR-Personal-Production", config["canonical_source"]["brand_repository"])
        channels = {row["channel_id"]: row for row in config["channels"]}
        self.assertEqual("Matthew-Beare/MIRROR-Personal-Experimental", channels["public-experimental"]["brand_repository"])
        self.assertEqual("Matthew-Beare/MIRROR-Institutional-Experimental", channels["institutional-experimental"]["brand_repository"])
        shared = config["shared_code_contract"]
        self.assertTrue(shared["same_portable_source_revision_required"])
        self.assertFalse(shared["channel_specific_feature_code_allowed"])


if __name__ == "__main__":
    unittest.main()
