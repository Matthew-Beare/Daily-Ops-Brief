#!/usr/bin/env python3
"""Build deterministic sanitised Life Planner distribution trees from canonical source."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path("distribution/channels.json")
MANIFEST_PATH = Path("DEPLOYMENT_CHANNEL.json")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


def _excluded_source(path: Path) -> bool:
    return "__pycache__" in path.parts or path.name in {".DS_Store"} or path.suffix == ".pyc"


def _load_config(root: Path) -> dict[str, Any]:
    value = json.loads((root / CONFIG_PATH).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("distribution/channels.json must use schema_version 1")
    return value


def _safe_relative(value: str) -> Path:
    posix = PurePosixPath(value)
    if not value or value.startswith("/") or "\\" in value:
        raise ValueError(f"unsafe distribution path: {value!r}")
    if any(part in {"", ".", ".."} for part in posix.parts):
        raise ValueError(f"unsafe distribution path: {value!r}")
    return Path(*posix.parts)


def _copy_file(source: Path, destination: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"symlink is forbidden in a distribution: {source}")
    if not source.is_file():
        raise ValueError(f"distribution source file is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _copy_path(source_root: Path, relative: Path, destination_root: Path) -> None:
    source = source_root / relative
    if source.is_symlink():
        raise ValueError(f"symlink is forbidden in a distribution: {relative.as_posix()}")
    if source.is_file():
        _copy_file(source, destination_root / relative)
        return
    if not source.is_dir():
        raise ValueError(f"distribution source path is missing: {relative.as_posix()}")
    for path in sorted(source.rglob("*")):
        if _excluded_source(path.relative_to(source_root)):
            continue
        if path.is_symlink():
            raise ValueError(
                f"symlink is forbidden in a distribution: {path.relative_to(source_root).as_posix()}"
            )
        if path.is_file():
            _copy_file(path, destination_root / path.relative_to(source_root))


def _payload_hashes(output: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(output.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlink is forbidden in a distribution: {path.relative_to(output)}")
        if path.is_file() and path.relative_to(output) != MANIFEST_PATH:
            relative = path.relative_to(output).as_posix()
            hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _channel(config: dict[str, Any], channel_id: str) -> dict[str, Any]:
    matches = [
        row for row in config.get("channels", [])
        if isinstance(row, dict) and row.get("channel_id") == channel_id
    ]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate distribution channel: {channel_id}")
    return matches[0]


def build(
    channel_id: str,
    output: Path,
    source_revision: str,
    *,
    root: Path = ROOT,
) -> Path:
    """Build one fresh channel tree and return its manifest path."""
    root = root.resolve()
    output = output.resolve()
    if not REVISION_RE.fullmatch(source_revision):
        raise ValueError("source revision must be one lowercase 40-character Git commit SHA")
    if output == root or root in output.parents:
        raise ValueError("distribution output must be outside the canonical source tree")
    if output.exists():
        raise ValueError("distribution output already exists; use a fresh path")

    config = _load_config(root)
    channel = _channel(config, channel_id)
    output.mkdir(parents=True)

    for value in config.get("portable_paths", []):
        if not isinstance(value, str):
            raise ValueError("portable_paths must contain strings")
        _copy_path(root, _safe_relative(value), output)

    overlay_value = channel.get("overlay")
    if not isinstance(overlay_value, str):
        raise ValueError(f"channel {channel_id} lacks an overlay")
    overlay = root / _safe_relative(overlay_value)
    if not overlay.is_dir():
        raise ValueError(f"channel overlay is missing: {overlay_value}")
    for path in sorted(overlay.rglob("*")):
        if _excluded_source(path.relative_to(overlay)):
            continue
        if path.is_symlink():
            raise ValueError(f"symlink is forbidden in an overlay: {path}")
        if path.is_file():
            _copy_file(path, output / path.relative_to(overlay))

    forbidden = set(config.get("forbidden_distribution_roots", []))
    present_roots = {path.relative_to(output).parts[0] for path in output.rglob("*")}
    leaked = sorted(forbidden & present_roots)
    if leaked:
        raise ValueError(f"forbidden canonical roots leaked into distribution: {', '.join(leaked)}")

    canonical = config.get("canonical_source", {})
    promotion = config.get("promotion_contract", {})
    manifest = {
        "schema_version": 1,
        "product_name": config.get("product_name"),
        "channel_id": channel_id,
        "repository": channel.get("repository"),
        "required_visibility": channel.get("required_visibility"),
        "template_repository": channel.get("template_repository"),
        "canonical_source_repository": canonical.get("repository"),
        "canonical_source_revision": source_revision,
        "generated_distribution": True,
        "manual_edits_allowed": promotion.get("manual_edits_to_distribution_repositories_allowed"),
        "contains_runtime_state": False,
        "regulated_data_allowed_in_git": channel.get("regulated_data_allowed_in_git"),
        "allowed_runtime_data": channel.get("allowed_runtime_data"),
        "payload_sha256": _payload_hashes(output),
    }
    manifest_path = output / MANIFEST_PATH
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--channel",
        required=True,
        choices=("public-experimental", "institutional-experimental"),
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-revision", required=True)
    args = parser.parse_args()
    manifest = build(args.channel, args.output, args.source_revision)
    print(f"Built {args.channel}: {manifest.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
