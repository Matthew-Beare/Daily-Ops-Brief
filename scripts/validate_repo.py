#!/usr/bin/env python3
"""Validate repository authority, recovery, scheduler, starter, and privacy contracts.

This validator intentionally checks cross-file agreement. A magic phrase appearing in
one document is not proof that the surrounding policy is coherent.
"""

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
    "scripts/audit_starter_privacy.py",
    "privacy/starter-blocklist.txt",
)
MAX_PROJECT_INSTRUCTIONS_CHARS = 3_000
MAX_START_HERE_CHARS = 9_000


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def contains_all(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return all(phrase.lower() in lowered for phrase in phrases)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        require((root / relative).is_file(), f"missing required file: {relative}", errors)
    if errors:
        return errors

    def text(relative: str) -> str:
        return (root / relative).read_text(encoding="utf-8")

    def json_file(relative: str):
        try:
            return json.loads(text(relative))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {relative}: {exc}")
            return {}

    project = text("project/INSTRUCTIONS.md.tmpl")
    readme = text("README.md")
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

    # Stable Project bootstrap and strict Git-side fingerprint.
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

    # Scheduler integrity is a chain, not an undocumented timezone field.
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
        require(
            contains_all(surface, ("notification", "duplicate", "actual firing" if label != "maintenance" else "actual firing")),
            f"{label} lacks scheduler notification/duplicate/observed-run evidence",
            errors,
        )
        require("canonical" in surface.lower(), f"{label} lacks canonical-time scheduling language", errors)
    for surface_name, surface in (("skill", skill), ("maintenance", maintenance), ("automation docs", automation), ("starter dependencies", dependencies), ("starter first boot", start), ("starter interview", interview), ("starter template", generic)):
        require("provider contract" in surface.lower(), f"{surface_name} does not condition provider timezone metadata on documented semantics", errors)
    require("default_timezone" in skill and "default_timezone" in automation and "default_timezone" in dependencies, "scheduler policy does not explicitly neutralize ambiguous default_timezone metadata", errors)
    require("first external" in skill.lower() and "Running" in skill, "skill does not require an entry Run Log mutation", errors)
    require("Before Gmail" in brief and "`Running`" in brief and "same" in brief.lower(), "brief workflow does not create/finalize one Run Log row around downstream work", errors)
    require("subsequent actual run/Run Log timestamp" in pants, "failure policy cannot prove scheduler recovery", errors)
    for forbidden in (
        "provider stored/default/execution timezone equals",
        "stored execution timezone matches the canonical timezone as well as the intended local schedule",
    ):
        require(forbidden.lower() not in (skill + start + interview + generic).lower(), f"stale unconditional scheduler rule remains: {forbidden}", errors)

    # Symmetric terminal paid mileage must agree everywhere, while geometry/runtime may stay directional.
    require("Paid terminal mileage is symmetric" in skill, "canonical skill lacks symmetric terminal mileage", errors)
    require("same paid-mile value" in maintenance, "state maintenance lacks symmetric mileage upsert", errors)
    require("symmetric by canonical terminal pair" in brief, "brief workflow still treats terminal paid miles as directional", errors)
    require("standing policy is symmetric by terminal pair" in runtime, "runtime comments contradict pair mileage policy", errors)
    require("terminal_paid_miles_symmetric_by_pair: true" in compatibility and "terminal_paid_miles_directional: false" in compatibility, "legacy compatibility snapshot contradicts symmetric mileage", errors)
    require("for the current deployment it is symmetric" in data_platform, "future data-platform design contradicts current pair-mile policy", errors)
    require("never mirrors automatically" not in data_platform.lower(), "data-platform doc retains stale no-mirroring rule", errors)
    require("Directional terminal paid-mile fields are learned evidence only" not in brief, "brief workflow retains stale directional paid-mile rule", errors)

    # Fail-fast recovery must stop the affected module, not build retry machinery.
    for phrase in ("Retry is not mandatory", "Pants Filling With Shit Report", "never create hidden retry jobs"):
        require(phrase in skill, f"skill lacks failure boundary: {phrase}", errors)
    for phrase in ("same external operation fails twice", "Stop writes for the affected module", "Continue unrelated modules", "never blind-rerun"):
        require(phrase in pants, f"Pants Filling With Shit policy lacks: {phrase}", errors)

    # Receipt/order/asset/knowledge/finance safety.
    require(contains_all(receipt, ("active shopping list", "remove the fulfilled shopping row", "explicit owner statement", "separate reconciliation task", "cancellation with no supported replacement")), "receipt policy does not preserve active-shopping semantics", errors)
    require(contains_all(fitment, ("Investigation before queue", "Unique resolution may be established by exclusion", "card last-four")), "fitment/financial evidence policy is incomplete", errors)
    require(contains_all(photo, ("UPC/EAN/GTIN", "chat-local shadow receipt database")), "photo receipt intake is incomplete", errors)
    require(contains_all(email, ("Orders/History/<vendor-slug>/<order-number>", "FedEx, UPS, DHL and USPS", "90 calendar days", "open return, claim, dispute")), "email reconciliation/retention contract is incomplete", errors)
    require(contains_all(asset, ("immutable RFC 4122 UUID", "collision-resistant across deployments/family members", "manufacturer/OEM")), "asset identity contract is incomplete", errors)
    require(contains_all(manual, ("Manuals & Reference", "Knowledge Index", "canonical Drive link", "immutable RFC 4122 UUID")), "knowledge/manual contract is incomplete", errors)
    require(contains_all(life, ("Next-action planner", "Routine accountability", "Exercise / fitness organization", "School / study workflow")), "whole-life planning policy is incomplete", errors)
    require(contains_all(reimbursement, ("A reimbursement is not a merchant refund", "Net Household Cost")), "reimbursement contract is incomplete", errors)
    require(contains_all(payment, ("Awaiting Settlement", "Overcharged", "unmatched")), "payment reconciliation contract is incomplete", errors)
    require(contains_all(contact, ("do not reply", "Do you want me to send this email?")), "vendor contact safety is incomplete", errors)
    require("deleting the originating ChatGPT conversation" in chat, "chat portability does not make old chats disposable", errors)
    require(contains_all(calendar, ("Google Calendar event ID", "update the linked event in place", "order delivery dates/windows")), "calendar projection contract is incomplete", errors)

    # Calendar projection is permitted; automation fan-out is not.
    require("not a per-order automation" in automation_design.lower(), "automation design conflates calendar projection with per-order automation", errors)
    require("never creates per-order scheduled tasks" in automation_design.lower(), "automation design does not forbid per-order task fanout", errors)

    # Identity schema must keep UUID primary and friendly IDs secondary.
    require("Entity UUID" in household_schema and "immutable" in household_schema and "Friendly" in household_schema, "household schema lacks immutable UUID/friendly-ID separation", errors)

    # Historical docs must not be mistaken for live state or leak mutable runtime snapshots in the current tree.
    require("Status: superseded" in historical_audit, "historical feature audit is not explicitly superseded", errors)
    require("TRIP-" not in historical_audit and "MILE-" not in historical_audit, "historical audit still copies mutable trip/mileage IDs into Git", errors)
    require("live canonical" in historical_audit.lower(), "historical audit does not redirect readers to live authorities", errors)

    # Repository privacy is a provider-state gate, not a prose assertion.
    require(contains_all(readme, ("must be private", "provider metadata", "stop provisioning")), "README does not gate deployment on actual private repository state", errors)
    require("This repository is private" not in readme, "README makes an unverified repository-visibility claim", errors)
    require(contains_all(dependencies, ("private", "provider metadata")), "starter dependencies do not verify actual private repository state", errors)
    require(contains_all(generic, ("must actually be private", "provider metadata")), "generated starter policy does not enforce private repository state", errors)

    # The first-beta installation path must exist even before a standalone starter repo exists.
    require(contains_all(versioning, ("standalone", "brand-new private", "pinned", "snapshot")), "starter versioning has no real pre-release first-user path", errors)
    require("do not fork" in versioning.lower() or "never fork" in versioning.lower(), "starter versioning may expose production repository history", errors)
    require("standalone" in shared.lower(), "shared feature workflow does not distinguish the standalone starter boundary", errors)

    # Importer must learn reusable pairs without manufacturing historical occurrences.
    require("historical_occurrences_imported" in importer and "False" in importer, "run-sheet importer does not prohibit occurrence creation", errors)
    require("TERMINAL_ALIASES" in importer and '"I4C": "IRC"' in importer, "run-sheet importer lacks proven alias normalization", errors)
    require("route_pair_count" in importer and '"occurrences"' not in importer, "run-sheet importer still exports historical occurrence rows", errors)

    # Starter is adaptive, deep enough to discover whole-life workflows, and sanitized.
    questions = json_file("starter/questions.json")
    config = json_file("starter/config.example.json")
    rows = [q for section in questions.get("sections", []) if isinstance(section, dict) for q in section.get("questions", []) if isinstance(q, dict)]
    ids = [q.get("id") for q in rows]
    require(len(rows) >= 80 and len(ids) == len(set(ids)), "starter questionnaire is missing whole-life depth or has duplicate IDs", errors)
    for qid in ("works_away_from_home", "accountability_domains", "routine_progression", "education_active", "study_home_away", "study_next_action_rule", "scheduler_timezone_integrity"):
        require(qid in ids, f"starter questionnaire lacks adaptive field: {qid}", errors)
    scheduler_questions = " ".join(str(q.get("prompt", "")) for q in rows if "scheduler" in str(q.get("id", "")) or "scheduled" in str(q.get("id", "")))
    require(contains_all(scheduler_questions, ("notification", "actual")), "starter scheduler questions do not collect notification/observed-run evidence", errors)

    require(len(start) < MAX_START_HERE_CHARS, f"START_HERE exceeds {MAX_START_HERE_CHARS} characters: {len(start)}", errors)
    for phrase in ("Minimum Useful Setup", "Start now by asking only the four kickoff questions", "non-technical user", "exactly what to click", "automatically update validation, commit, and push", "Dependency gate", "Pants Filling With Shit Report", "partial cancellation", "Calendar Projection", "immutable UUID", "Awaiting Settlement", "Do you want me to send this email?", "old chats are deleted", "work away from home", "whole-life interview", "active shopping list"):
        require(phrase.lower() in start.lower(), f"starter onboarding lacks: {phrase}", errors)
    for phrase in ("Do you regularly work away from home", "minimum viable version", "home versus away/on the road", "Exercise / fitness", "School / study", "what to do next", "stored/execution timezone"):
        require(phrase.lower() in interview.lower(), f"adaptive life interview lacks: {phrase}", errors)
    require("four" in starter_readme.lower(), "starter README has an inconsistent stock-behavior count", errors)
    require("GitHub side" in dependencies and "ChatGPT side" in dependencies and "Installed GitHub Apps" in dependencies, "dependency guide lacks two-sided GitHub setup", errors)
    require("Manuals and reference library" in catalog and "immutable collision-resistant UUID" in catalog, "module catalog lacks manual/UUID enrollment", errors)
    require("Shopping and procurement reconciliation" in catalog, "module catalog lacks shopping/procurement enrollment", errors)
    require("Personal accountability and routines" in catalog and "Education and study coach" in catalog, "module catalog lacks whole-life accountability/study modules", errors)

    starter_surface = start + interview + catalog + dependencies + versioning + shared + json.dumps(questions)
    for private_marker in ("Matthew-Beare", "jbeare92", "1pHkTdCx", "Pig Pet", "Mazda Miata", "Subaru WRX", "Civic Type R"):
        require(private_marker not in starter_surface, f"starter leaks user-specific marker: {private_marker}", errors)

    require(isinstance(config, dict) and all(isinstance(k, str) and k.isupper() for k in config), "starter config keys must be uppercase tokens", errors)
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships production schedule times", errors)
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