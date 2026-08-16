# Changelog

## 0.2.0 — 2026-08-16

- Added a complete, version-controlled ChatGPT Project instructions template.
- Added deterministic rendering with local Sheet URL injection.
- Added a policy-source fingerprint and CI drift guard that forces instruction review after lasting policy changes.
- Added the full-replacement rule: return the entire updated instructions block, never a partial patch.

## 0.1.0 — 2026-08-16

- Added deterministic HOME/ROAD, task, appointment, travel, mileage, and run-health policy.
- Added deterministic shipment reconciliation with evidence precedence and split-package support.
- Defined the active-only shipment queue and delivered-row deletion rule.
- Defined Gmail filing and explicit archive-approval behaviour.
- Added cross-conversation Daily Brief/Ops-list capture boundaries.
- Added sanitized schemas, fixtures, rebuild documentation, and continuous tests.
- Added a machine-readable Google Sheets contract and idempotent shipment-tab migration specification.
