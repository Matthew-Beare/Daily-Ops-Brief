# Daily Ops Brief

Private, rebuildable policy and tooling for the Daily Ops Brief control room.

## Canonical sources

- `skills/ops-brief-policy/SKILL.md` — human-readable skill contract.
- `policy/ops-brief-policy.yaml` — machine-readable policy constants and resolver rules.
- `tests/ops-brief-regressions.md` — regression contract for mode resolution and failure isolation.

Mutable operational state does **not** live in Git. It lives in the authoritative Google Sheets named by the policy. Git owns durable behavior; Sheets own live state.

## Current policy version

`3.0.1`

The 2026-08-22 fix hardens ROAD mode resolution and makes mileage/pay failures section-scoped so a non-Thursday mileage parse/read issue cannot abort an otherwise valid brief.
