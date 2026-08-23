#!/usr/bin/env python3
"""Validate the coherent LyfeOS public-release and reference-deployment contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from policy_fingerprint import compute

REQUIRED = (
    ".gitignore",
    "LICENSE",
    "README.md",
    ".github/workflows/ci.yml",
    "project/INSTRUCTIONS.md.tmpl",
    "project/POLICY_FINGERPRINT.txt",
    "policy/ops-brief-policy.yaml",
    "docs/automation-contracts.md",
    "docs/automation-design.md",
    "docs/data-platform-grafana.md",
    "docs/feature-audit-2026-08-22.md",
    "docs/household-financial-reconciliation.md",
    "docs/lyfeos-data-model.md",
    "starter/README.md",
    "starter/START_HERE.md",
    "starter/LIFE_INTERVIEW.md",
    "starter/MODULE_CATALOG.md",
    "starter/DEPENDENCIES.md",
    "starter/VERSIONING.md",
    "starter/SHARED_FEATURE_WORKFLOW.md",
    "starter/config.example.json",
    "starter/questions.json",
    "starter/INSTRUCTIONS.md.tmpl",
    "skill/ops-brief-policy/SKILL.md",
    "skill/ops-brief-policy/references/brief-run.md",
    "skill/ops-brief-policy/references/state-maintenance.md",
    "skill/ops-brief-policy/references/pants-filling-with-shit-report.md",
    "skill/ops-brief-policy/references/receipt-ingestion.md",
    "skill/ops-brief-policy/references/receipt-classification-fitment.md",
    "skill/ops-brief-policy/references/receipt-photo-intake.md",
    "skill/ops-brief-policy/references/email-reconciliation.md",
    "skill/ops-brief-policy/references/asset-acquisition.md",
    "skill/ops-brief-policy/references/knowledge-manual-ingestion.md",
    "skill/ops-brief-policy/references/life-planning-accountability.md",
    "skill/ops-brief-policy/references/calendar-projection.md",
    "skill/ops-brief-policy/references/household-reimbursement.md",
    "skill/ops-brief-policy/references/payment-reconciliation.md",
    "skill/ops-brief-policy/references/vendor-contact.md",
    "skill/ops-brief-policy/references/chat-portability.md",
    "skill/ops-brief-policy/scripts/ops_policy_runtime.py",
    "skill/ops-brief-policy/scripts/payment_reconciliation.py",
    "scripts/import_run_sheet.py",
    "scripts/audit_public_source.py",
    "scripts/audit_starter_privacy.py",
    "privacy/starter-blocklist.txt",
)
MAX_PROJECT_INSTRUCTIONS_CHARS = 3_000
MAX_START_HERE_CHARS = 9_000


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def has(text: str, *phrases: str) -> bool:
    lowered = text.lower()
    return all(phrase.lower() in lowered for phrase in phrases)


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED:
        require((root / relative).is_file(), f"missing required file: {relative}", errors)
    if errors:
        return errors

    def text(relative: str) -> str:
        return (root / relative).read_text(encoding="utf-8")

    def load_json(relative: str):
        try:
            return json.loads(text(relative))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {relative}: {exc}")
            return {}

    readme = text("README.md")
    gitignore = text(".gitignore")
    license_text = text("LICENSE")
    ci = text(".github/workflows/ci.yml")
    project = text("project/INSTRUCTIONS.md.tmpl")
    skill = text("skill/ops-brief-policy/SKILL.md")
    brief = text("skill/ops-brief-policy/references/brief-run.md")
    maintenance = text("skill/ops-brief-policy/references/state-maintenance.md")
    pants = text("skill/ops-brief-policy/references/pants-filling-with-shit-report.md")
    runtime = text("skill/ops-brief-policy/scripts/ops_policy_runtime.py")
    receipt = text("skill/ops-brief-policy/references/receipt-ingestion.md")
    fitment = text("skill/ops-brief-policy/references/receipt-classification-fitment.md")
    photo = text("skill/ops-brief-policy/references/receipt-photo-intake.md")
    email = text("skill/ops-brief-policy/references/email-reconciliation.md")
    asset = text("skill/ops-brief-policy/references/asset-acquisition.md")
    manual = text("skill/ops-brief-policy/references/knowledge-manual-ingestion.md")
    life = text("skill/ops-brief-policy/references/life-planning-accountability.md")
    calendar = text("skill/ops-brief-policy/references/calendar-projection.md")
    reimbursement = text("skill/ops-brief-policy/references/household-reimbursement.md")
    payment = text("skill/ops-brief-policy/references/payment-reconciliation.md")
    contact = text("skill/ops-brief-policy/references/vendor-contact.md")
    chat = text("skill/ops-brief-policy/references/chat-portability.md")
    automation = text("docs/automation-contracts.md")
    automation_design = text("docs/automation-design.md")
    data_platform = text("docs/data-platform-grafana.md")
    historical_audit = text("docs/feature-audit-2026-08-22.md")
    household_schema = text("docs/household-financial-reconciliation.md")
    compatibility = text("policy/ops-brief-policy.yaml")
    start = text("starter/START_HERE.md")
    interview = text("starter/LIFE_INTERVIEW.md")
    catalog = text("starter/MODULE_CATALOG.md")
    dependencies = text("starter/DEPENDENCIES.md")
    starter_readme = text("starter/README.md")
    versioning = text("starter/VERSIONING.md")
    shared = text("starter/SHARED_FEATURE_WORKFLOW.md")
    generic = text("starter/INSTRUCTIONS.md.tmpl")
    importer = text("scripts/import_run_sheet.py")
    public_audit = text("scripts/audit_public_source.py")

    # Stable reference-deployment bootstrap and strict policy fingerprint.
    require(len(project) <= MAX_PROJECT_INSTRUCTIONS_CHARS, f"project contract exceeds {MAX_PROJECT_INSTRUCTIONS_CHARS} characters: {len(project)}", errors)
    for phrase in (
        "BOOTSTRAP_CONTRACT_VERSION: 2",
        "project/POLICY_FINGERPRINT.txt",
        "sole policy/code/test/bootstrap source",
        "2:45 AM/PM Eastern Ops Brief",
        "BYHOUR=2,14;BYMINUTE=45;BYSECOND=0",
        "Receipt & Order Lifecycle",
        "Paid terminal miles are symmetric A↔B",
        "immutable UUID",
        "Do you want me to send this email?",
    ):
        require(phrase in project, f"project contract lacks: {phrase}", errors)
    require("POLICY_SOURCE_FINGERPRINT:" not in project, "project contract embeds a moving fingerprint", errors)

    fingerprint = text("project/POLICY_FINGERPRINT.txt").strip()
    require(re.fullmatch(r"[0-9a-f]{64}", fingerprint) is not None, "Git-side policy fingerprint is invalid", errors)
    if re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        actual = compute(root / "skill/ops-brief-policy")
        require(fingerprint == actual, f"policy fingerprint mismatch: expected {actual}", errors)

    # Public-source product contract.
    require(has(readme, "intentionally public", "starter/start_here.md", "public-source audit", "mutable operational state"), "README does not describe the public upstream/state boundary", errors)
    require("must be private" not in readme.lower(), "README still requires the public upstream to be private", errors)
    require(has(starter_readme, "public distribution boundary", "public or private", "reference implementation"), "starter README does not define a portable public boundary", errors)
    require(has(versioning, "simple fork path", "clean portable-snapshot path", "public and private are both supported"), "starter versioning lacks usable public installation paths", errors)
    require(has(shared, "public upstream", "mutable operational state", "public or private"), "shared feature workflow does not preserve public portability/state isolation", errors)
    require(has(dependencies, "public-source gate", "public or private", "provider metadata"), "starter dependencies lack repository visibility/source-audit handling", errors)
    require(has(generic, "repository visibility", "public source", "provider metadata"), "rendered starter policy cannot represent public/private source", errors)
    require("REPOSITORY_VISIBILITY" in generic, "starter policy template lacks repository visibility token", errors)
    require("MIT License" in license_text and "Permission is hereby granted" in license_text, "public source lacks a usable MIT license", errors)
    for ignored in (".env", "config.local.json", "*.sqlite"):
        require(ignored in gitignore, f".gitignore lacks public-source safety pattern: {ignored}", errors)

    require(has(public_audit, "audit_history", "SCAN_EXEMPT_PATHS", "CARD_CANDIDATE", "BLOCKED_FILENAMES"), "public source auditor lacks history/secret/card/file gates", errors)
    require("--history" in ci and "fetch-depth: 0" in ci, "CI does not run full-history public source audit", errors)
    for command in (
        "scripts/audit_public_source.py . --history",
        "scripts/audit_starter_privacy.py starter",
        "scripts/validate_repo.py .",
        "unittest discover -s tests",
        "unittest discover -s skill/ops-brief-policy/scripts",
        "starter/tools/validate_feature_manifest.py",
        "unittest discover -s starter/tests",
    ):
        require(command in ci, f"CI release gate lacks: {command}", errors)

    # Portable starter must not regress to a private-only deployment assumption.
    portable_surface = "\n".join((start, interview, dependencies, starter_readme, versioning, shared, generic))
    for stale in (
        "private git is required",
        "deployment repository must actually be private",
        "brand-new private repository",
        "must be private because",
    ):
        require(stale not in portable_surface.lower(), f"portable starter retains private-only rule: {stale}", errors)

    # Scheduler health is an evidence chain, not an undocumented timezone field.
    scheduler_surfaces = {
        "skill": skill,
        "maintenance": maintenance,
        "automation docs": automation,
        "starter dependencies": dependencies,
        "starter first boot": start,
        "starter interview": interview,
        "starter template": generic,
    }
    for label, surface in scheduler_surfaces.items():
        require(has(surface, "notification", "duplicate", "actual firing", "canonical"), f"{label} lacks scheduler notification/duplicate/observed-run evidence", errors)
        require("provider contract" in surface.lower(), f"{label} does not condition timezone metadata on provider semantics", errors)
    require("default_timezone" in skill and "default_timezone" in automation and "default_timezone" in dependencies, "scheduler policy does not neutralize ambiguous default_timezone metadata", errors)
    require("first external" in skill.lower() and "`Running`" in skill, "skill does not require an entry Run Log mutation", errors)
    require("Before Gmail" in brief and "`Running`" in brief, "brief workflow does not enter Run Log before downstream work", errors)
    require("subsequent actual run/Run Log timestamp" in pants, "failure policy cannot prove scheduler recovery", errors)

    # Symmetric paid terminal mileage for this reference deployment.
    require("Paid terminal mileage is symmetric" in skill, "canonical skill lacks symmetric terminal mileage", errors)
    require("same paid-mile value" in maintenance, "state maintenance lacks symmetric mileage upsert", errors)
    require("symmetric by canonical terminal pair" in brief, "brief workflow still treats terminal paid miles as directional", errors)
    require("standing policy is symmetric by terminal pair" in runtime, "runtime comments contradict pair mileage policy", errors)
    require("terminal_paid_miles_symmetric_by_pair: true" in compatibility and "terminal_paid_miles_directional: false" in compatibility, "legacy compatibility snapshot contradicts symmetric mileage", errors)
    require("for the current deployment it is symmetric" in data_platform, "future data-platform design contradicts current pair-mile policy", errors)
    require("never mirrors automatically" not in data_platform.lower(), "data-platform doc retains stale no-mirroring rule", errors)

    # Circuit breaker and safe failure behavior.
    for phrase in ("Retry is not mandatory", "Pants Filling With Shit Report", "never create hidden retry jobs"):
        require(phrase in skill, f"skill lacks failure boundary: {phrase}", errors)
    for phrase in ("same external operation fails twice", "Stop writes for the affected module", "Continue unrelated modules", "never blind-rerun"):
        require(phrase in pants, f"Pants Filling With Shit policy lacks: {phrase}", errors)

    # Receipt/order/asset/knowledge/finance safety.
    require(has(receipt, "active shopping list", "remove the fulfilled shopping row", "explicit owner statement", "separate reconciliation task", "cancellation with no supported replacement"), "receipt policy does not preserve active-shopping semantics", errors)
    require(has(fitment, "Investigation before queue", "Unique resolution may be established by exclusion", "card last-four"), "fitment/financial evidence policy is incomplete", errors)
    require(has(photo, "UPC/EAN/GTIN", "chat-local shadow receipt database"), "photo receipt intake is incomplete", errors)
    require(has(email, "Orders/History/<vendor-slug>/<order-number>", "FedEx, UPS, DHL and USPS", "90 calendar days", "open return, claim, dispute"), "email reconciliation/retention contract is incomplete", errors)
    require(has(asset, "immutable RFC 4122 UUID", "collision-resistant across deployments/family members", "manufacturer/OEM"), "asset identity contract is incomplete", errors)
    require(has(manual, "Manuals & Reference", "Knowledge Index", "canonical Drive link", "immutable RFC 4122 UUID"), "knowledge/manual contract is incomplete", errors)
    require(has(life, "Next-action planner", "Routine accountability", "Exercise / fitness organization", "School / study workflow"), "whole-life planning policy is incomplete", errors)
    require(has(reimbursement, "A reimbursement is not a merchant refund", "Net Household Cost"), "reimbursement contract is incomplete", errors)
    require(has(payment, "Awaiting Settlement", "Overcharged", "unmatched"), "payment reconciliation contract is incomplete", errors)
    require(has(contact, "do not reply", "Do you want me to send this email?"), "vendor contact safety is incomplete", errors)
    require("deleting the originating ChatGPT conversation" in chat, "chat portability does not make old chats disposable", errors)
    require(has(calendar, "Google Calendar event ID", "update the linked event in place", "order delivery dates/windows"), "calendar projection contract is incomplete", errors)

    # Calendar projection is allowed while per-record task fanout is forbidden.
    require("not a per-order automation" in automation_design.lower(), "automation design conflates Calendar Projection with per-order automation", errors)
    require("never creates per-order scheduled tasks" in automation_design.lower(), "automation design does not forbid per-order scheduled-task fanout", errors)

    # Identity/history contracts.
    require(has(household_schema, "Entity UUID", "immutable", "Friendly"), "household schema lacks immutable UUID/friendly-ID separation", errors)
    require("Status: superseded" in historical_audit, "historical feature audit is not explicitly superseded", errors)
    require("TRIP-" not in historical_audit and "MILE-" not in historical_audit, "historical audit copies mutable trip/mileage IDs into Git", errors)
    require("live canonical" in historical_audit.lower(), "historical audit does not redirect current-state readers to live authorities", errors)

    # Run-sheet importer learns reusable route pairs only.
    require("historical_occurrences_imported" in importer and "False" in importer, "run-sheet importer does not prohibit occurrence creation", errors)
    require("TERMINAL_ALIASES" in importer and '"I4C": "IRC"' in importer, "run-sheet importer lacks proven alias normalization", errors)
    require("route_pair_count" in importer and '"occurrences"' not in importer, "run-sheet importer still exports historical occurrence rows", errors)

    # Starter depth, adaptability, safety, and template completeness.
    questions = load_json("starter/questions.json")
    config = load_json("starter/config.example.json")
    rows = [q for section in questions.get("sections", []) if isinstance(section, dict) for q in section.get("questions", []) if isinstance(q, dict)]
    ids = [q.get("id") for q in rows]
    require(isinstance(questions, dict) and int(questions.get("version", 0)) >= 4, "starter questionnaire is not current public version", errors)
    require(len(rows) >= 80 and len(ids) == len(set(ids)), "starter questionnaire is missing whole-life depth or has duplicate IDs", errors)
    for qid in (
        "works_away_from_home",
        "accountability_domains",
        "routine_progression",
        "education_active",
        "study_home_away",
        "study_next_action_rule",
        "scheduler_timezone_integrity",
        "repository_visibility",
        "public_source_policy",
    ):
        require(qid in ids, f"starter questionnaire lacks adaptive field: {qid}", errors)

    require(len(start) < MAX_START_HERE_CHARS, f"START_HERE exceeds {MAX_START_HERE_CHARS} characters: {len(start)}", errors)
    for phrase in (
        "non-technical user",
        "Minimum Useful Setup",
        "Start now by asking only the four kickoff questions",
        "mark HOME/ROAD bypassed",
        "Driving/trucking",
        "active shopping list",
        "partial cancellation",
        "true replacement",
        "Calendar Projection",
        "immutable UUID",
        "Awaiting Settlement",
        "Pants Filling With Shit Report",
        "Do you want me to send this email?",
        "old chats are deleted",
        "automatically update validation, commit, and push",
    ):
        require(phrase.lower() in start.lower(), f"START_HERE lacks required onboarding behavior: {phrase}", errors)
    require(has(interview, "Do you regularly work away from home", "minimum viable version", "home versus away/on the road", "Exercise / fitness", "School / study", "what to do next"), "adaptive whole-life interview is incomplete", errors)

    require(isinstance(config, dict) and all(isinstance(k, str) and k.isupper() for k in config), "starter config keys must be uppercase tokens", errors)
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone", errors)
    require(config.get("REPOSITORY_VISIBILITY") == "USER_SELECTED_PUBLIC_OR_PRIVATE", "starter config lacks explicit repository visibility choice", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships reference schedule times", errors)
    template_tokens = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", generic))
    require(template_tokens <= set(config), "starter config does not cover every template token", errors)

    # Block known reference-deployment contamination from the entire portable starter surface.
    blocklist = [
        line.strip()
        for line in text("privacy/starter-blocklist.txt").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    starter_surface = "\n".join((start, interview, catalog, dependencies, starter_readme, versioning, shared, generic, json.dumps(questions)))
    for marker in blocklist:
        require(marker not in starter_surface, f"portable starter leaks reference-deployment marker: {marker}", errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
