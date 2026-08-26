#!/usr/bin/env python3
"""Render a plain-language Markdown report for a paused MIRA upstream source conflict."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(report: dict) -> str:
    help_data = report.get("user_help") or {}
    conflicts = report.get("conflicts") or []
    lines = [
        f"# {help_data.get('headline', 'MIRA update needs a decision')}",
        "",
        help_data.get("plain_language", "MIRA found a source conflict and paused the update."),
        "",
        f"**Your current version is safe.** {help_data.get('your_data_is_safe', 'Nothing was automatically overwritten.')}",
        "",
        "## Files that need a decision",
        "",
    ]
    if conflicts:
        lines.extend(f"- `{path}`" for path in conflicts)
    else:
        lines.append("- MIRA could not isolate a single filename; ask MIRA to inspect the update branch before editing anything.")
    lines += ["", "## What to do", ""]
    for index, step in enumerate(help_data.get("what_you_should_do") or [], start=1):
        lines.append(f"{index}. {step}")
    lines += [
        "",
        "## Safe default",
        "",
        help_data.get("recommended_default", "Preserve user-created behavior unless the user explicitly chooses otherwise."),
        "",
        "## Do not do this",
        "",
    ]
    lines.extend(f"- {item}" for item in help_data.get("do_not_do") or [])
    lines += [
        "",
        "## Technical reference (normally you can ignore this)",
        "",
        f"- Your current source: `{report.get('target_sha', '')}`",
        f"- Incoming MIRA source: `{report.get('upstream_sha', '')}`",
        "",
        "Ask MIRA in ChatGPT: **Resolve this MIRA update conflict and walk me through each decision in plain English.**",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("output")
    args = parser.parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(report), encoding="utf-8")


if __name__ == "__main__":
    main()
