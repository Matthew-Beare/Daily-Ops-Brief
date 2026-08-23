#!/usr/bin/env python3
"""Render a generic Project instructions template from a flat JSON config."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Mapping


TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def load_config(path: Path) -> dict[str, str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("configuration must be a JSON object")
    config: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Z0-9_]+", key):
            raise ValueError(f"invalid configuration key: {key!r}")
        if isinstance(value, (dict, list)) or value is None:
            raise ValueError(f"configuration value for {key} must be a scalar")
        config[key] = str(value)
    return config


def render(template: str, config: Mapping[str, str]) -> str:
    required = set(TOKEN_RE.findall(template))
    missing = sorted(key for key in required if key not in config or not config[key].strip())
    if missing:
        raise ValueError("missing configuration keys: " + ", ".join(missing))

    rendered = TOKEN_RE.sub(lambda match: config[match.group(1)], template)
    leftovers = sorted(set(TOKEN_RE.findall(rendered)))
    if leftovers:
        raise ValueError("unresolved template keys: " + ", ".join(leftovers))
    return rendered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="validate rendering without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    rendered = render(args.template.read_text(encoding="utf-8"), config)

    if args.check:
        print("Starter configuration and template are valid.")
        return 0
    if args.output is None:
        raise SystemExit("--output is required unless --check is used")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
