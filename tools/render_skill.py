#!/usr/bin/env python3
"""Render the installable Ops Brief skill from sanitized repository sources."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any


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
        raise ValueError(f"Set {field} before rendering the skill.")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError(f"Invalid Google Sheet ID in {field}.")
    return f"https://docs.google.com/spreadsheets/d/{value}/edit"


def render(config_path: Path, output: Path) -> Path:
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")

    config = _load_config(config_path)
    source = Path(__file__).resolve().parents[1] / "skill"
    rendered = (source / "SKILL.md.tmpl").read_text(encoding="utf-8")
    for placeholder, field in PLACEHOLDERS.items():
        rendered = rendered.replace(placeholder, _sheet_url(config.get(field), field))
    if "{{" in rendered or "}}" in rendered:
        raise ValueError("Unresolved template placeholder remains in SKILL.md.")

    shutil.copytree(source, output)
    template_path = output / "SKILL.md.tmpl"
    (output / "SKILL.md").write_text(rendered, encoding="utf-8")
    template_path.unlink()
    return output / "SKILL.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rendered = render(args.config, args.output)
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
