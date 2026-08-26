#!/usr/bin/env python3
"""Safely reconcile a user's Personal Production source with canonical MIRA upstream."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run("git", *args, check=check)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_report(path: pathlib.Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def conflict_help(conflicts: list[str]) -> dict:
    file_text = ", ".join(conflicts) if conflicts else "one or more customized files"
    return {
        "headline": "MIRA paused this update to protect your customization",
        "plain_language": f"The new MIRA release and your personal version both changed {file_text}. Git cannot know which behavior you intended, so MIRA did not choose for you.",
        "your_data_is_safe": "Nothing was deleted, overwritten, force-merged, or removed from your Personal Production branch. Your current working version remains intact.",
        "what_you_should_do": [
            "Open this GitHub issue. You do not need to use the command line.",
            "Read the 'Files that need a decision' section. Each file will be explained in ordinary language by MIRA/ChatGPT before any edit is made.",
            "For each conflict, choose the outcome you want: keep your behavior, use the new MIRA behavior, or combine both when they are compatible.",
            "Ask MIRA in ChatGPT to resolve the conflict using those choices. MIRA should create a repair branch, not edit main directly.",
            "Let the normal automated tests run. If they are green, merge the repair PR. If they are not green, the update stays paused.",
            "After the repair merges, MIRA resumes the normal update flow. You do not need to reinstall or rebuild anything manually unless the installed-app updater specifically asks you to.",
        ],
        "recommended_default": "When the two behaviors are compatible, preserve the user's customization and incorporate the upstream fix. Never discard either side just to make Git stop complaining.",
        "do_not_do": [
            "Do not delete the Personal Production repository.",
            "Do not click a force-merge option just to clear the warning.",
            "Do not copy raw conflict markers into the app or database.",
            "Do not create a second competing Personal Production repository.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely reconcile a Personal Production repository with canonical MIRA upstream.")
    parser.add_argument("--upstream", required=True, help="Canonical upstream Git URL")
    parser.add_argument("--upstream-ref", default="main")
    parser.add_argument("--target", default="main")
    parser.add_argument("--report", default="reconciliation-report.json")
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    if git("status", "--porcelain").stdout.strip():
        write_report(report_path, {
            "status": "blocked",
            "reason": "dirty_worktree",
            "user_message": "MIRA found uncommitted work and stopped before updating so nothing could be lost.",
            "created_at": now(),
        })
        return 2

    remotes = git("remote").stdout.split()
    if "mirror-upstream" in remotes:
        git("remote", "set-url", "mirror-upstream", args.upstream)
    else:
        git("remote", "add", "mirror-upstream", args.upstream)
    git("fetch", "--prune", "mirror-upstream", args.upstream_ref)

    upstream_ref = f"mirror-upstream/{args.upstream_ref}"
    upstream_sha = git("rev-parse", upstream_ref).stdout.strip()
    target_sha = git("rev-parse", args.target).stdout.strip()
    ancestor = git("merge-base", "--is-ancestor", upstream_sha, target_sha, check=False)
    if ancestor.returncode == 0:
        write_report(report_path, {
            "status": "current",
            "target_sha": target_sha,
            "upstream_sha": upstream_sha,
            "user_message": "Your MIRA source is already up to date.",
            "created_at": now(),
        })
        return 0

    branch = f"mirror/update/{upstream_sha[:12]}"
    git("checkout", "-B", branch, args.target)
    merge = git("merge", "--no-edit", "--no-ff", upstream_ref, check=False)
    if merge.returncode != 0:
        conflicts = [line for line in git("diff", "--name-only", "--diff-filter=U", check=False).stdout.splitlines() if line]
        git("merge", "--abort", check=False)
        git("checkout", args.target, check=False)
        write_report(report_path, {
            "status": "conflict",
            "target_sha": target_sha,
            "upstream_sha": upstream_sha,
            "conflicts": conflicts,
            "human_review_required": True,
            "policy": "fail closed; never discard user-created features or upstream changes automatically",
            "user_help": conflict_help(conflicts),
            "created_at": now(),
        })
        return 3

    merged_sha = git("rev-parse", "HEAD").stdout.strip()
    changed = [line for line in git("diff", "--name-only", f"{target_sha}..{merged_sha}").stdout.splitlines() if line]
    write_report(report_path, {
        "status": "clean_merge",
        "branch": branch,
        "target_sha": target_sha,
        "upstream_sha": upstream_sha,
        "merged_sha": merged_sha,
        "changed_files": changed,
        "human_review_required": False,
        "user_message": "MIRA reconciled the update without overwriting your custom work. Automated checks are the only remaining gate.",
        "next_step": "push branch, open PR, run required checks, and merge automatically when green",
        "created_at": now(),
    })
    print(branch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
