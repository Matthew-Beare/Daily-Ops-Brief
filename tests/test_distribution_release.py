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

    def test_channel_contract_has_one_canonical_source_and_no_manual_edits(self) -> None:
        config = json.loads((ROOT / "distribution/channels.json").read_text(encoding="utf-8"))
        self.assertEqual("sole-source-of-truth", config["canonical_source"]["role"])
        self.assertEqual("private", config["canonical_source"]["required_visibility"])
        self.assertFalse(config["promotion_contract"]["manual_edits_to_distribution_repositories_allowed"])
        self.assertFalse(config["promotion_contract"]["force_push_allowed"])
        channels = {row["channel_id"]: row for row in config["channels"]}
        self.assertEqual("public", channels["public-experimental"]["required_visibility"])
        self.assertTrue(channels["public-experimental"]["template_repository"])
        self.assertEqual("private", channels["institutional-experimental"]["required_visibility"])
        self.assertFalse(channels["institutional-experimental"]["regulated_data_allowed_in_git"])


if __name__ == "__main__":
    unittest.main()
