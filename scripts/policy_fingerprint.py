#!/usr/bin/env python3
"""Compute the stable policy-source fingerprint embedded in Project instructions."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def policy_files(skill_root: Path) -> list[Path]:
    files = [skill_root / "SKILL.md"]
    files.extend(sorted((skill_root / "references").glob("*.md")))
    files.extend(
        skill_root / "scripts" / name
        for name in ("ops_policy.py", "reconcile_shipments.py")
    )
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing policy source: " + ", ".join(missing))
    return sorted(files, key=lambda path: path.relative_to(skill_root).as_posix())


def compute(skill_root: Path) -> str:
    digest = hashlib.sha256()
    for path in policy_files(skill_root):
        relative = path.relative_to(skill_root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", type=Path)
    args = parser.parse_args()
    print(compute(args.skill_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
