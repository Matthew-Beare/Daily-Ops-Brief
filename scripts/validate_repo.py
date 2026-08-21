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
    "starter/README.md",
    "starter/config.example.json",
    "starter/questions.json",
    "starter/INSTRUCTIONS.md.tmpl",
    "skill/ops-brief-policy/SKILL.md",
    "skill/ops-brief-policy/references/receipt-ingestion.md",
    "skill/ops-brief-policy/references/state-maintenance.md",
)

MAX_PROJECT_INSTRUCTIONS_CHARS = 4_000


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

    require(
        len(project) <= MAX_PROJECT_INSTRUCTIONS_CHARS,
        f"project contract exceeds {MAX_PROJECT_INSTRUCTIONS_CHARS} characters: {len(project)}",
        errors,
    )

    require("Keep exactly one active Ops Brief automation" in project, "project contract does not require one active Ops Brief automation", errors)
    require("BYHOUR=2,14;BYMINUTE=45;BYSECOND=0" in project, "project contract is missing the twice-daily RRULE", errors)
    require("exactly one active Ops Brief automation" in skill, "skill invariant is not the one-task design", errors)
    require("receipt-ingestion.md" in skill, "skill does not route receipt ingestion", errors)
    require("Purchase & Receipt Archive" in project, "project contract is missing purchase authority", errors)
    require("Receipt & Order Lifecycle" in project, "project contract is missing the consolidated receipt lifecycle task", errors)
    require("BYHOUR=1,13;BYMINUTE=45" in project, "project contract is missing the receipt lifecycle RRULE", errors)
    require("Audit gate" in project, "project contract is missing the receipt integrity gate", errors)
    require("Order Events" in skill, "skill does not preserve lifecycle history", errors)
    require("Classification Queue" in skill, "skill does not route unknown purchase classification", errors)
    require("To consolidate a healthy legacy AM/PM pair" in maintenance, "state maintenance lacks the migration transaction", errors)
    require("Keep exactly two active Ops Brief" not in project + skill + maintenance, "legacy two-task invariant remains", errors)

    match = re.search(r"POLICY_SOURCE_FINGERPRINT: sha256:([0-9a-f]{64})", project)
    require(match is not None, "project contract has no valid policy fingerprint", errors)
    if match:
        actual = compute(root / "skill/ops-brief-policy")
        require(match.group(1) == actual, f"policy fingerprint mismatch: expected {actual}", errors)

    questions = json.loads((root / "starter/questions.json").read_text(encoding="utf-8"))
    config = json.loads((root / "starter/config.example.json").read_text(encoding="utf-8"))
    question_rows = [question for section in questions.get("sections", []) for question in section.get("questions", [])]
    ids = [row.get("id") for row in question_rows]
    require(len(question_rows) >= 40, "starter questionnaire is not deep enough", errors)
    require(len(ids) == len(set(ids)), "starter questionnaire contains duplicate IDs", errors)
    require(all(isinstance(key, str) and key.isupper() for key in config), "starter config keys must be uppercase tokens", errors)

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
