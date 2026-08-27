# CURRENT WORK

Git is authoritative for active MIRROR development state. This file must identify exactly one active work packet and the exact resume point.

## Active packet

- **Packet ID:** `G0-002`
- **Name:** Feature Audit Slice 1 — Core runtime + Brief/Time/Operational State
- **Class:** audit
- **Status:** ready
- **Branch:** `governance/audit-control-plane-v1`
- **Base SHA:** `2f19034f2b3aac724b79a5412140b213bbf56197`
- **Related source:** legacy feature-ledger category A plus newer matching `main`, tests, PR #31, and relevant branch evidence
- **Objective:** Reconstruct the first bounded slice of the canonical feature registry with stable semantic IDs, complete descriptions, dependency relationships, acceptance criteria, and honest verification state. Do not implement product behavior.

## Protected production boundary

Existing Google spreadsheets, Drive artifacts, briefs, schedules, and other live MIRA/MIRROR state are **legacy production**. They remain read-only during G0 and MIRA 2.0 development. No audit packet may write, rename, repurpose, migrate, or clean up those artifacts.

New implementation work will later use a separate MIRA 2.0 sandbox/reality namespace under a dedicated packet with provider readback.

## Acceptance criteria for G0-002

1. Audit every category-A legacy feature and any newer feature that belongs to the same core/ops domain.
2. Assign each recovered capability a permanent semantic feature ID.
3. Give each feature a full description, decision state, delivery state, milestone, dependencies, enables, acceptance criteria, evidence, and constraints.
4. Reconcile duplicates/superseded wording without deleting historical evidence.
5. Do not upgrade implementation status merely because code or CI exists; distinguish test/integration/live proof.
6. Add newly discovered unfinished work to `BACKLOG.md` with dependency metadata.
7. Commit the completed slice and update this file to the first exact unaudited item in `G0-003` before switching slices.
8. Touch no live Google production data and implement no unrelated product feature.

## Previous checkpoint

`G0-001` completed on branch commit `2f19034f2b3aac724b79a5412140b213bbf56197`:

- installed `ROADMAP.md`, `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, and `project/WORK_PACKET_POLICY.md`;
- documented the customer/product-owner versus assistant/developer ownership model;
- made backlog priority dependency/value driven rather than FIFO;
- split the full audit into bounded recovery-safe slices;
- established the legacy-production no-touch rule and separate MIRA 2.0 sandbox requirement;
- remotely read back the control files from GitHub.

## Blockers

None.

## Exact next action

Open `docs/feature-ledger-2026-08-24.md` at **category A: Brief engine, time, tasking, and operational state**. Enumerate every row into stable semantic IDs, then compare that domain against current `main`, tests, and PR #31 to recover newer/changed capabilities. The first unprocessed source is the first category-A row: **Exactly two briefs at 2:45 AM and 2:45 PM `America/New_York`**.

## Resume protocol

On any new session or recovery:

1. Read `CURRENT_WORK.md` first.
2. Confirm the recorded branch/head exists remotely.
3. Continue from the exact next action, not from memory or a broad project summary.
4. Continue only the active packet unless a dependency required for acceptance is discovered.
5. New customer ideas go to `BACKLOG.md` by default; they do not expand the active packet.
6. If the customer explicitly reprioritizes, first checkpoint the displaced packet and record its exact resume point, then switch scope.
