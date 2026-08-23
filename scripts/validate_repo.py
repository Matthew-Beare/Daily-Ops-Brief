#!/usr/bin/env python3
"""Validate coherent LyfeOS public-release, starter, and reference-deployment contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from policy_fingerprint import compute

REQUIRED = (
    ".gitignore", "LICENSE", "README.md", ".github/workflows/ci.yml",
    "project/INSTRUCTIONS.md.tmpl", "project/POLICY_FINGERPRINT.txt",
    "policy/ops-brief-policy.yaml",
    "docs/automation-contracts.md", "docs/automation-design.md",
    "docs/data-platform-grafana.md", "docs/feature-audit-2026-08-22.md",
    "docs/household-financial-reconciliation.md", "docs/lyfeos-data-model.md",
    "starter/README.md", "starter/START_HERE.md", "starter/LIFE_INTERVIEW.md",
    "starter/MODULE_CATALOG.md", "starter/DEPENDENCIES.md", "starter/VERSIONING.md",
    "starter/PERSONAL_FORK_LIFECYCLE.md", "starter/CAPABILITY_DISCOVERY.md",
    "starter/GIT_STATE_MODEL.md", "starter/SHARED_FEATURE_WORKFLOW.md",
    "starter/config.example.json", "starter/questions.json", "starter/INSTRUCTIONS.md.tmpl",
    "starter/features/meal-planning/feature.json", "starter/features/meal-planning/FEATURE.md",
    "starter/features/appointment-reconciliation/feature.json", "starter/features/appointment-reconciliation/FEATURE.md",
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
    "scripts/import_run_sheet.py", "scripts/audit_public_source.py",
    "scripts/audit_starter_privacy.py", "privacy/starter-blocklist.txt",
)
MAX_PROJECT_INSTRUCTIONS_CHARS = 3_000
MAX_START_HERE_CHARS = 12_000


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def all_terms(value: str, *terms: str) -> bool:
    lower = value.lower()
    return all(term.lower() in lower for term in terms)


def any_term(value: str, *terms: str) -> bool:
    lower = value.lower()
    return any(term.lower() in lower for term in terms)


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED:
        require((root / relative).is_file(), f"missing required file: {relative}", errors)
    if errors:
        return errors

    def text(path: str) -> str:
        return (root / path).read_text(encoding="utf-8")

    def load_json(path: str):
        try:
            return json.loads(text(path))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {path}: {exc}")
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
    historical = text("docs/feature-audit-2026-08-22.md")
    household = text("docs/household-financial-reconciliation.md")
    compatibility = text("policy/ops-brief-policy.yaml")

    start = text("starter/START_HERE.md")
    interview = text("starter/LIFE_INTERVIEW.md")
    catalog = text("starter/MODULE_CATALOG.md")
    deps = text("starter/DEPENDENCIES.md")
    starter_readme = text("starter/README.md")
    versioning = text("starter/VERSIONING.md")
    lifecycle = text("starter/PERSONAL_FORK_LIFECYCLE.md")
    discovery = text("starter/CAPABILITY_DISCOVERY.md")
    git_state = text("starter/GIT_STATE_MODEL.md")
    shared = text("starter/SHARED_FEATURE_WORKFLOW.md")
    generic = text("starter/INSTRUCTIONS.md.tmpl")
    meal_feature = text("starter/features/meal-planning/FEATURE.md")
    appointment_feature = text("starter/features/appointment-reconciliation/FEATURE.md")
    importer = text("scripts/import_run_sheet.py")
    public_audit = text("scripts/audit_public_source.py")

    # Reference bootstrap/fingerprint remain untouched by starter architecture.
    require(len(project) <= MAX_PROJECT_INSTRUCTIONS_CHARS, f"project contract exceeds {MAX_PROJECT_INSTRUCTIONS_CHARS} characters: {len(project)}", errors)
    for term in (
        "BOOTSTRAP_CONTRACT_VERSION: 2", "project/POLICY_FINGERPRINT.txt",
        "sole policy/code/test/bootstrap source", "2:45 AM/PM Eastern Ops Brief",
        "BYHOUR=2,14;BYMINUTE=45;BYSECOND=0", "Receipt & Order Lifecycle",
        "Paid terminal miles are symmetric A↔B", "immutable UUID",
        "Do you want me to send this email?",
    ):
        require(term in project, f"project contract lacks: {term}", errors)
    fingerprint = text("project/POLICY_FINGERPRINT.txt").strip()
    require(bool(re.fullmatch(r"[0-9a-f]{64}", fingerprint)), "Git-side policy fingerprint is invalid", errors)
    if re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        expected = compute(root / "skill/ops-brief-policy")
        require(fingerprint == expected, f"policy fingerprint mismatch: expected {expected}", errors)

    # Public upstream vs private Git-native starter vs reference-deployment exception.
    require(all_terms(readme, "intentionally public", "starter/start_here.md", "private git", "mutable operational state", "reference deployment", "public-source audit"), "README lacks explicit upstream/starter/reference state boundaries", errors)
    require(all_terms(starter_readme, "private personal git", "public upstream", "git state", "reference implementation"), "starter README lacks private Git-state/public-upstream contract", errors)
    require(all_terms(git_state, "canonical personal state authority", "private", "event files are immutable", "snapshot", "push by fast-forward only", "read back", "never force-push", "state/"), "Git state model is incomplete", errors)
    require(all_terms(versioning, "private personal-lineage path", "public github fork path", "code only", "clean portable-snapshot path", "state transaction"), "starter versioning lacks safe lineage/state paths", errors)
    require(all_terms(lifecycle, "canonical source of truth", "personal state", "private", "first-boot state/config checkpoint", "fast-forward only"), "personal fork lifecycle is not Git-state authoritative", errors)
    require(all_terms(shared, "public upstream", "private user deployment", "state/", "synthetic fixtures", "publication authority"), "shared feature workflow does not isolate private state", errors)
    require(all_terms(discovery, "private deployment git", "optional evidence adapter", "one canonical personal-state authority: private git"), "capability discovery does not treat providers as adapters around Git", errors)
    require(all_terms(deps, "private git", "canonical personal-state authority", "provider metadata", "public-source", "fast-forward only"), "starter dependencies lack Git-state/privacy contract", errors)
    require(all_terms(generic, "canonical personal state", "private deployment repository", "provider metadata", "state/", "fast-forward only"), "starter template cannot represent Git-native personal state", errors)
    require("{{REPOSITORY_VISIBILITY}}" in generic, "starter template lacks REPOSITORY_VISIBILITY", errors)

    config = load_json("starter/config.example.json")
    require(config.get("TIMEZONE") == "REQUIRED_IANA_TIMEZONE", "starter config ships a production timezone", errors)
    require(config.get("STATE_STORE") == "PRIVATE_GIT_REPOSITORY/state", "starter config does not make Git state canonical", errors)
    require(config.get("REPOSITORY_VISIBILITY") == "PRIVATE_REQUIRED_WHEN_PERSONAL_STATE_IS_ENABLED", "starter config does not protect personal Git state", errors)
    require(config.get("GIT_STATE_MODEL") == "IMMUTABLE_EVENTS_PLUS_DERIVED_SNAPSHOTS", "starter config lacks event/snapshot state model", errors)
    require("02:45" not in json.dumps(config) and "14:45" not in json.dumps(config), "starter config ships reference schedule times", errors)
    require(isinstance(config, dict) and all(isinstance(k, str) and k.isupper() for k in config), "starter config keys must be uppercase", errors)
    template_tokens = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", generic))
    require(template_tokens <= set(config), "starter config does not cover template tokens", errors)

    meal_manifest = load_json("starter/features/meal-planning/feature.json")
    appointment_manifest = load_json("starter/features/appointment-reconciliation/feature.json")
    for name, manifest in (("meal planning", meal_manifest), ("appointment reconciliation", appointment_manifest)):
        boundary = manifest.get("data_boundary", {}) if isinstance(manifest, dict) else {}
        require(boundary.get("source_contains_personal_data") is False, f"{name} portable source contains personal data", errors)
        require(boundary.get("runtime_state") == "deployment-local", f"{name} does not declare deployment-local Git state", errors)
    require(all_terms(meal_feature, "private git", "do you want help with meal planning?", "shopping intent is not purchase history", "commit"), "meal planning feature lacks Git-backed state/import contract", errors)
    require(all_terms(appointment_feature, "private git", "read the calendar event back", "read the git state back", "event id", "reminder", "source linkage"), "appointment feature lacks provider+Git verification transaction", errors)

    # Public upstream release gates.
    require("MIT License" in license_text and "Permission is hereby granted" in license_text, "public source lacks MIT reuse permission", errors)
    for pattern in (".env", "config.local.json", "*.sqlite"):
        require(pattern in gitignore, f".gitignore lacks safety pattern: {pattern}", errors)
    require(all_terms(public_audit, "audit_history", "scan_exempt_paths", "card_candidate", "blocked_filenames"), "public-source auditor lacks history/credential/card gates", errors)
    require("fetch-depth: 0" in ci and "audit_public_source.py . --history" in ci, "CI does not audit reachable Git history", errors)
    for term in (
        "audit_starter_privacy.py starter", "validate_repo.py .",
        "unittest discover -s tests", "unittest discover -s skill/ops-brief-policy/scripts",
        "validate_feature_manifest.py", "unittest discover -s starter/tests",
    ):
        require(term in ci, f"CI release gate lacks: {term}", errors)

    # Scheduler evidence: reference and starter both require definition/readback/notification/dedupe/observed execution.
    scheduler_surfaces = {
        "skill": skill, "maintenance": maintenance, "automation docs": automation,
        "starter dependencies": deps, "starter first boot": start,
        "starter interview": interview, "starter template": generic,
    }
    for label, surface in scheduler_surfaces.items():
        require(all_terms(surface, "notification", "duplicate", "canonical"), f"{label} lacks scheduler readback evidence", errors)
        require(any_term(surface, "actual firing", "actual scheduled firing", "observed firing", "observed execution"), f"{label} lacks observed scheduler execution evidence", errors)
        require(any_term(surface, "provider contract", "provider/tool contract"), f"{label} does not condition provider metadata on documented semantics", errors)
    require("default_timezone" in skill and "default_timezone" in automation and "default_timezone" in deps, "scheduler policy does not neutralize ambiguous default_timezone metadata", errors)
    require(all_terms(skill, "first external", "`Running`", "Run Log"), "skill does not require early Run Log entry", errors)
    require(all_terms(brief, "Before Gmail", "`Running`", "Run Log"), "brief workflow does not enter Run Log before downstream work", errors)
    require(all_terms(pants, "subsequent actual run/Run Log timestamp"), "failure policy cannot prove scheduler recovery", errors)

    # Reference-deployment invariants remain unchanged.
    require(all_terms(skill, "Keep mutable operational state in canonical Sheets", "retained files/evidence in canonical Drive"), "reference skill lost Sheets/Drive state authority", errors)
    require(all_terms(skill, "paid terminal mileage", "symmetric", "explicit", "exception"), "skill lacks symmetric paid-mile policy", errors)
    require(all_terms(maintenance, "same paid-mile value", "both", "unless"), "state maintenance lacks symmetric paid-mile upsert", errors)
    require(all_terms(brief, "symmetric", "terminal pair"), "brief workflow lacks pair-symmetric paid-mile semantics", errors)
    require(all_terms(runtime, "policy is symmetric by terminal pair", "both columns", "exception"), "runtime comments contradict pair-mile policy", errors)
    require("terminal_paid_miles_symmetric_by_pair: true" in compatibility and "terminal_paid_miles_directional: false" in compatibility, "legacy compatibility snapshot contradicts symmetric paid miles", errors)
    require(all_terms(data_platform, "symmetric", "terminal") and "never mirrors automatically" not in data_platform.lower(), "future data model contradicts current pair-mile policy", errors)

    require(all_terms(skill, "Retry is not mandatory", "Pants Filling With Shit Report", "never create hidden retry jobs"), "skill lacks bounded failure policy", errors)
    require(all_terms(pants, "same external operation fails twice", "Stop writes for the affected module", "Continue unrelated modules", "never blind-rerun"), "Pants policy is not module-scoped/fail-fast", errors)

    # Purchase/evidence/identity/finance/communication reference contracts.
    require(all_terms(receipt, "active shopping list", "remove the fulfilled shopping row", "explicit owner statement", "separate reconciliation task", "cancellation with no supported replacement"), "receipt/shopping contract incomplete", errors)
    require(all_terms(fitment, "Investigation before queue", "Unique resolution may be established by exclusion", "card last-four"), "fitment evidence contract incomplete", errors)
    require(all_terms(photo, "UPC/EAN/GTIN", "chat-local shadow receipt database"), "photo intake contract incomplete", errors)
    require(all_terms(email, "Orders/History/<vendor-slug>/<order-number>", "FedEx, UPS, DHL and USPS", "90 calendar days", "open return, claim, dispute"), "email retention/reconciliation contract incomplete", errors)
    require(all_terms(asset, "immutable RFC 4122 UUID", "collision-resistant across deployments/family members", "manufacturer/OEM"), "asset identity contract incomplete", errors)
    require(all_terms(manual, "Manuals & Reference", "Knowledge Index", "canonical Drive link", "immutable RFC 4122 UUID"), "knowledge/manual contract incomplete", errors)
    require(all_terms(life, "Next-action planner", "Routine accountability", "Exercise / fitness organization", "School / study workflow"), "whole-life planning contract incomplete", errors)
    require(all_terms(reimbursement, "A reimbursement is not a merchant refund", "Net Household Cost"), "reimbursement contract incomplete", errors)
    require(all_terms(payment, "Awaiting Settlement", "Overcharged", "unmatched"), "payment reconciliation contract incomplete", errors)
    require(all_terms(contact, "do not reply", "Do you want me to send this email?"), "vendor contact safety incomplete", errors)
    require("deleting the originating ChatGPT conversation" in chat, "chat portability contract incomplete", errors)
    require(all_terms(calendar, "Google Calendar event ID", "update the linked event in place", "order delivery dates/windows"), "Calendar Projection contract incomplete", errors)
    require(all_terms(automation_design, "not a per-order automation", "never creates per-order scheduled tasks"), "automation design conflates Calendar Projection with task fanout", errors)

    # Identity/history/import boundaries.
    require(all_terms(household, "Entity UUID", "immutable", "Friendly"), "household schema lacks UUID/friendly-ID separation", errors)
    require("Status: superseded" in historical and "TRIP-" not in historical and "MILE-" not in historical and "live canonical" in historical.lower(), "historical audit can be mistaken for live mutable state", errors)
    require("historical_occurrences_imported" in importer and "False" in importer, "run-sheet importer may create historical occurrences", errors)
    require("TERMINAL_ALIASES" in importer and '"I4C": "IRC"' in importer, "run-sheet importer lacks proven alias normalization", errors)
    require("route_pair_count" in importer and '"occurrences"' not in importer, "run-sheet importer exports occurrence rows", errors)

    # Starter must be bounded, adaptive, deep, and discovery-driven.
    questions = load_json("starter/questions.json")
    rows = [q for section in questions.get("sections", []) if isinstance(section, dict) for q in section.get("questions", []) if isinstance(q, dict)]
    ids = [q.get("id") for q in rows]
    require(isinstance(questions, dict) and int(questions.get("version", 0)) >= 5, "starter questionnaire version is stale", errors)
    require(len(rows) >= 100 and len(ids) == len(set(ids)), "starter questionnaire lacks depth or has duplicate IDs", errors)
    for qid in (
        "works_away_from_home", "accountability_domains", "routine_progression",
        "education_active", "study_home_away", "study_next_action_rule",
        "scheduler_timezone_integrity", "repository_visibility", "public_source_policy",
        "employment_status", "retired_support", "hiking_outdoors", "vacation_planning",
        "meal_planning_help", "existing_meal_plans", "fitness_wearable",
        "medical_event_tracking", "appointment_email_auto_update", "git_state_commit_policy",
    ):
        require(qid in ids, f"starter questionnaire lacks field: {qid}", errors)
    require(len(start) < MAX_START_HERE_CHARS, f"START_HERE exceeds {MAX_START_HERE_CHARS} characters: {len(start)}", errors)
    for term in (
        "non-technical user", "Minimum Useful Setup", "Start now by asking only the four kickoff questions",
        "mark HOME/ROAD bypassed", "Driving/trucking", "active shopping list",
        "partial cancellation", "true replacement", "Calendar Projection", "immutable UUID",
        "Awaiting Settlement", "Pants Filling With Shit Report", "Do you want me to send this email?",
        "old chats are deleted", "Do you want help with meal planning?", "private Git",
        "automatically validates, commits, pushes",
    ):
        require(term.lower() in start.lower(), f"START_HERE lacks behavior: {term}", errors)
    require(all_terms(interview, "Do you regularly work away from home", "minimum viable version", "home versus away/on the road", "Exercise / fitness", "School / study", "what to do next", "retired", "Do you want help with meal planning?", "private Git"), "whole-life interview incomplete", errors)

    # Portable starter must not leak current reference deployment markers.
    markers = [line.strip() for line in text("privacy/starter-blocklist.txt").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    starter_surface = "\n".join((start, interview, catalog, deps, starter_readme, versioning, lifecycle, discovery, git_state, shared, generic, json.dumps(questions)))
    for marker in markers:
        require(marker not in starter_surface, f"portable starter leaks reference marker: {marker}", errors)

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
