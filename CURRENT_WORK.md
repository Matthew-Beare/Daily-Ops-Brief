# CURRENT WORK

Git is authoritative for active MIRROR development state. This file must identify exactly one active work packet and the exact resume point.

## Active packet

- **Packet ID:** `SEC-001`
- **Name:** Restore clean public-history baseline before feature audit
- **Class:** integrity/security blocker
- **Status:** active
- **Branch:** `governance/audit-control-plane-v1`
- **Current branch head before this checkpoint:** `5fca1ae737375f088e10e2920e716f6db86b47fe`
- **Blocked packet:** `G0-002` Feature Audit Slice 1
- **Objective:** Resolve the reachable-history public-source audit failure discovered by PR #34 without broad/destructive history rewriting, then merge the governance control plane and resume the feature audit.

## Why priority changed

PR #34 CI failed at `python3 scripts/audit_public_source.py . --history` because reachable commit `95d46eedc8fd2c05dae8e3256c019af6412236ec` contains:

1. a concrete personal email address in `starter/clients/desktop/src-tauri/tauri.conf.json`;
2. a numeric sequence in `starter/clients/pwa/brand-mark.svg` flagged as a possible full payment-card number;
3. a numeric sequence in `starter/clients/pwa/icon.svg` flagged as a possible full payment-card number.

This failure predates the governance files. Under the green-before-growth and integrity rules, it is a blocker and therefore outranks the queued feature audit.

## Protected production boundary

Existing Google spreadsheets, Drive artifacts, briefs, schedules, and other live MIRA/MIRROR state remain **legacy production** and read-only. `SEC-001` is Git/repository work only and must not touch Google production data.

## Acceptance criteria for SEC-001

1. Inspect the exact offending historical content and classify each finding as true sensitive data or scanner false positive.
2. Choose the least destructive remediation that makes the repository publication boundary honest; do not rewrite broad history merely to silence CI unless no safe alternative exists and the customer explicitly approves that irreversible step.
3. Preserve rollback/recovery evidence for any history-sensitive operation.
4. Re-run the required CI on PR #34's exact final head and require success before merge.
5. Merge PR #34 only after required checks are green and remotely read back `main`.
6. Update this file back to `G0-002` with its exact first unaudited feature row after merge.
7. Touch no live Google production data and add no unrelated product features.

## Completed evidence

- G0-001 control-plane files were created and remotely read back.
- PR #34 was opened from `governance/audit-control-plane-v1` to `main`.
- PR #34 CI run `33029356048` failed at the history audit before later CI stages.
- The failure was traced to reachable commit `95d46eedc8fd2c05dae8e3256c019af6412236ec`, not to the new governance files.
- `BACKLOG.md` now records `SEC-001` as the active blocker and `DEV-001` as waiting on it.

## Blockers

The current required CI cannot pass until the reachable-history findings are correctly remediated or the scanner is narrowly corrected for verified false positives.

## Exact next action

Inspect the three offending paths at commit `95d46eedc8fd2c05dae8e3256c019af6412236ec` and compare them with the current versions plus `scripts/audit_public_source.py` detection rules. Determine separately whether the email is real sensitive history and whether each SVG numeric string is genuinely card-like data or a deterministic image/vector false positive. Do **not** begin `G0-002` until `SEC-001` is resolved and PR #34 is green/merged.

## Displaced packet resume point

`G0-002` resumes at the first legacy-ledger category-A row: **Exactly two briefs at 2:45 AM and 2:45 PM `America/New_York`**. Its acceptance criteria were previously checkpointed and remain unchanged.

## Resume protocol

On any new session or recovery:

1. Read `CURRENT_WORK.md` first.
2. Confirm the recorded branch/head exists remotely.
3. Continue from the exact next action, not from memory or a broad project summary.
4. Continue only the active packet unless a dependency required for acceptance is discovered.
5. New customer ideas go to `BACKLOG.md` by default; they do not expand the active packet.
6. If the customer explicitly reprioritizes, first checkpoint the displaced packet and record its exact resume point, then switch scope.
