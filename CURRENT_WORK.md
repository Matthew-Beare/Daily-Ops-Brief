# CURRENT WORK

Git is authoritative for active MIRROR development state. This file must identify exactly one active work packet and the exact resume point.

## Active packet

- **Packet ID:** `G0-001`
- **Name:** Install resumable audit/control-plane checkpoint
- **Class:** governance
- **Status:** active
- **Branch:** `governance/audit-control-plane-v1`
- **Base SHA:** `2c2824c70ddc3268c25333063eb61428817a5bf4`
- **Objective:** Make the upcoming full feature audit resumable and protect all existing live user data before any MIRA 2.0 product work begins.

## Non-negotiable data boundary

Existing Google spreadsheets, Drive artifacts, briefs, schedules, and other live MIRA/MIRROR state are **legacy production**. They are read-only during the audit and MIRA 2.0 development unless a later migration packet explicitly authorizes a bounded change with backup, rollback, and provider readback.

New development must use a separate MIRA 2.0 sandbox/reality namespace. Creating that Google sandbox is a later bounded packet; it must not overwrite, rename, repurpose, or silently migrate legacy production artifacts.

## Acceptance criteria

1. `ROADMAP.md`, `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, and `project/WORK_PACKET_POLICY.md` exist in Git.
2. The customer/developer ownership model is documented.
3. Backlog ordering is dependency/value driven, not FIFO.
4. The feature audit is explicitly split into bounded resumable packets.
5. Legacy Google production data is protected by an explicit no-touch boundary.
6. Every future packet has a durable exact resume point before implementation begins.
7. This packet changes no live Google data and no executable product behavior.

## Completed

- Chosen the current clean `main` baseline as the audit base.
- Identified the existing forensic feature ledger and generated feature-catalog machinery as audit inputs rather than disposable work.
- Identified PR #31 as a frozen integration/reference source to be triaged, not merged wholesale.

## Blockers

None.

## Exact next action

Commit this control-plane checkpoint, verify it remotely, then advance `CURRENT_WORK.md` to `G0-002` and begin **Feature Audit Slice 1: governance/core runtime + Brief/Time/Operational State (legacy ledger category A plus any newer matching PR #31 features)**. Do not implement product features while auditing.

## Resume protocol

On any new session or recovery:

1. Read `CURRENT_WORK.md` first.
2. Confirm the recorded branch and head SHA still exist remotely.
3. Read the referenced packet acceptance criteria and exact next action.
4. Continue only that packet unless a dependency required for acceptance is discovered.
5. New customer ideas go to `BACKLOG.md` by default; they do not expand the active packet.
6. If the customer explicitly reprioritizes, first checkpoint the current packet and record its exact resume point, then switch scope.
