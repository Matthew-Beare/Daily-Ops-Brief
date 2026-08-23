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
    "starter/LIFE_INTERVIEW.md",
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
    "skill/ops-brief-policy/references/life-planning-accountability.md",
    "skill/ops-brief-policy/references/pants-filling-with-shit-report.md",
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
MAX_START_HERE_CHARS = 9_000


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
    life = text("skill/ops-brief-policy/references/life-planning-accountability.md")
    pants = text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
    calendar = text("skill/ops-brief-policy/references/calendar-projection.md")
    reimbursement = text("skill/ops-brief-policy/references/household-reimbursement.md")
    payment = text("skill/ops-brief-policy/references/payment-reconciliation.md")
    contact = text("skill/ops-brief-policy/references/vendor-contact.md")
    chat = text("skill/ops-brief-policy/references/chat-portability.md")
    automation_docs = text("docs/automation-contracts.md")
    start = text("starter/START_HERE.md")
    interview = text("starter/LIFE_INTERVIEW.md")
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
        require(fingerprint == actual, f"policy fingerprint mismatch: expected {actual}", errors)

    for ref in (
        "receipt-ingestion.md", "receipt-photo-intake.md", "asset-acquisition.md",
        "knowledge-manual-ingestion.md", "life-planning-accountability.md", "pants-filling-with-shit-report.md",
        "calendar-projection.md", "household-reimbursement.md", "payment-reconciliation.md", "vendor-contact.md", "chat-portability.md",
    ):
        require(ref in skill, f"skill does not route {ref}", errors)
    require("unique canonical terminal pairs" in skill, "skill may import repeated historical trip occurrences", errors)
    require("FedEx/UPS/DHL/USPS" in skill, "skill lacks USPS carrier-retention scope", errors)
    require("immutable collision-resistant RFC 4122 UUID" in skill, "skill lacks global immutable identity", errors)
    require("Retry is not mandatory" in skill, "skill treats retries as mandatory", errors)
    require("Pants Filling With Shit Report" in skill, "skill lacks named failure circuit breaker", errors)
    require("never create hidden retry jobs" in skill, "skill lacks retry-job prohibition", errors)
    require("Shopping & Procurement" in skill, "skill lacks shopping/procurement reconciliation routing", errors)
    require("active shopping list" in skill and "remove the fulfilled shopping row" in skill, "skill does not enforce active-shopping-list semantics", errors)
    require("stored/default/execution timezone" in skill, "skill accepts visible TZID without provider execution-timezone verification", errors)
    require("life-planning-accountability.md" in skill, "skill lacks personal planning/accountability routing", errors)

    receipt_lower = receipt.lower()
    require("Partial Cancellation Confirmed" in receipt and "Cancellation Requested" in receipt, "receipt policy lacks cancellation lifecycle handling", errors)
    require("Replacement Group ID" in receipt, "receipt policy lacks linked replacement handling", errors)
    require("shopping & procurement reconciliation" in receipt_lower, "receipt policy lacks shopping reconciliation", errors)
    require("active shopping list" in receipt and "remove the fulfilled shopping row" in receipt, "receipt policy still treats shopping as purchase history", errors)
    require("explicit owner statement" in receipt and "separate reconciliation task" in receipt, "receipt policy cannot resolve owner-confirmed purchases with missing evidence", errors)
    require("Purchased` tombstone" in receipt, "receipt policy does not prohibit purchased tombstones", errors)
    require("cancellation with no supported replacement" in receipt, "receipt policy may close cancelled intent incorrectly", errors)
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

    require("# Pants Filling With Shit Report" in pants, "failure report has wrong name", errors)
    require("same external operation fails twice" in pants, "failure report lacks repeated-failure trigger", errors)
    require("Retry is **not mandatory**" in pants, "failure report lacks no-retry boundary", errors)
    require("Stop writes for the affected module" in pants and "Continue unrelated modules" in pants, "failure report is not module-scoped", errors)
    require("never blind-rerun" in pants and "ambiguous" in pants.lower(), "failure report lacks CI/partial-write protection", errors)
    require("Scheduler execution timezone mismatch" in pants and "subsequent actual run/Run Log timestamp" in pants, "failure report lacks scheduler-timezone recovery proof", errors)

    require("Calendar Projection" in calendar and "source type + source ID" in calendar and "order delivery dates/windows" in calendar, "calendar projection contract is incomplete", errors)
    require("same paid-mile value" in maintenance, "state maintenance lacks symmetric mileage upsert", errors)
    require("A reusable route pair may be learned even when the user does not want a current Trip occurrence created" in maintenance, "route learning incorrectly forces trip tracking", errors)
    require("stored/default/execution timezone" in maintenance and "travel/device timezone" in maintenance, "automation maintenance lacks provider execution-timezone integrity", errors)
    require("Do **not** report a timezone repair successful from VEVENT text alone" in maintenance, "automation repair can falsely pass on VEVENT text", errors)
    require("stored/default/execution timezone" in automation_docs and "fail the automation-maintenance module closed" in automation_docs, "automation contract lacks fail-closed timezone behavior", errors)

    require("# Life Planning, Accountability, and Study" in life, "life planning policy is missing", errors)
    require("Next-action planner" in life and "Routine accountability" in life, "life planning lacks next-action/accountability semantics", errors)
    require("Exercise / fitness organization" in life and "School / study workflow" in life, "life planning lacks exercise/study modules", errors)
    require("do not infer completion from silence" in life.lower(), "life planning may hallucinate completion", errors)

    require("historical_occurrences_imported" in importer and "False" in importer, "run-sheet importer does not prohibit occurrence creation", errors)
    require("TERMINAL_ALIASES" in importer and '"I4C": "IRC"' in importer, "run-sheet importer lacks proven alias normalization", errors)
    require("route_pair_count" in importer and '"occurrences"' not in importer, "run-sheet importer still exports historical occurrence rows", errors)

    questions = json.loads(text("starter/questions.json"))
    config = json.loads(text("starter/config.example.json"))
    rows = [q for section in questions.get("sections", []) for q in section.get("questions", [])]
    ids = [q.get("id") for q in rows]
    require(len(rows) >= 80 and len(ids) == len(set(ids)), "starter questionnaire is missing whole-life depth or has duplicate IDs", errors)
    for qid in (
        "works_away_from_home", "accountability_domains", "routine_progression", "education_active",
        "study_home_away", "study_next_action_rule", "scheduler_timezone_integrity",
    ):
        require(qid in ids, f"starter questionnaire lacks adaptive field: {qid}", errors)
    require(all(isinstance(k, str) and k.isupper() for k in config), "starter config keys must be uppercase tokens", errors)
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships production schedule times", errors)

    require(len(start) < MAX_START_HERE_CHARS, f"START_HERE exceeds {MAX_START_HERE_CHARS} characters: {len(start)}", errors)
    for phrase in (
        "Minimum Useful Setup", "Start now by asking only the four kickoff questions",
        "non-technical user", "exactly what to click", "automatically update validation, commit, and push",
        "Dependency gate", "Pants Filling With Shit Report", "partial cancellation", "Calendar Projection",
        "immutable UUID", "manual", "Awaiting Settlement", "Do you want me to send this email?", "old chats are deleted",
        "work away from home", "whole-life interview", "active shopping list",
    ):
        require(phrase.lower() in start.lower(), f"starter onboarding lacks: {phrase}", errors)

    for phrase in (
        "Do you regularly work away from home", "minimum viable version", "home versus away/on the road",
        "Exercise / fitness", "School / study", "what to do next", "stored/execution timezone",
    ):
        require(phrase.lower() in interview.lower(), f"adaptive life interview lacks: {phrase}", errors)

    require("GitHub side" in dependencies and "ChatGPT side" in dependencies and "Installed GitHub Apps" in dependencies, "dependency guide lacks two-sided GitHub setup", errors)
    require("stored/default/execution timezone" in dependencies and "fail closed" in dependencies, "dependency guide lacks scheduler-timezone gate", errors)
    require("Manuals and reference library" in catalog and "immutable collision-resistant UUID" in catalog, "module catalog lacks manual/UUID enrollment", errors)
    require("Shopping and procurement reconciliation" in catalog, "module catalog lacks shopping/procurement enrollment", errors)
    require("Personal accountability and routines" in catalog and "Education and study coach" in catalog, "module catalog lacks whole-life accountability/study modules", errors)

    starter_surface = start + interview + catalog + dependencies + json.dumps(questions)
    for private_marker in ("Matthew-Beare", "jbeare92", "1pHkTdCx", "Pig Pet", "Mazda Miata", "Subaru WRX", "Civic Type R"):
        require(private_marker not in starter_surface, f"starter leaks user-specific marker: {private_marker}", errors)

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
