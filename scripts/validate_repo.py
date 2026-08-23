#!/usr/bin/env python3
"""Validate the repository's policy, starter, and stable bootstrap contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from policy_fingerprint import compute

REQUIRED = (
    "README.md",
    "project/INSTRUCTIONS.md.tmpl",
    "project/POLICY_FINGERPRINT.txt",
    "docs/lyfeos-data-model.md",
    "docs/household-financial-reconciliation.md",
    "docs/automation-contracts.md",
    "starter/README.md",
    "starter/START_HERE.md",
    "starter/MODULE_CATALOG.md",
    "starter/DEPENDENCIES.md",
    "starter/VERSIONING.md",
    "starter/config.example.json",
    "starter/questions.json",
    "starter/INSTRUCTIONS.md.tmpl",
    "skill/ops-brief-policy/SKILL.md",
    "skill/ops-brief-policy/references/receipt-ingestion.md",
    "skill/ops-brief-policy/references/receipt-classification-fitment.md",
    "skill/ops-brief-policy/references/receipt-photo-intake.md",
    "skill/ops-brief-policy/references/asset-acquisition.md",
    "skill/ops-brief-policy/references/knowledge-manual-ingestion.md",
    "skill/ops-brief-policy/references/calendar-projection.md",
    "skill/ops-brief-policy/references/household-reimbursement.md",
    "skill/ops-brief-policy/references/payment-reconciliation.md",
    "skill/ops-brief-policy/references/vendor-contact.md",
    "skill/ops-brief-policy/references/chat-portability.md",
    "skill/ops-brief-policy/references/email-reconciliation.md",
    "skill/ops-brief-policy/references/state-maintenance.md",
    "skill/ops-brief-policy/scripts/payment_reconciliation.py",
    "skill/ops-brief-policy/scripts/test_payment_reconciliation.py",
    "scripts/import_run_sheet.py",
    "scripts/audit_starter_privacy.py",
    "privacy/starter-blocklist.txt",
)
MAX_PROJECT_INSTRUCTIONS_CHARS = 3_000


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        require((root / relative).is_file(), f"missing required file: {relative}", errors)
    if errors:
        return errors

    def text(relative: str) -> str:
        return (root / relative).read_text(encoding="utf-8")

    project = text("project/INSTRUCTIONS.md.tmpl")
    skill = text("skill/ops-brief-policy/SKILL.md")
    maintenance = text("skill/ops-brief-policy/references/state-maintenance.md")
    receipt = text("skill/ops-brief-policy/references/receipt-ingestion.md")
    fitment = text("skill/ops-brief-policy/references/receipt-classification-fitment.md")
    photo = text("skill/ops-brief-policy/references/receipt-photo-intake.md")
    email = text("skill/ops-brief-policy/references/email-reconciliation.md")
    asset = text("skill/ops-brief-policy/references/asset-acquisition.md")
    manual = text("skill/ops-brief-policy/references/knowledge-manual-ingestion.md")
    calendar = text("skill/ops-brief-policy/references/calendar-projection.md")
    reimbursement = text("skill/ops-brief-policy/references/household-reimbursement.md")
    payment = text("skill/ops-brief-policy/references/payment-reconciliation.md")
    contact = text("skill/ops-brief-policy/references/vendor-contact.md")
    chat = text("skill/ops-brief-policy/references/chat-portability.md")
    start = text("starter/START_HERE.md")
    catalog = text("starter/MODULE_CATALOG.md")
    dependencies = text("starter/DEPENDENCIES.md")
    importer = text("scripts/import_run_sheet.py")

    require(len(project) <= MAX_PROJECT_INSTRUCTIONS_CHARS, f"project contract exceeds {MAX_PROJECT_INSTRUCTIONS_CHARS} characters: {len(project)}", errors)
    for phrase in (
        "BOOTSTRAP_CONTRACT_VERSION: 2",
        "project/POLICY_FINGERPRINT.txt",
        "2:45 AM/PM Eastern Ops Brief",
        "BYHOUR=2,14;BYMINUTE=45;BYSECOND=0",
        "Receipt & Order Lifecycle",
        "BYHOUR=1,13;BYMINUTE=45",
        "sole policy/code/test/bootstrap source",
        "runtime copy",
        "FedEx/UPS/DHL/USPS",
        "Paid terminal miles are symmetric A↔B",
        "immutable UUID",
        "Do you want me to send this email?",
    ):
        require(phrase in project, f"project contract lacks: {phrase}", errors)
    require("POLICY_SOURCE_FINGERPRINT:" not in project, "project contract still embeds changing policy fingerprint", errors)

    fingerprint = text("project/POLICY_FINGERPRINT.txt").strip()
    require(re.fullmatch(r"[0-9a-f]{64}", fingerprint) is not None, "Git-side policy fingerprint is invalid", errors)
    if re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        actual = compute(root / "skill/ops-brief-policy")
        print(f"POLICY_FINGERPRINT_ACTUAL={actual}")

    for ref in (
        "receipt-ingestion.md", "receipt-photo-intake.md", "asset-acquisition.md",
        "knowledge-manual-ingestion.md", "calendar-projection.md", "household-reimbursement.md",
        "payment-reconciliation.md", "vendor-contact.md", "chat-portability.md",
    ):
        require(ref in skill, f"skill does not route {ref}", errors)
    require("unique canonical terminal pairs" in skill, "skill may import repeated historical trip occurrences", errors)
    require("FedEx/UPS/DHL/USPS" in skill, "skill lacks USPS carrier-retention scope", errors)
    require("immutable collision-resistant RFC 4122 UUID" in skill, "skill lacks global immutable identity", errors)

    require("Partial Cancellation Confirmed" in receipt and "Cancellation Requested" in receipt, "receipt policy lacks cancellation lifecycle handling", errors)
    require("Replacement Group ID" in receipt, "receipt policy lacks linked replacement handling", errors)
    require("Investigation before queue" in fitment and "Unique resolution may be established by exclusion" in fitment, "fitment policy permits premature unknown assignment", errors)
    require("card last-four" in fitment, "financial resolution policy lacks last-four reconciliation", errors)
    require("UPC/EAN/GTIN" in photo and "chat-local shadow receipt database" in photo, "photo intake lacks canonical barcode/receipt ingestion", errors)
    require("A reimbursement is not a merchant refund" in reimbursement and "Net Household Cost" in reimbursement, "reimbursement policy lacks net-household semantics", errors)
    require("Awaiting Settlement" in payment and "Overcharged" in payment and "unmatched" in payment.lower(), "payment policy lacks settlement/variance investigation", errors)
    require("do not reply" in contact.lower() and "Do you want me to send this email?" in contact, "vendor contact safety is incomplete", errors)
    require("deleting the originating ChatGPT conversation" in chat, "chat portability does not make old chats disposable", errors)

    require("Orders/History/<vendor-slug>/<order-number>" in email, "email policy lacks per-order Gmail filing", errors)
    require("FedEx, UPS, DHL and USPS" in email and "90 calendar days" in email, "email policy lacks USPS-inclusive bounded carrier purge", errors)
    require("Any carrier not named above remains retention-only" in email, "carrier retention scope is not bounded", errors)
    require("open return, claim, dispute" in email, "carrier purge lacks exception hold", errors)

    require("immutable RFC 4122 UUID" in asset and "collision-resistant across deployments/family members" in asset, "asset UUID contract is incomplete", errors)
    require("Manuals & Reference" in manual and "Knowledge Index" in manual and "canonical Drive link" in manual, "manual knowledge contract is incomplete", errors)
    require("immutable RFC 4122 UUID" in manual and "PostgreSQL" in manual, "manual migration identity contract is incomplete", errors)
    require("Calendar Projection" in calendar and "source type + source ID" in calendar and "order delivery dates/windows" in calendar, "calendar projection contract is incomplete", errors)
    require("same paid-mile value" in maintenance, "state maintenance lacks symmetric mileage upsert", errors)

    require("historical_occurrences_imported" in importer and "False" in importer, "run-sheet importer does not prohibit occurrence creation", errors)
    require("TERMINAL_ALIASES" in importer and '"I4C": "IRC"' in importer, "run-sheet importer lacks proven alias normalization", errors)
    require("route_pair_count" in importer and '"occurrences"' not in importer, "run-sheet importer still exports historical occurrence rows", errors)

    questions = json.loads(text("starter/questions.json"))
    config = json.loads(text("starter/config.example.json"))
    rows = [q for section in questions.get("sections", []) for q in section.get("questions", [])]
    ids = [q.get("id") for q in rows]
    require(len(rows) >= 40 and len(ids) == len(set(ids)), "starter questionnaire is missing depth or has duplicate IDs", errors)
    require(all(isinstance(k, str) and k.isupper() for k in config), "starter config keys must be uppercase tokens", errors)
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships production schedule times", errors)
    require(len(start) < 9000, f"START_HERE exceeds 9000 characters: {len(start)}", errors)
    for phrase in (
        "Minimum Useful Setup", "Start now by asking only the four kickoff questions",
        "non-technical user", "exactly what to click", "automatically validate, commit, push and verify",
        "Dependency gate", "Calendar Projection", "immutable UUID", "manual", "Awaiting Settlement",
        "Do you want me to send this email?", "old chats are deleted",
    ):
        require(phrase.lower() in start.lower(), f"starter onboarding lacks: {phrase}", errors)
    require("GitHub side" in dependencies and "ChatGPT side" in dependencies and "Installed GitHub Apps" in dependencies, "dependency guide lacks two-sided GitHub setup", errors)
    require("Manuals and reference library" in catalog and "immutable collision-resistant UUID" in catalog, "module catalog lacks manual/UUID enrollment", errors)

    for private_marker in ("Matthew-Beare", "jbeare92", "1pHkTdCx", "Pig Pet", "Mazda Miata", "Subaru WRX", "Civic Type R"):
        require(private_marker not in start + catalog + dependencies, f"starter leaks user-specific marker: {private_marker}", errors)

    generic = text("starter/INSTRUCTIONS.md.tmpl")
    template_tokens = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", generic))
    require(template_tokens <= set(config), "starter config does not cover every template token", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
