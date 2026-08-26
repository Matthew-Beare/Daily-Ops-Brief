from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "reconcile_upstream.py"


def run(cwd: pathlib.Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def git(cwd: pathlib.Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(cwd, "git", *args, check=check)


def configure(repo: pathlib.Path) -> None:
    git(repo, "config", "user.name", "MIRA Test")
    git(repo, "config", "user.email", "mira-test@example.com")


class UpstreamReconcilerTests(unittest.TestCase):
    def make_pair(self, root: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
        upstream = root / "upstream"
        personal = root / "personal"
        upstream.mkdir()
        git(upstream, "init", "-b", "main")
        configure(upstream)
        (upstream / "shared.txt").write_text("base\n", encoding="utf-8")
        git(upstream, "add", ".")
        git(upstream, "commit", "-m", "base")
        run(root, "git", "clone", str(upstream), str(personal))
        configure(personal)
        return upstream, personal

    def test_clean_upstream_and_custom_changes_merge_without_human_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            upstream, personal = self.make_pair(root)
            (personal / "custom.txt").write_text("user feature\n", encoding="utf-8")
            git(personal, "add", ".")
            git(personal, "commit", "-m", "custom feature")
            (upstream / "upstream.txt").write_text("canonical release\n", encoding="utf-8")
            git(upstream, "add", ".")
            git(upstream, "commit", "-m", "upstream feature")

            report = personal / "report.json"
            result = run(
                personal,
                "python3", str(SCRIPT),
                "--upstream", str(upstream),
                "--target", "main",
                "--report", str(report),
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual("clean_merge", payload["status"])
            self.assertFalse(payload["human_review_required"])
            self.assertTrue((personal / "custom.txt").is_file())
            self.assertTrue((personal / "upstream.txt").is_file())

    def test_conflict_fails_closed_and_returns_to_target_branch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            upstream, personal = self.make_pair(root)
            (personal / "shared.txt").write_text("user version\n", encoding="utf-8")
            git(personal, "add", ".")
            git(personal, "commit", "-m", "custom shared change")
            (upstream / "shared.txt").write_text("upstream version\n", encoding="utf-8")
            git(upstream, "add", ".")
            git(upstream, "commit", "-m", "upstream shared change")

            report = personal / "report.json"
            result = run(
                personal,
                "python3", str(SCRIPT),
                "--upstream", str(upstream),
                "--target", "main",
                "--report", str(report),
                check=False,
            )
            self.assertEqual(3, result.returncode)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual("conflict", payload["status"])
            self.assertTrue(payload["human_review_required"])
            self.assertIn("shared.txt", payload["conflicts"])
            self.assertEqual("main", git(personal, "branch", "--show-current").stdout.strip())
            self.assertEqual("user version\n", (personal / "shared.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
