from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


BUILDER = _module("build_distribution", "scripts/build_distribution.py")
VALIDATOR = _module("validate_distribution", "scripts/validate_distribution.py")
AUDITOR = _module("audit_public_source", "scripts/audit_public_source.py")
REVISION = "a" * 40


class DistributionReleaseTests(unittest.TestCase):
    def build(self, channel: str, parent: Path, name: str = "release") -> Path:
        output = parent / name
        BUILDER.build(channel, output, REVISION, root=ROOT)
        return output

    def test_both_channels_are_fresh_valid_sanitised_trees(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            for channel in ("public-experimental", "institutional-experimental"):
                with self.subTest(channel=channel):
                    output = self.build(channel, parent, channel)
                    self.assertEqual([], AUDITOR.audit(output))
                    self.assertEqual(
                        [],
                        VALIDATOR.validate(
                            output,
                            expected_channel=channel,
                            expected_source_revision=REVISION,
                        ),
                    )
                    self.assertFalse((output / "skill").exists())
                    self.assertFalse((output / "project").exists())
                    self.assertFalse((output / "policy").exists())
                    self.assertTrue((output / "starter/PROVIDER_ONBOARDING.md").is_file())
                    self.assertTrue((output / "starter/QUICK_START.md").is_file())
                    self.assertTrue((output / "starter/SHARED_FEATURE_WORKFLOW.md").is_file())
                    self.assertTrue((output / "starter/life-planner/SKILL.md").is_file())
                    self.assertTrue((output / "starter/life-planner/scripts/google_bootstrap.py").is_file())

    def test_build_is_deterministic_for_same_channel_and_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            first = self.build("public-experimental", parent, "first")
            second = self.build("public-experimental", parent, "second")
            first_files = {
                path.relative_to(first).as_posix(): path.read_bytes()
                for path in first.rglob("*") if path.is_file()
            }
            second_files = {
                path.relative_to(second).as_posix(): path.read_bytes()
                for path in second.rglob("*") if path.is_file()
            }
            self.assertEqual(first_files, second_files)

    def test_payload_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = self.build("institutional-experimental", Path(temp))
            readme = output / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\nmanual drift\n", encoding="utf-8")
            self.assertIn(
                "distribution payload differs from its immutable hash manifest",
                VALIDATOR.validate(output),
            )

    def test_git_metadata_and_ignored_python_cache_do_not_change_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = self.build("public-experimental", Path(temp))
            (output / ".git/objects").mkdir(parents=True)
            (output / ".git/HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            cache = output / "starter/tools/__pycache__"
            cache.mkdir()
            (cache / "module.cpython-312.pyc").write_bytes(b"ignored cache")
            self.assertEqual([], VALIDATOR.validate(output))

    def test_channel_contract_has_one_public_canonical_source_and_public_onboarding_repos(self) -> None:
        config = json.loads((ROOT / "distribution/channels.json").read_text(encoding="utf-8"))
        self.assertEqual("sole-source-of-truth", config["canonical_source"]["role"])
        self.assertEqual("public", config["canonical_source"]["required_visibility"])
        self.assertEqual("Matthew-Beare/MIRA-Personal-Production", config["canonical_source"]["repository"])
        self.assertFalse(config["promotion_contract"]["manual_edits_to_distribution_repositories_allowed"])
        self.assertFalse(config["promotion_contract"]["force_push_allowed"])
        channels = {row["channel_id"]: row for row in config["channels"]}
        self.assertEqual("public", channels["public-experimental"]["required_visibility"])
        self.assertEqual("public", channels["institutional-experimental"]["required_visibility"])
        self.assertEqual("Matthew-Beare/MIRA-Public-Experimental", channels["public-experimental"]["repository"])
        self.assertEqual("Matthew-Beare/MIRA-Institutional-Experimental", channels["institutional-experimental"]["repository"])
        self.assertTrue(channels["public-experimental"]["template_repository"])
        self.assertFalse(channels["institutional-experimental"]["regulated_data_allowed_in_git"])

    def test_canonical_source_keeps_history_audit_while_distributions_scan_current_tree(self) -> None:
        canonical_ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/audit_public_source.py . --history", canonical_ci)

        for relative in (
            "distribution/overlays/public-experimental/.github/workflows/ci.yml",
            "distribution/overlays/institutional-experimental/.github/workflows/ci.yml",
        ):
            with self.subTest(relative=relative):
                distribution_ci = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("scripts/audit_public_source.py .", distribution_ci)
                self.assertNotIn("scripts/audit_public_source.py . --history", distribution_ci)
                self.assertIn("scripts/validate_distribution.py", distribution_ci)

        release_doc = (ROOT / "distribution/README.md").read_text(encoding="utf-8")
        self.assertIn("canonical full-history audit", release_doc)
        self.assertIn("current generated tree", release_doc)
        self.assertIn("no-force-push", release_doc)

    def test_distribution_artifacts_run_target_ci_and_finish_clean(self) -> None:
        workflow = (ROOT / ".github/workflows/build-distributions.yml").read_text(encoding="utf-8")
        self.assertEqual(2, workflow.count("include-hidden-files: true"))
        self.assertIn('cd "$RUNNER_TEMP/MIRA-Public-Experimental"', workflow)
        self.assertIn('cd "$RUNNER_TEMP/MIRA-Institutional-Experimental"', workflow)
        self.assertEqual(4, workflow.count("python3 scripts/audit_public_source.py ."))
        self.assertEqual(4, workflow.count("python3 scripts/audit_starter_privacy.py starter"))
        self.assertEqual(4, workflow.count("python3 scripts/validate_distribution.py ."))
        self.assertEqual(2, workflow.count("python3 starter/tools/validate_feature_manifest.py --check-files"))
        self.assertEqual(2, workflow.count("python3 -m unittest discover -s starter/tests -p 'test_*.py'"))
        self.assertEqual(2, workflow.count("-name __pycache__"))
        self.assertEqual(2, workflow.count("-name '*.pyc' -o -name '*.pyo'"))


if __name__ == "__main__":
    unittest.main()
