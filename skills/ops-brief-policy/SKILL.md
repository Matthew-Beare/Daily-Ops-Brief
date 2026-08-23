---
name: ops-brief-policy
description: Legacy compatibility entry point for the Daily Ops Brief policy.
version: 3.1.2
---

# Compatibility Entry Point

This path is retained only so older links and bootstrap material do not break after repository reconciliation.

The canonical policy source is:

- `skill/ops-brief-policy/SKILL.md`
- deployed runtime: `skill/ops-brief-policy/scripts/ops_policy_runtime.py`

Do not maintain behavior here. Any lasting policy, workflow, schema, test, onboarding, or output change belongs under the canonical `skill/ops-brief-policy/` tree and must pass repository validation before merge.

Mutable operational state remains in the canonical Google Sheets. Never copy live task, route, trip, mileage, receipt, shipment, or financial-resolution state into this compatibility file.
