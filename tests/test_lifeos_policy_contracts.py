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

    def test_carrier_retention_is_narrow(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/email-reconciliation.md")
        self.assertIn("90 calendar days", policy)
        self.assertIn("FedEx, UPS and DHL", policy)
        self.assertIn("USPS", policy)
        self.assertIn("merchant order confirmation", policy.lower())
        self.assertIn("open return, claim, dispute", policy)

    def test_asset_acquisition_requires_dedupe_and_evidence(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/asset-acquisition.md")
        self.assertIn("one stable Asset/Tool ID", policy)
        self.assertIn("serial number", policy)
        self.assertIn("manufacturer/OEM", policy)
        self.assertIn("search existing canonical asset/tool/inventory records", policy)

    def test_calendar_projection_updates_in_place(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/calendar-projection.md")
        self.assertIn("Google Calendar event ID", policy)
        self.assertIn("update the linked event in place", policy)
        self.assertIn("order delivery dates/windows", policy)
        self.assertIn("Inviting other people", policy)

    def test_terminal_paid_miles_are_symmetric(self) -> None:
        policy = self.text("skill/ops-brief-policy/references/state-maintenance.md")
        self.assertIn("company-paid terminal mileage is symmetric by terminal pair", policy)
        self.assertIn("same paid-mile value", policy)


if __name__ == "__main__":
    unittest.main()
