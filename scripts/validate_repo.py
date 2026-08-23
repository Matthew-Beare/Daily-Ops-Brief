#!/usr/bin/env python3
"""Validate the repository's policy, starter, and bootstrap contract."""

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
    "docs/lyfeos-data-model.md",
    "docs/household-financial-reconciliation.md",
    "docs/automation-contracts.md",
    "starter/README.md",
    "starter/START_HERE.md",
    "starter/VERSIONING.md",
    "starter/config.example.json",
    "starter/questions.json",
    "starter/INSTRUCTIONS.md.tmpl",
    "skill/ops-brief-policy/SKILL.md",
    "skill/ops-brief-policy/references/receipt-ingestion.md",
    "skill/ops-brief-policy/references/receipt-classification-fitment.md",
    "skill/ops-brief-policy/references/receipt-photo-intake.md",
    "skill/ops-brief-policy/references/household-reimbursement.md",
    "skill/ops-brief-policy/references/payment-reconciliation.md",
    "skill/ops-brief-policy/references/vendor-contact.md",
    "skill/ops-brief-policy/references/chat-portability.md",
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
    reimbursement_policy = (root / "skill/ops-brief-policy/references/household-reimbursement.md").read_text(encoding="utf-8")
    payment_policy = (root / "skill/ops-brief-policy/references/payment-reconciliation.md").read_text(encoding="utf-8")
    contact_policy = (root / "skill/ops-brief-policy/references/vendor-contact.md").read_text(encoding="utf-8")
    chat_policy = (root / "skill/ops-brief-policy/references/chat-portability.md").read_text(encoding="utf-8")

    require(
        len(project) <= MAX_PROJECT_INSTRUCTIONS_CHARS,
        f"project contract exceeds {MAX_PROJECT_INSTRUCTIONS_CHARS} characters: {len(project)}",
        errors,
    )

    require("Keep exactly one active Ops Brief automation" in project, "project contract does not require one active Ops Brief automation", errors)
    require("BYHOUR=2,14;BYMINUTE=45;BYSECOND=0" in project, "project contract is missing the twice-daily RRULE", errors)
    require("exactly one active Ops Brief automation" in skill, "skill invariant is not the one-task design", errors)
    require("receipt-ingestion.md" in skill, "skill does not route receipt ingestion", errors)
    require("receipt-photo-intake.md" in skill, "skill does not route receipt images/screenshots into canonical ingestion", errors)
    require("household-reimbursement.md" in skill, "skill does not route beneficiary/reimbursement reconciliation", errors)
    require("payment-reconciliation.md" in skill, "skill does not route expected merchant charge reconciliation", errors)
    require("vendor-contact.md" in skill, "skill does not route safe vendor contact", errors)
    require("chat-portability.md" in skill, "skill does not define cross-chat recovery", errors)
    require("receipt photo" in skill.lower() or "receipt, invoice" in skill.lower(), "skill metadata does not advertise photo/receipt intake", errors)
    require("Purchase & Receipt Archive" in project, "project contract is missing purchase authority", errors)
    require("Receipt & Order Lifecycle" in project, "project contract is missing the consolidated receipt lifecycle task", errors)
    require("BYHOUR=1,13;BYMINUTE=45" in project, "project contract is missing the receipt lifecycle RRULE", errors)
    require("Audit gate" in project, "project contract is missing the receipt integrity gate", errors)
    require("Order Events" in skill, "skill does not preserve lifecycle history", errors)
    require("Classification Queue" in skill, "skill does not route unknown purchase classification", errors)
    require("Payment Reconciliation" in skill, "skill lacks persistent expected-charge cases", errors)
    require("Partial Cancellation Confirmed" in receipt_policy, "receipt policy lacks confirmed partial-cancellation handling", errors)
    require("Cancellation Requested" in receipt_policy, "receipt policy lacks pending-cancellation handling", errors)
    require("scope: order" in email_policy, "email policy lacks full-order cancellation scope", errors)
    require("remaining_item" in email_policy, "email policy lacks surviving-item cancellation evidence", errors)
    require("Replacement Group ID" in receipt_policy, "receipt policy lacks linked replacement-order handling", errors)
    require("replacement_order_number" in email_policy, "email policy lacks replacement shipment evidence", errors)
    require("Order Events!A1:Q1000" in email_policy, "email policy does not read replacement-link columns", errors)
    require("Investigation before queue" in fitment_policy, "fitment policy permits premature unknown assignment", errors)
    require("Unique resolution may be established by exclusion" in fitment_policy, "fitment policy lacks exclusion-based asset assignment", errors)
    require("card last-four" in fitment_policy, "financial resolution policy lacks payment-account last-four reconciliation", errors)
    require("UPC/EAN/GTIN" in photo_policy, "photo intake does not extract barcode/product identity", errors)
    require("chat-local shadow receipt database" in photo_policy, "photo intake does not require canonical LifeOS state", errors)
    require("Only after reachable evidence has been exhausted" in photo_policy, "photo intake permits premature unknown classification", errors)
    require("photograph and an email are often two sources for one transaction" in photo_policy, "photo intake lacks cross-source deduplication", errors)
    require("explicit pre-send confirmation" in photo_policy, "photo intake lacks explicit email send confirmation", errors)
    require("A reimbursement is not a merchant refund" in reimbursement_policy, "reimbursement policy conflates payback with merchant refunds", errors)
    require("Net Household Cost" in reimbursement_policy, "reimbursement policy lacks household net-cost accounting", errors)
    require("Awaiting Settlement" in payment_policy, "payment policy lacks persistent unsettled-charge state", errors)
    require("Overcharged" in payment_policy, "payment policy lacks merchant overcharge detection", errors)
    require("unmatched" in payment_policy.lower(), "payment policy lacks unmatched charge investigation", errors)
    require("do not reply" in contact_policy.lower(), "vendor-contact policy does not detect no-reply/unmonitored mail", errors)
    require("Do you want me to send this email?" in contact_policy, "vendor-contact policy lacks exact pre-send approval", errors)
    require("deleting the originating ChatGPT conversation" in chat_policy, "chat portability does not make prior chat disposable", errors)
    require("without asking for a separate Git confirmation" in maintenance, "state maintenance lacks automatic Git synchronization", errors)
    require("automatically commit/push" in project, "project contract lacks automatic durable Git synchronization", errors)
    require("sole policy/code/test/bootstrap source" in project, "project contract lacks a sole policy source of truth", errors)
    require("runtime copy" in project, "project contract does not define the installed skill as a deployment copy", errors)
    require("sole source of truth" in maintenance, "state maintenance lacks a sole repository authority", errors)
    require("deployed runtime copy" in maintenance, "state maintenance treats the installed skill as a competing authority", errors)
    require("To consolidate a healthy legacy AM/PM pair" in maintenance, "state maintenance lacks the migration transaction", errors)
    require("Keep exactly two active Ops Brief" not in project + skill + maintenance, "legacy two-task invariant remains", errors)

    match = re.search(r"POLICY_SOURCE_FINGERPRINT: sha256:([0-9a-f]{64})", project)
    require(match is not None, "project contract has no valid policy fingerprint", errors)
    if match:
        actual = compute(root / "skill/ops-brief-policy")
        require(match.group(1) == actual, f"policy fingerprint mismatch: expected {actual}", errors)

    questions = json.loads((root / "starter/questions.json").read_text(encoding="utf-8"))
    config = json.loads((root / "starter/config.example.json").read_text(encoding="utf-8"))
    start_here = (root / "starter/START_HERE.md").read_text(encoding="utf-8")
    question_rows = [question for section in questions.get("sections", []) for question in section.get("questions", [])]
    ids = [row.get("id") for row in question_rows]
    require(len(question_rows) >= 40, "starter questionnaire is not deep enough", errors)
    require(len(ids) == len(set(ids)), "starter questionnaire contains duplicate IDs", errors)
    require(all(isinstance(key, str) and key.isupper() for key in config), "starter config keys must be uppercase tokens", errors)
    for required_key in ("ORDER_UPDATE_SLOTS", "ORDER_NOTIFICATION_MODE", "RECIPE_LIBRARY_MODE", "MODE_MODEL", "AUTO_VERSIONING", "MERGE_POLICY", "HOUSEHOLD_MODEL", "PAYMENT_RECONCILIATION", "REIMBURSEMENT_TRACKING"):
        require(required_key in config, f"starter config is missing {required_key}", errors)
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone instead of requiring first-boot input", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships production schedule times", errors)
    require("Minimum Useful Setup" in start_here, "starter has no minimum-useful-setup path", errors)
    require("no more than four" in start_here.lower(), "starter does not bound first-boot question batches", errors)
    require("explicit approval" in start_here, "starter does not approval-gate consequential actions", errors)
    require("automatically create" in start_here.lower(), "starter does not automate baseline resource provisioning", errors)
    require("idempotent" in start_here.lower(), "starter provisioning does not require dedupe/migration instead of duplicate databases", errors)
    require("partial cancellation" in start_here.lower(), "starter lacks order-cancellation lifecycle guidance", errors)
    require("authoritative timezone" in start_here.lower(), "starter does not ask for an authoritative timezone", errors)
    require("exact local times" in start_here.lower(), "starter does not ask for exact local update times", errors)
    require("recipe library" in start_here.lower(), "starter lacks stock recipe handling", errors)
    require("exact job title" in start_here.lower(), "starter does not ask for the exact job title", errors)
    require("mark HOME/ROAD bypassed" in start_here, "starter does not bypass HOME/ROAD for non-travel roles", errors)
    require("driving/trucking" in start_here.lower(), "starter does not route travel jobs into HOME/ROAD", errors)
    require("automatically update validation, commit, and push" in start_here, "starter lacks standing automatic Git versioning", errors)
    require("true replacement" in start_here.lower(), "starter lacks linked replacement-order semantics", errors)
    require("Awaiting Settlement" in start_here, "starter lacks expected-charge follow-through", errors)
    require("reimbursement" in start_here.lower(), "starter lacks outside-beneficiary reimbursement workflow", errors)
    require("Do you want me to send this email?" in start_here, "starter lacks explicit email approval prompt", errors)
    require("old chats are deleted" in start_here.lower(), "starter does not require chat-disposable recovery", errors)
    require("Start now by asking only the four kickoff questions" in start_here, "starter lacks a deterministic conversational entry point", errors)
    for private_marker in ("Matthew-Beare", "jbeare92", "1pHkTdCx", "Mazda Miata", "Subaru WRX", "Civic Type R"):
        require(private_marker not in start_here, f"starter leaks user-specific marker: {private_marker}", errors)

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
