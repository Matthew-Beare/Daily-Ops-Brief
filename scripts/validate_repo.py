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
    "skill/ops-brief-policy/references/calendar-projection.md",
    "skill/ops-brief-policy/references/household-reimbursement.md",
    "skill/ops-brief-policy/references/payment-reconciliation.md",
    "skill/ops-brief-policy/references/vendor-contact.md",
    "skill/ops-brief-policy/references/chat-portability.md",
    "skill/ops-brief-policy/references/email-reconciliation.md",
    "skill/ops-brief-policy/references/state-maintenance.md",
    "skill/ops-brief-policy/scripts/payment_reconciliation.py",
    "skill/ops-brief-policy/scripts/test_payment_reconciliation.py",
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

    project = (root / "project/INSTRUCTIONS.md.tmpl").read_text(encoding="utf-8")
    skill = (root / "skill/ops-brief-policy/SKILL.md").read_text(encoding="utf-8")
    maintenance = (root / "skill/ops-brief-policy/references/state-maintenance.md").read_text(encoding="utf-8")
    receipt_policy = (root / "skill/ops-brief-policy/references/receipt-ingestion.md").read_text(encoding="utf-8")
    fitment_policy = (root / "skill/ops-brief-policy/references/receipt-classification-fitment.md").read_text(encoding="utf-8")
    photo_policy = (root / "skill/ops-brief-policy/references/receipt-photo-intake.md").read_text(encoding="utf-8")
    email_policy = (root / "skill/ops-brief-policy/references/email-reconciliation.md").read_text(encoding="utf-8")
    asset_policy = (root / "skill/ops-brief-policy/references/asset-acquisition.md").read_text(encoding="utf-8")
    calendar_policy = (root / "skill/ops-brief-policy/references/calendar-projection.md").read_text(encoding="utf-8")
    reimbursement_policy = (root / "skill/ops-brief-policy/references/household-reimbursement.md").read_text(encoding="utf-8")
    payment_policy = (root / "skill/ops-brief-policy/references/payment-reconciliation.md").read_text(encoding="utf-8")
    contact_policy = (root / "skill/ops-brief-policy/references/vendor-contact.md").read_text(encoding="utf-8")
    chat_policy = (root / "skill/ops-brief-policy/references/chat-portability.md").read_text(encoding="utf-8")
    start_here = (root / "starter/START_HERE.md").read_text(encoding="utf-8")
    module_catalog = (root / "starter/MODULE_CATALOG.md").read_text(encoding="utf-8")
    dependencies = (root / "starter/DEPENDENCIES.md").read_text(encoding="utf-8")

    require(len(project) <= MAX_PROJECT_INSTRUCTIONS_CHARS, f"project contract exceeds {MAX_PROJECT_INSTRUCTIONS_CHARS} characters: {len(project)}", errors)
    require("BOOTSTRAP_CONTRACT_VERSION: 2" in project, "project contract lacks stable bootstrap version", errors)
    require("project/POLICY_FINGERPRINT.txt" in project, "project contract does not delegate policy integrity to Git", errors)
    require("POLICY_SOURCE_FINGERPRINT:" not in project, "project contract still embeds a changing policy fingerprint", errors)
    require("2:45 AM/PM Eastern Ops Brief" in project and "BYHOUR=2,14;BYMINUTE=45;BYSECOND=0" in project, "project contract is missing canonical Ops schedule", errors)
    require("Receipt & Order Lifecycle" in project and "BYHOUR=1,13;BYMINUTE=45" in project, "project contract is missing consolidated receipt schedule", errors)
    require("sole policy/code/test/bootstrap source" in project, "project contract lacks sole repository authority", errors)
    require("runtime copy" in project, "project contract does not define installed skill as deployment copy", errors)
    require("Paid terminal miles are symmetric A↔B" in project, "project contract lacks symmetric paid-mile rule", errors)
    require("90-day post-delivery retention rule" in project, "project contract lacks narrow carrier retention exception", errors)
    require("Do you want me to send this email?" in project, "project contract lacks explicit send approval", errors)

    fingerprint = (root / "project/POLICY_FINGERPRINT.txt").read_text(encoding="utf-8").strip()
    require(re.fullmatch(r"[0-9a-f]{64}", fingerprint) is not None, "Git-side policy fingerprint is invalid", errors)
    if re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        actual = compute(root / "skill/ops-brief-policy")
        require(fingerprint == actual, f"policy fingerprint mismatch: expected {actual}", errors)

    for ref in ("receipt-ingestion.md", "receipt-photo-intake.md", "asset-acquisition.md", "calendar-projection.md", "household-reimbursement.md", "payment-reconciliation.md", "vendor-contact.md", "chat-portability.md"):
        require(ref in skill, f"skill does not route {ref}", errors)
    require("Paid terminal mileage is symmetric" in skill, "skill lacks symmetric terminal mileage", errors)
    require("90-day retention rule" in skill, "skill lacks carrier retention routing", errors)
    require("Calendar Projection" in skill, "skill lacks calendar projection state", errors)
    require("model/serial" in skill.lower(), "skill metadata lacks asset identity intake", errors)

    require("Partial Cancellation Confirmed" in receipt_policy and "Cancellation Requested" in receipt_policy, "receipt policy lacks cancellation lifecycle handling", errors)
    require("Replacement Group ID" in receipt_policy, "receipt policy lacks linked replacement handling", errors)
    require("Investigation before queue" in fitment_policy and "Unique resolution may be established by exclusion" in fitment_policy, "fitment policy permits premature unknown assignment", errors)
    require("card last-four" in fitment_policy, "financial resolution policy lacks last-four reconciliation", errors)
    require("UPC/EAN/GTIN" in photo_policy and "chat-local shadow receipt database" in photo_policy, "photo intake lacks canonical barcode/receipt ingestion", errors)
    require("A reimbursement is not a merchant refund" in reimbursement_policy and "Net Household Cost" in reimbursement_policy, "reimbursement policy lacks net-household semantics", errors)
    require("Awaiting Settlement" in payment_policy and "Overcharged" in payment_policy and "unmatched" in payment_policy.lower(), "payment policy lacks settlement/variance investigation", errors)
    require("do not reply" in contact_policy.lower() and "Do you want me to send this email?" in contact_policy, "vendor contact safety is incomplete", errors)
    require("deleting the originating ChatGPT conversation" in chat_policy, "chat portability does not make old chats disposable", errors)
    require("Orders/History/<vendor-slug>/<order-number>" in email_policy, "email policy lacks per-order Gmail filing", errors)
    require("90 calendar days" in email_policy and "FedEx, UPS and DHL" in email_policy, "email policy lacks bounded carrier purge rule", errors)
    require("USPS" in email_policy and "remain retention-only" in email_policy, "carrier purge rule is not narrowly bounded", errors)
    require("model number" in asset_policy.lower() and "serial number" in asset_policy.lower() and "one stable Asset/Tool ID" in asset_policy, "asset acquisition contract is incomplete", errors)
    require("Calendar Projection" in calendar_policy and "order delivery dates/windows" in calendar_policy and "source type + source ID" in calendar_policy, "calendar projection contract is incomplete", errors)
    require("A↔B" in maintenance and "same paid-mile value" in maintenance, "state maintenance lacks symmetric mileage upsert", errors)
    require("Calendar Projection" in maintenance, "state maintenance lacks calendar projection dedupe state", errors)
    require("stable bootstrap contract" in maintenance.lower(), "state maintenance lacks stable Project bootstrap design", errors)
    require("without asking for a separate Git confirmation" in maintenance, "state maintenance lacks standing Git synchronization", errors)
    require("To consolidate a healthy legacy AM/PM pair" in maintenance, "state maintenance lacks automation migration transaction", errors)

    questions = json.loads((root / "starter/questions.json").read_text(encoding="utf-8"))
    config = json.loads((root / "starter/config.example.json").read_text(encoding="utf-8"))
    question_rows = [q for section in questions.get("sections", []) for q in section.get("questions", [])]
    ids = [q.get("id") for q in question_rows]
    require(len(question_rows) >= 40, "starter questionnaire is not deep enough", errors)
    require(len(ids) == len(set(ids)), "starter questionnaire contains duplicate IDs", errors)
    require(all(isinstance(k, str) and k.isupper() for k in config), "starter config keys must be uppercase tokens", errors)
    for key in ("ORDER_UPDATE_SLOTS", "ORDER_NOTIFICATION_MODE", "RECIPE_LIBRARY_MODE", "MODE_MODEL", "AUTO_VERSIONING", "MERGE_POLICY", "HOUSEHOLD_MODEL", "PAYMENT_RECONCILIATION", "REIMBURSEMENT_TRACKING"):
        require(key in config, f"starter config is missing {key}", errors)
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships production schedule times", errors)
    require(len(start_here) < 9000, f"START_HERE exceeds 9000 characters: {len(start_here)}", errors)
    for phrase in ("Minimum Useful Setup", "Start now by asking only the four kickoff questions", "explicit approval", "authoritative timezone", "exact local times", "recipe", "exact job title", "mark HOME/ROAD bypassed", "driving/trucking", "true replacement", "automatically update validation, commit, and push", "Awaiting Settlement", "reimbursement", "Do you want me to send this email?", "old chats are deleted", "Dependency gate", "Calendar Projection"):
        require(phrase.lower() in start_here.lower(), f"starter onboarding lacks: {phrase}", errors)
    require("automatically create or validate" in start_here.lower() and "idempotent" in start_here.lower(), "starter lacks automated idempotent provisioning", errors)
    require("GitHub side" in dependencies and "ChatGPT side" in dependencies and "Installed GitHub Apps" in dependencies, "dependency guide lacks two-sided GitHub setup", errors)
    require("order delivery dates/windows" in module_catalog and "model/serial" in module_catalog.lower(), "module catalog lacks calendar/asset enrollment", errors)
    for private_marker in ("Matthew-Beare", "jbeare92", "1pHkTdCx", "Mazda Miata", "Subaru WRX", "Civic Type R"):
        require(private_marker not in start_here + module_catalog + dependencies, f"starter leaks user-specific marker: {private_marker}", errors)

    generic_template = (root / "starter/INSTRUCTIONS.md.tmpl").read_text(encoding="utf-8")
    template_tokens = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", generic_template))
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
