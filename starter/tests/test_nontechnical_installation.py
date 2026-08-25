from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
_LEGACY_PATH = Path(__file__).with_name("test_nontechnical_installation_legacy.inc")
_namespace = runpy.run_path(str(_LEGACY_PATH))
_BaseNontechnicalInstallationTests = _namespace["NontechnicalInstallationTests"]


class NontechnicalInstallationTests(_BaseNontechnicalInstallationTests):
    def test_template_path_creates_private_user_owned_repository(self) -> None:
        flow = self.flow()
        self.assertEqual(5, flow["version"])
        self.assertEqual("Matthew-Beare/MIRA-Public-Experimental", flow["upstream"])
        self.assertEqual("current-public-onboarding-template", flow["upstream_status"])
        self.assertEqual("github-template", flow["copy_method"])
        self.assertEqual("private", flow["default_personal_visibility"])
        self.assertEqual("user", flow["first_repository_creation"]["default_actor"])
        self.assertEqual("github-web", flow["first_repository_creation"]["surface"])
        self.assertIn("repository-creation action", flow["first_repository_creation"]["assistant_creation_allowed_when"])
        self.assertFalse(flow["first_repository_creation"]["include_all_branches"])
        self.assertIn("template_missing", flow["blocked_states"])
        install = self.text("INSTALL.md")
        self.assertIn("MIRA-Public-Experimental/generate", install)
        self.assertIn("/generate", install)

    def test_provider_specific_browser_onboarding_covers_non_google_lanes(self) -> None:
        flow = self.flow()
        self.assertEqual("PROVIDER_ONBOARDING.md", flow["provider_onboarding_document"])
        providers = self.text("PROVIDER_ONBOARDING.md")
        for phrase in (
            "Google Workspace lane",
            "Microsoft 365, OneDrive and SharePoint lane",
            "Apple and iCloud lane",
            "Claude and other AI runtimes",
            "Institutional and VA deployment",
            "No local OneDrive sync client",
            "read → write → readback",
        ):
            self.assertIn(phrase, providers)
        install = self.text("INSTALL.md")
        self.assertIn("PROVIDER_ONBOARDING.md", install)
        self.assertIn("MIRA-Public-Experimental/generate", install)

    def test_public_front_door_uses_current_working_name(self) -> None:
        surfaces = (
            (ROOT.parent / "README.md").read_text(encoding="utf-8"),
            self.text("README.md"),
            self.text("INSTALL.md"),
        )
        for surface in surfaces:
            self.assertIn("M.I.R.R.O.R.", surface)
            self.assertIn("MIRA", surface)
            self.assertNotIn("# LyfeOS", surface)
        branding = (ROOT.parent / "docs" / "BRANDING.md").read_text(encoding="utf-8")
        self.assertIn("Memory, Integration, Reality, Reconciliation, Observation, and Record", branding)
        self.assertIn("MIRROR Intelligence and Reasoning Assistant", branding)
        self.assertIn("compatibility identifiers", branding)
        self.assertIn("proper trademark/domain/app-store clearance", branding)


del _BaseNontechnicalInstallationTests
del _namespace
