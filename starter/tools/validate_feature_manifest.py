#!/usr/bin/env python3
"""Validate portable Life-Ops feature manifests without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?$"
)
REQUIRED_FIELDS = {
    "manifest_version",
    "id",
    "version",
    "summary",
    "portable",
    "compatibility",
    "dependencies",
    "entrypoints",
    "permissions",
    "data_boundary",
    "config_schema",
    "tests",
}
ENTRYPOINT_FIELDS = {"references", "scripts", "schemas", "migrations"}
PERMISSION_FIELDS = {"connectors", "network_domains", "writes", "approval_required"}
RUNTIME_STATES = {"none", "deployment-local", "external-authority"}


def _string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        errors.append(f"{field} must be a list of nonempty strings")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{field} must not contain duplicates")
    return value


def _safe_path(value: str) -> bool:
    if "\\" in value or not value or value.startswith("/"):
        return False
    path = PurePosixPath(value)
    return all(part not in {"", ".", ".."} for part in path.parts)


def validate_manifest(value: Any, check_files_from: Path | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["manifest root must be an object"]

    missing = sorted(REQUIRED_FIELDS - set(value))
    extra = sorted(set(value) - REQUIRED_FIELDS)
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown fields: {', '.join(extra)}")
    if missing:
        return errors

    if value["manifest_version"] != 1:
        errors.append("manifest_version must equal 1")
    if not isinstance(value["id"], str) or not ID_RE.fullmatch(value["id"]):
        errors.append("id must be lowercase hyphen-case")
    if not isinstance(value["version"], str) or not VERSION_RE.fullmatch(
        value["version"]
    ):
        errors.append("version must be semantic version syntax")
    if not isinstance(value["summary"], str) or not 1 <= len(value["summary"]) <= 200:
        errors.append("summary must contain 1 to 200 characters")
    if value["portable"] is not True:
        errors.append("portable must be true")

    compatibility = value["compatibility"]
    if (
        not isinstance(compatibility, dict)
        or set(compatibility) != {"core"}
        or not isinstance(compatibility.get("core"), str)
        or not compatibility["core"].strip()
    ):
        errors.append("compatibility must contain only a nonempty core range")

    dependencies = value["dependencies"]
    if not isinstance(dependencies, list):
        errors.append("dependencies must be a list")
    else:
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict) or set(dependency) != {
                "id",
                "version_range",
            }:
                errors.append(
                    f"dependencies[{index}] must contain id and version_range only"
                )
                continue
            if not isinstance(dependency["id"], str) or not ID_RE.fullmatch(
                dependency["id"]
            ):
                errors.append(f"dependencies[{index}].id is invalid")
            if (
                not isinstance(dependency["version_range"], str)
                or not dependency["version_range"].strip()
            ):
                errors.append(f"dependencies[{index}].version_range is empty")

    entrypoints = value["entrypoints"]
    referenced_paths: list[tuple[str, str]] = []
    if not isinstance(entrypoints, dict) or set(entrypoints) != ENTRYPOINT_FIELDS:
        errors.append("entrypoints must contain references, scripts, schemas, and migrations")
    else:
        for field in sorted(ENTRYPOINT_FIELDS):
            for path in _string_list(
                entrypoints[field], f"entrypoints.{field}", errors
            ):
                if not _safe_path(path):
                    errors.append(f"entrypoints.{field} contains unsafe path: {path}")
                else:
                    referenced_paths.append((f"entrypoints.{field}", path))

    permissions = value["permissions"]
    if not isinstance(permissions, dict) or set(permissions) != PERMISSION_FIELDS:
        errors.append(
            "permissions must contain connectors, network_domains, writes, and approval_required"
        )
    else:
        for field in sorted(PERMISSION_FIELDS):
            items = _string_list(permissions[field], f"permissions.{field}", errors)
            if field == "network_domains" and any("://" in item for item in items):
                errors.append("permissions.network_domains must contain domains, not URLs")

    boundary = value["data_boundary"]
    boundary_fields = {
        "source_contains_personal_data",
        "shared_logs_contain_personal_data",
        "runtime_state",
        "forbidden_source_data",
    }
    if not isinstance(boundary, dict) or set(boundary) != boundary_fields:
        errors.append("data_boundary fields do not match the portable contract")
    else:
        if boundary["source_contains_personal_data"] is not False:
            errors.append("source_contains_personal_data must be false")
        if boundary["shared_logs_contain_personal_data"] is not False:
            errors.append("shared_logs_contain_personal_data must be false")
        if boundary["runtime_state"] not in RUNTIME_STATES:
            errors.append("data_boundary.runtime_state is invalid")
        forbidden = _string_list(
            boundary["forbidden_source_data"],
            "data_boundary.forbidden_source_data",
            errors,
        )
        if not forbidden:
            errors.append("data_boundary.forbidden_source_data must not be empty")

    config_schema = value["config_schema"]
    if not isinstance(config_schema, dict):
        errors.append("config_schema must be an object")
    else:
        if config_schema.get("type") != "object":
            errors.append("config_schema.type must equal object")
        if config_schema.get("additionalProperties") is not False:
            errors.append("config_schema.additionalProperties must be false")

    tests = _string_list(value["tests"], "tests", errors)
    if not tests:
        errors.append("tests must not be empty")
    for path in tests:
        if not _safe_path(path):
            errors.append(f"tests contains unsafe path: {path}")
        else:
            referenced_paths.append(("tests", path))

    if check_files_from is not None:
        for field, relative in referenced_paths:
            if not (check_files_from / relative).is_file():
                errors.append(f"{field} references missing file: {relative}")

    return errors


def default_manifests() -> list[Path]:
    return sorted(
        [
            *ROOT.glob("features/*/feature.json"),
            *ROOT.glob("fixtures/features/*.feature.json"),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="*", type=Path)
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Require every declared entrypoint and test path to exist beside the manifest.",
    )
    args = parser.parse_args()
    manifests = args.manifests or default_manifests()
    if not manifests:
        parser.error("no feature manifests found")

    failed = False
    for path in manifests:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR {path}: {exc}")
            failed = True
            continue
        errors = validate_manifest(value, path.parent if args.check_files else None)
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR {path}: {error}")
        else:
            print(f"OK {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
