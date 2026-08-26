#!/usr/bin/env python3
"""Validate the full repository contract plus the current M.I.R.R.O.R. release topology."""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path


LEGACY_PATH = Path(__file__).with_name("validate_repo_legacy.inc")
STALE_RELEASE_ERRORS = {
    "README lacks observed beta-source/distribution boundary",
    "branding lacks channel names or clearance boundary",
    "distribution promotion contract is incomplete",
    "public distribution overlay is incomplete",
    "institutional distribution overlay is incomplete",
    "canonical Personal-Production channel is invalid",
    "public experimental channel is invalid",
    "institutional experimental channel is invalid",
    "shared feature workflow blurs portable source and live state",
    "browser install flow points at the wrong live beta template",
    "appointment feature lacks provider/reminder/readback contract",
    "platform capability manifest schema is invalid",
    "starter config does not default mutable state to Sheets/supported DB",
}


def _all_terms(value: str, *terms: str) -> bool:
    lower = value.lower()
    return all(term.lower() in lower for term in terms)


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _legacy_validate(root: Path) -> list[str]:
    if not LEGACY_PATH.is_file():
        return ["legacy repository validator payload is missing"]
    namespace = runpy.run_path(str(LEGACY_PATH))
    validator = namespace.get("validate")
    if not callable(validator):
        return ["legacy repository validator payload is invalid"]
    return list(validator(root))


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors = [error for error in _legacy_validate(root) if error not in STALE_RELEASE_ERRORS]

    def text(path: str) -> str:
        try:
            return (root / path).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"missing/unreadable required text {path}: {exc}")
            return ""

    def load_json(path: str):
        try:
            return json.loads((root / path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {path}: {exc}")
            return {}

    readme = text("README.md")
    branding = text("docs/BRANDING.md")
    distribution_readme = text("distribution/README.md")
    public_overlay = text("distribution/overlays/public-experimental/README.md")
    institutional_overlay = text("distribution/overlays/institutional-experimental/README.md")
    shared = text("starter/SHARED_FEATURE_WORKFLOW.md")
    quick_start = text("starter/QUICK_START.md")
    appointment_feature = text("starter/features/appointment-reconciliation/FEATURE.md")
    architecture = text("docs/architecture.md")
    runtime_architecture = text("docs/runtime-platform-architecture.md")
    config = load_json("distribution/channels.json")
    install_flow = load_json("starter/install-flow.json")
    starter_config = load_json("starter/config.example.json")
    platform_manifest = load_json("starter/platform-capabilities.json")
    runtime_contract = load_json("starter/runtime-interface-contract.json")
    model_policy = load_json("starter/model-routing-policy.json")
    barcode_contract = load_json("starter/barcode-qr-contract.json")
    appointment_contract = load_json("starter/appointment-identity-contract.json")
    client_api = load_json("starter/client-api-contract.json")
    network_contract = load_json("starter/network-security-contract.json")

    _require(
        _all_terms(
            readme,
            "M.I.R.R.O.R.",
            "Memory, Integration, Reality, Reconciliation, Observation, and Record",
            "MIRROR Intelligence and Reasoning Assistant",
            "holds the durable reflection of reality",
            "Magic MIRA on the wall",
            "assets",
            "finances",
            "calendars",
            "email",
            "orders",
            "appointments",
            "medications",
            "Build and share new skills",
            "all three onboarding repositories are public",
        ),
        "README lacks current M.I.R.R.O.R. public onboarding contract",
        errors,
    )
    _require("Signature line:" not in readme, "README contains internal copy-editing label", errors)

    _require(
        _all_terms(
            branding,
            "Memory, Integration, Reality, Reconciliation, Observation, and Record",
            "MIRROR Intelligence and Reasoning Assistant",
            "holds the durable reflection of reality",
            "Magic MIRA on the wall",
            "MIRA-Personal-Production",
            "MIRA-Public-Experimental",
            "MIRA-Institutional-Experimental",
            "all three repositories are public onboarding surfaces",
            "proper trademark/domain/app-store clearance",
        ),
        "branding lacks current M.I.R.R.O.R. identity/repository contract",
        errors,
    )

    _require(
        _all_terms(
            distribution_readme,
            "one canonical source",
            "deterministic",
            "public onboarding surfaces",
            "MIRA-Personal-Production",
            "MIRA-Public-Experimental",
            "MIRA-Institutional-Experimental",
            "without force",
            "remote readback",
            "green CI",
            "no PHI/PII",
        ),
        "distribution promotion contract is incomplete for renamed public channels",
        errors,
    )
    _require(
        _all_terms(public_overlay, "M.I.R.R.O.R. Personal-Experimental", "public repository", "sanitised", "not the canonical source", "DEPLOYMENT_CHANNEL.json"),
        "public distribution overlay lacks renamed public onboarding boundary",
        errors,
    )
    _require(
        _all_terms(institutional_overlay, "M.I.R.R.O.R. Institutional-Experimental", "public repository", "no PHI/PII in Git", "ATO", "approved runtime", "generated distribution", "generic or synthetic personas"),
        "institutional distribution overlay lacks public sanitised boundary",
        errors,
    )

    canonical = config.get("canonical_source", {}) if isinstance(config, dict) else {}
    channels = {
        row.get("channel_id"): row
        for row in config.get("channels", [])
        if isinstance(row, dict)
    } if isinstance(config, dict) else {}
    promotion = config.get("promotion_contract", {}) if isinstance(config, dict) else {}
    shared_code = config.get("shared_code_contract", {}) if isinstance(config, dict) else {}

    _require(config.get("schema_version") == 1, "distribution channel schema is invalid", errors)
    _require(
        canonical.get("repository") == "Matthew-Beare/MIRA-Personal-Production"
        and canonical.get("required_visibility") == "public"
        and canonical.get("role") == "sole-source-of-truth"
        and canonical.get("template_repository") is True,
        "canonical M.I.R.R.O.R. Personal-Production channel is invalid",
        errors,
    )
    _require(set(channels) == {"public-experimental", "institutional-experimental"}, "distribution channels are incomplete", errors)
    _require(
        channels.get("public-experimental", {}).get("repository") == "Matthew-Beare/MIRA-Public-Experimental"
        and channels.get("public-experimental", {}).get("required_visibility") == "public"
        and channels.get("public-experimental", {}).get("template_repository") is True,
        "M.I.R.R.O.R. Personal-Experimental channel is invalid",
        errors,
    )
    _require(
        channels.get("institutional-experimental", {}).get("repository") == "Matthew-Beare/MIRA-Institutional-Experimental"
        and channels.get("institutional-experimental", {}).get("required_visibility") == "public"
        and channels.get("institutional-experimental", {}).get("template_repository") is True
        and channels.get("institutional-experimental", {}).get("regulated_data_allowed_in_git") is False,
        "M.I.R.R.O.R. Institutional-Experimental channel is invalid",
        errors,
    )
    _require(
        shared_code.get("same_portable_source_revision_required") is True
        and shared_code.get("channel_specific_feature_code_allowed") is False,
        "shared-code release contract is invalid",
        errors,
    )
    _require(
        promotion.get("distribution_repositories_are_sources_of_truth") is False
        and promotion.get("manual_edits_to_distribution_repositories_allowed") is False
        and promotion.get("remote_readback_required") is True
        and promotion.get("green_ci_required") is True
        and promotion.get("force_push_allowed") is False,
        "distribution promotion safety contract is invalid",
        errors,
    )

    _require(
        _all_terms(
            shared,
            "structured state authority",
            "drive/evidence authority",
            "synthetic fixtures",
            "feature branch",
            "Do you want to make this feature available to other people?",
            "explicit publication approval",
            "upstream pull request",
        ),
        "shared skill workflow lacks private-to-public contribution contract",
        errors,
    )
    _require(
        _all_terms(quick_start, "Make M.I.R.R.O.R. do something new", "feature branch", "synthetic", "make this feature available to other people"),
        "QUICK_START lacks nontechnical skill-design/share instructions",
        errors,
    )
    _require(
        install_flow.get("upstream") == "Matthew-Beare/MIRA-Public-Experimental"
        and install_flow.get("upstream_status") == "current-public-onboarding-template"
        and install_flow.get("copy_method") == "github-template",
        "browser install flow points at the wrong M.I.R.R.O.R. onboarding source",
        errors,
    )

    # Current provider-neutral runtime architecture supersedes provider-specific beta assumptions.
    _require(
        _all_terms(
            appointment_feature,
            "cache first, research second",
            "owner correction",
            "morning-of",
            "60 minutes before",
            "IANA timezone",
            "read canonical state back",
            "spoken delivery",
            "Text-to-Speech",
            "Visual reminders remain available",
        ),
        "appointment feature lacks current identity/reminder/readback/spoken-delivery contract",
        errors,
    )

    capability_ids = set(platform_manifest.get("capability_ids", [])) if isinstance(platform_manifest, dict) else set()
    runtime_ids = {row.get("id") for row in platform_manifest.get("ai_runtimes", []) if isinstance(row, dict)} if isinstance(platform_manifest, dict) else set()
    storage_ids = {row.get("id") for row in platform_manifest.get("storage_backends", []) if isinstance(row, dict)} if isinstance(platform_manifest, dict) else set()
    client_ids = {row.get("id") for row in platform_manifest.get("client_surfaces", []) if isinstance(row, dict)} if isinstance(platform_manifest, dict) else set()
    _require(platform_manifest.get("schema_version") == 2, "platform capability manifest is not runtime-architecture schema v2", errors)
    _require({
        "source_read", "source_write", "source_remote_readback", "managed_release_read",
        "structured_state_read", "structured_state_write", "structured_state_readback",
        "structured_state_transactions", "structured_state_migration_export",
        "evidence_read", "evidence_write", "evidence_readback", "evidence_content_hash",
        "email_read", "calendar_read", "calendar_write", "calendar_readback",
        "scheduled_dispatch", "canonical_clock_gate", "observed_scheduled_firing",
        "client_api_read", "client_api_command", "client_sync", "local_agent",
        "visual_notification", "spoken_notification", "barcode_decode", "camera_capture",
        "local_model", "hosted_model", "strong_hosted_model",
        "private_overlay_network", "authenticated_https_api",
    } <= capability_ids, "platform capability manifest lacks future runtime/client/storage gates", errors)
    _require({"chatgpt", "local-model-runtime"} <= runtime_ids, "platform manifest lacks hosted/local model runtime lanes", errors)
    _require({"google-workspace", "self-hosted-linux", "cloud-native"} <= storage_ids, "platform manifest lacks browser/self-hosted/cloud storage lanes", errors)
    _require(client_ids == {"web", "windows-desktop", "linux-desktop", "android"}, "platform manifest lacks exact supported client surfaces", errors)

    _require(
        isinstance(starter_config, dict)
        and "POSTGRESQL" in starter_config.get("STATE_BACKEND", "")
        and starter_config.get("STATE_STORE") == "CURRENT_STRUCTURED_STATE_AUTHORITY_SELECTED_BY_AUTHORITY_REGISTRY"
        and "S3" in starter_config.get("EVIDENCE_BACKEND", "")
        and "VERSIONED_BOUNDED_SERVICE_API" in starter_config.get("CLIENT_API", "")
        and "SYSTEMD_TIMER" in starter_config.get("SCHEDULER_ADAPTER", ""),
        "starter config does not declare provider-neutral state/evidence/API/scheduler adapters",
        errors,
    )

    _require(
        runtime_contract.get("schema_version") == 1
        and runtime_contract.get("principles", {}).get("provider_neutral_core") is True
        and runtime_contract.get("principles", {}).get("clients_never_write_database_directly") is True
        and "postgresql" in runtime_contract.get("interfaces", {}).get("structured_state", {}).get("candidate_adapters", [])
        and "s3_compatible_object_storage" in runtime_contract.get("interfaces", {}).get("evidence_store", {}).get("candidate_adapters", [])
        and set(runtime_contract.get("client_surfaces", [])) == {"web", "windows_desktop", "linux_desktop", "android"},
        "runtime interface contract is incomplete or provider-coupled",
        errors,
    )
    _require(model_policy.get("default_path") == "deterministic" and "required_validator_failed" in model_policy.get("escalation_triggers", []), "model routing does not remain deterministic-first with explicit escalation", errors)
    _require(set(barcode_contract.get("scan_classes", {})) == {"product_identifier", "asset_tag", "location_tag", "evidence_reference"}, "barcode/QR contract lacks product/asset/location identity classes", errors)
    _require(appointment_contract.get("correction_rule") and appointment_contract.get("delivery", {}).get("privacy_default") == "generic", "appointment identity contract lacks durable correction or privacy-safe spoken delivery", errors)
    _require(client_api.get("security", {}).get("database_credentials_in_clients_prohibited") is True and client_api.get("sync", {}).get("client_offline_queue_requires_idempotency_keys") is True, "client API contract lacks credential/idempotency boundary", errors)
    _require(network_contract.get("homelab", {}).get("database_public_exposure") == "prohibited" and network_contract.get("cloud_native", {}).get("same_client_API_contract") is True, "network contract permits unsafe database exposure or client divergence", errors)
    _require(_all_terms(architecture, "provider-neutral", "PostgreSQL", "systemd", "Windows/Linux desktop", "Android", "database stays private"), "architecture doc lacks future runtime topology", errors)
    _require(_all_terms(runtime_architecture, "browser/connector", "Self-hosted Linux", "Cloud native", "service/API", "barcode and QR", "model routing", "Never expose PostgreSQL"), "runtime platform architecture is incomplete", errors)

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
