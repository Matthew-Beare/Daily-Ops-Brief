#!/usr/bin/env python3
"""Compute the stable deployed-policy fingerprint stored inside Git.

Fingerprint v2 hashes each policy file's relative path plus its deterministic Git
blob identity. This preserves content sensitivity while making the repository tree
sufficient to independently reproduce a checkpoint fingerprint without weakening
strict validation or requiring a deliberately failing CI discovery run.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def policy_files(skill_root: Path) -> list[Path]:
    files = [skill_root / "SKILL.md"]
    files.extend(sorted((skill_root / "references").glob("*.md")))
    scripts = skill_root / "scripts"
    files.extend(
        sorted(
            path
            for path in scripts.glob("*.py")
            if path.is_file() and not path.name.startswith("test_") and path.name != "__init__.py"
        )
    )
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing policy source: " + ", ".join(missing))
    return sorted(files, key=lambda path: path.relative_to(skill_root).as_posix())


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def compute(skill_root: Path) -> str:
    digest = hashlib.sha256()
    for path in policy_files(skill_root):
        relative = path.relative_to(skill_root).as_posix().encode("utf-8")
        blob_identity = git_blob_sha(path.read_bytes()).encode("ascii")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(blob_identity)
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
