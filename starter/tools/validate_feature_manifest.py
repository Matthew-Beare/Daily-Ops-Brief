#!/usr/bin/env python3
"""Validate portable LyfeOS feature manifests without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CROSS_WRITE_RE = re.compile(r"^[a-z][a-z0-9-]*:[a-z][a-z0-9-]*$")
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$")
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
    "runtime_contract",
    "config_schema",
    "tests",
}
ENTRYPOINT_FIELDS = {"references", "scripts", "schemas", "migrations"}
PERMISSION_FIELDS = {"connectors", "network_domains", "writes", "approval_required"}
RUNTIME_STATES = {"none", "deployment-local", "external-authority"}
RUNTIME_CONTRACT_FIELDS = {
    "failure_domain",
    "required_capabilities",
    "optional_capabilities",
    "conditional_capabilities",
    "canonical_state_classes",
    "idempotency_scope",
    "on_required_failure",
    "on_optional_failure",
    "cross_module_writes",
}


def _string_list(value: Any, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{field} must be a list of nonempty strings")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{field} must not contain duplicates")
    return value


def _id_list(value: Any, field: str, errors: list[str], *, allow_empty: bool = True) -> list[str]:
    items = _string_list(value, field, errors)
    if not allow_empty and not items:
        errors.append(f"{field} must not be empty")
    for item in items:
        if not ID_RE.fullmatch(item):
            errors.append(f"{field} contains invalid id: {item}")
    return items


def _safe_path(value: str) -> bool:
    if "\\" in value or not value or value.startswith("/"):
        return False
    path = PurePosixPath(value)
    return all(part not in {"", ".", ".."} for part in path.parts)


def _is_fixture(path: Path) -> bool:
    return "fixtures" in path.parts


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
    if value["manifest_version"] != 2:
        errors.append("manifest_version must equal 2")
    if not isinstance(value["id"], str) or not ID_RE.fullmatch(value["id"]):
        errors.append("id must be lowercase hyphen-case")
    if not isinstance(value["version"], str) or not VERSION_RE.fullmatch(value["version"]):
        errors.append("version must be semantic version syntax")
    if not isinstance(value["summary"], str) or not 1 <= len(value["summary"]) <= 200:
        errors.append("summary must contain 1 to 200 characters")
    if value["portable"] is not True:
        errors.append("portable must be true")

    compatibility = value["compatibility"]
    if not isinstance(compatibility, dict) or set(compatibility) != {"core"} or not isinstance(compatibility.get("core"), str) or not compatibility["core"].strip():
        errors.append("compatibility must contain only a nonempty core range")

    dependencies = value["dependencies"]
    seen_dependency_ids: set[str] = set()
    if not isinstance(dependencies, list):
        errors.append("dependencies must be a list")
    else:
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict) or set(dependency) != {"id", "version_range"}:
                errors.append(f"dependencies[{index}] must contain id and version_range only")
                continue
            dep_id = dependency.get("id")
            if not isinstance(dep_id, str) or not ID_RE.fullmatch(dep_id):
                errors.append(f"dependencies[{index}].id is invalid")
            elif dep_id == value.get("id"):
                errors.append("feature cannot depend on itself")
            elif dep_id in seen_dependency_ids:
                errors.append(f"duplicate feature dependency: {dep_id}")
            else:
                seen_dependency_ids.add(dep_id)
            if not isinstance(dependency.get("version_range"), str) or not dependency["version_range"].strip():
                errors.append(f"dependencies[{index}].version_range is empty")

    entrypoints = value["entrypoints"]
    referenced_paths: list[tuple[str, str]] = []
    if not isinstance(entrypoints, dict) or set(entrypoints) != ENTRYPOINT_FIELDS:
        errors.append("entrypoints must contain references, scripts, schemas, and migrations")
    else:
        for field in sorted(ENTRYPOINT_FIELDS):
            for path in _string_list(entrypoints[field], f"entrypoints.{field}", errors):
                if not _safe_path(path):
                    errors.append(f"entrypoints.{field} contains unsafe path: {path}")
                else:
                    referenced_paths.append((f"entrypoints.{field}", path))

    permissions = value["permissions"]
    if not isinstance(permissions, dict) or set(permissions) != PERMISSION_FIELDS:
        errors.append("permissions must contain connectors, network_domains, writes, and approval_required")
    else:
        for field in sorted(PERMISSION_FIELDS):
            items = _string_list(permissions[field], f"permissions.{field}", errors)
            if field == "network_domains" and any("://" in item for item in items):
                errors.append("permissions.network_domains must contain domains, not URLs")

    boundary = value["data_boundary"]
    runtime_state: str | None = None
    boundary_fields = {"source_contains_personal_data", "shared_logs_contain_personal_data", "runtime_state", "forbidden_source_data"}
    if not isinstance(boundary, dict) or set(boundary) != boundary_fields:
        errors.append("data_boundary fields do not match the portable contract")
    else:
        runtime_state = boundary.get("runtime_state") if isinstance(boundary.get("runtime_state"), str) else None
        if boundary["source_contains_personal_data"] is not False:
            errors.append("source_contains_personal_data must be false")
        if boundary["shared_logs_contain_personal_data"] is not False:
            errors.append("shared_logs_contain_personal_data must be false")
        if runtime_state not in RUNTIME_STATES:
            errors.append("data_boundary.runtime_state is invalid")
        forbidden = _string_list(boundary["forbidden_source_data"], "data_boundary.forbidden_source_data", errors)
        if not forbidden:
            errors.append("data_boundary.forbidden_source_data must not be empty")

    runtime = value["runtime_contract"]
    if not isinstance(runtime, dict) or set(runtime) != RUNTIME_CONTRACT_FIELDS:
        errors.append("runtime_contract fields do not match the isolation contract")
    else:
        domain = runtime.get("failure_domain")
        if not isinstance(domain, str) or not ID_RE.fullmatch(domain):
            errors.append("runtime_contract.failure_domain must be lowercase hyphen-case")

        required = _id_list(
            runtime.get("required_capabilities"),
            "runtime_contract.required_capabilities",
            errors,
            allow_empty=False,
        )
        optional = _id_list(
            runtime.get("optional_capabilities"),
            "runtime_contract.optional_capabilities",
            errors,
        )
        overlap = sorted(set(required) & set(optional))
        if overlap:
            errors.append(f"capabilities cannot be both required and optional: {', '.join(overlap)}")

        conditional = runtime.get("conditional_capabilities")
        if not isinstance(conditional, dict) or any(
            not isinstance(key, str)
            or not ID_RE.fullmatch(key)
            or not isinstance(rule, str)
            or not rule.strip()
            for key, rule in (conditional.items() if isinstance(conditional, dict) else [])
        ):
            errors.append("runtime_contract.conditional_capabilities must map capability ids to nonempty string rules")
        elif not set(conditional) <= set(optional):
            errors.append("conditional capabilities must be declared optional capabilities")

        state_classes = _id_list(
            runtime.get("canonical_state_classes"),
            "runtime_contract.canonical_state_classes",
            errors,
        )
        if runtime_state == "external-authority" and "structured-state-authority" not in required:
            errors.append("external-authority features must require structured-state-authority")
        if runtime_state not in {None, "none"} and not state_classes:
            errors.append("stateful features must declare canonical_state_classes")

        idempotency = runtime.get("idempotency_scope")
        if not isinstance(idempotency, str) or not idempotency.strip() or len(idempotency) > 160:
            errors.append("runtime_contract.idempotency_scope must be a nonempty string <= 160 characters")
        if runtime.get("on_required_failure") != "block-module-only":
            errors.append("runtime_contract.on_required_failure must equal block-module-only")
        if runtime.get("on_optional_failure") != "degrade-capability-and-continue":
            errors.append("runtime_contract.on_optional_failure must equal degrade-capability-and-continue")
        cross_writes = _string_list(runtime.get("cross_module_writes"), "runtime_contract.cross_module_writes", errors)
        for write in cross_writes:
            if not CROSS_WRITE_RE.fullmatch(write):
                errors.append(f"runtime_contract.cross_module_writes contains invalid target: {write}")

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


def validate_dependency_graph(entries: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    """Validate live feature-to-feature dependencies as one acyclic install bundle."""
    errors: list[str] = []
    by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path, value in entries:
        feature_id = value.get("id")
        if not isinstance(feature_id, str):
            continue
        if feature_id in by_id:
            errors.append(f"duplicate live feature id: {feature_id}")
        else:
            by_id[feature_id] = (path, value)

    graph: dict[str, list[str]] = {feature_id: [] for feature_id in by_id}
    for feature_id, (_, value) in by_id.items():
        dependencies = value.get("dependencies")
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue
            dep_id = dependency.get("id")
            if not isinstance(dep_id, str):
                continue
            if dep_id not in by_id:
                errors.append(f"feature {feature_id} depends on missing bundled feature {dep_id}")
            else:
                graph[feature_id].append(dep_id)

    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            cycle_start = stack.index(node) if node in stack else 0
            cycle = stack[cycle_start:] + [node]
            errors.append("feature dependency cycle: " + " -> ".join(cycle))
            return
        visiting.add(node)
        stack.append(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for feature_id in sorted(graph):
        visit(feature_id)
    return errors


def default_manifests() -> list[Path]:
    return sorted([*ROOT.glob("features/*/feature.json"), *ROOT.glob("fixtures/features/*.feature.json")])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="*", type=Path)
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Require every declared live-feature entrypoint and test path to exist beside the manifest. Synthetic fixtures are schema-checked only.",
    )
    args = parser.parse_args()
    manifests = args.manifests or default_manifests()
    if not manifests:
        parser.error("no feature manifests found")

    failed = False
    parsed: list[tuple[Path, dict[str, Any]]] = []
    for path in manifests:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR {path}: {exc}")
            failed = True
            continue
        parsed.append((path, value))
        check_from = path.parent if args.check_files and not _is_fixture(path) else None
        errors = validate_manifest(value, check_from)
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR {path}: {error}")
        else:
            print(f"OK {path}")

    live_entries = [(path, value) for path, value in parsed if not _is_fixture(path)]
    graph_errors = validate_dependency_graph(live_entries)
    if graph_errors:
        failed = True
        for error in graph_errors:
            print(f"ERROR feature graph: {error}")
    elif live_entries:
        print("OK live feature dependency graph")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
