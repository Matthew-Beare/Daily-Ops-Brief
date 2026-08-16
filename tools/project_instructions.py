#!/usr/bin/env python3
"""Render project instructions and guard them against policy-source drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_SOURCE_GLOBS = (
    "docs/OPERATIONS.md",
    "project/INSTRUCTIONS.md.tmpl",
    "schemas/google-sheets.json",
    "skill/SKILL.md.tmpl",
    "skill/references/*.md",
    "skill/scripts/*.py",
)
PLACEHOLDERS = {
    "{{OPS_STATUS_REGISTER_URL}}": "ops_status_register_id",
    "{{MILEAGE_PAY_TRACKER_URL}}": "mileage_pay_tracker_id",
}


def _load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("Configuration root must be an object.")
    return value


def _sheet_url(sheet_id: Any, field: str) -> str:
    value = str(sheet_id or "").strip()
    if not value or value == "SET_ME":
        raise ValueError(f"Set {field} before rendering project instructions.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError(f"Invalid Google Sheet ID in {field}.")
    return f"https://docs.google.com/spreadsheets/d/{value}/edit"


def policy_sources(root: Path = ROOT) -> list[Path]:
    paths: set[Path] = set()
    for pattern in POLICY_SOURCE_GLOBS:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    if not paths:
        raise ValueError("No policy sources found.")
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def policy_fingerprint(root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for path in policy_sources(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def expected_fingerprint(root: Path = ROOT) -> str:
    value = (root / "project" / "POLICY_SOURCE.sha256").read_text(
        encoding="utf-8"
    ).strip()
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError("project/POLICY_SOURCE.sha256 is not a lowercase SHA-256 digest.")
    return value


def check(root: Path = ROOT) -> str:
    expected = expected_fingerprint(root)
    actual = policy_fingerprint(root)
    if actual != expected:
        raise ValueError(
            "Project instructions require policy review: "
            f"expected {expected}, calculated {actual}."
        )
    return actual


def render(config_path: Path, output: Path, root: Path = ROOT) -> Path:
    fingerprint = check(root)
    config = _load_config(config_path)
    text = (root / "project" / "INSTRUCTIONS.md.tmpl").read_text(
        encoding="utf-8"
    )
    for placeholder, field in PLACEHOLDERS.items():
        text = text.replace(placeholder, _sheet_url(config.get(field), field))
    text = text.replace("{{POLICY_SOURCE_SHA256}}", fingerprint)
    if "{{" in text or "}}" in text:
        raise ValueError("Unresolved template placeholder remains in project instructions.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="Fail when policy sources were not reviewed.")
    subparsers.add_parser("fingerprint", help="Print the current policy fingerprint.")
    render_parser = subparsers.add_parser(
        "render", help="Render the complete copy-paste project instructions."
    )
    render_parser.add_argument("--config", required=True, type=Path)
    render_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "check":
        print(check())
    elif args.command == "fingerprint":
        print(policy_fingerprint())
    else:
        print(render(args.config, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
