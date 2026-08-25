# Architecture

M.I.R.R.O.R. separates mutable state, deterministic policy, evidence, scheduled dispatch, versioned recovery material, and feature ownership/dependency lineage.

At the product boundary, **MIRA is the control plane**: conversation, reasoning, planning, dependency analysis, user approval, reconciliation, recommendations, and approved execution. **M.I.R.R.O.R. is the reality/data plane plus durable structure**: canonical state/evidence interfaces, policy, schemas, provenance, feature lineage, and the records that describe reality. The data-plane analogy is useful but intentionally approximate because M.I.R.R.O.R. owns more durable structure than a classic packet-forwarding plane.

| Layer | Authority | Responsibility |
|---|---|---|
| Mutable Ops state | Ops Status Register | Tasks, controls, routes, trips, shipments, suppressions, run logs |
| Mileage state | Mileage & Pay Tracker | Company-paid miles, frozen rate, gross estimate, pay-week history |
| Purchase state | Purchase & Receipt Archive | Transactions, items, lifecycle events, expense allocations, classification queue, audit gate |
| Evidence | Gmail, Calendar, Drive | Complete threads, appointments, receipt attachments and archives |
| Policy | `skill/ops-brief-policy` | Routing, invariants, deterministic workflow, failure boundaries |
| Feature ownership/dependencies | `starter/features.lock.json` + `starter/feature-dependency-map.json` | Durable owner/origin/lineage, feature dependencies, required/optional capabilities, rollback/conflict policy |
| MIRA reconciliation control plane | `starter/tools/feature_reconciliation.py` + AI runtime | Non-mutating upgrade comparison, dependency readiness, overlap/consolidation proposals, Boomer-mode explanation, user approval boundary |
| Control-cycle dispatcher | One ChatGPT task | Reconcile receipts/orders, run the PM qualified-job watch, and emit briefs at deployment-owned scheduled times |
| Recovery | Git source + verified provider state | Tests, templates, documentation, policy fingerprints, feature rollback checkpoints, state/evidence readback |

The reference task carries no mutable database. The dispatcher chooses the configured slot and invokes the skill; receipt/order, qualified-job, and brief phases remain separate failure domains inside one scheduled run. Receipt work must pass the Audit gate before archiving source mail. No order, job, or calendar event receives its own automation.

See [LyfeOS Data Model](lyfeos-data-model.md) for keys, relationships, and the self-hosting boundary.

The generic starter is separate from the current deployment. It may generate a new bootstrap contract, but it must not inherit the current user's identifiers or operational rows.

## Feature and upgrade architecture

Features are modular packages with explicit manifests, failure domains, dependencies, permissions, state boundaries, and tests. They normally remain in one repository/process. Separate network services are introduced only for a real isolation, privilege, scaling, hardware, or platform boundary; microservices are not used merely to simulate modularity.

Every feature has durable ownership and lineage. User-created features default to user ownership. Locally modified stock features retain their upstream base plus a local revision. CI rejects unowned features and a stale dependency map.

Upstream updates are three-view reconciliations: originally adopted upstream state, current deployment state, and candidate upstream state. The candidate is a proposal, never a replacement image. User-owned/local behavior is preserved by default and every changed feature remains user-in-the-loop. AI may propose consolidation or compatibility repair, but cannot delete or overwrite local behavior on its own.

Before an approved upgrade, MIRA creates a rollback checkpoint, applies the candidate away from the known-good deployment, runs dependency/capability checks, migrations, stock/local tests, privacy/source audits, and CI, then verifies remote readback before promotion.

Stable capability contracts are preferred to reaching into another feature's private implementation. This allows the M.I.R.R.O.R. internals to change without unnecessarily breaking local extensions.

## Portable deployment architecture

The reference deployment above uses Google authorities and ChatGPT scheduling. The reusable starter does not hard-code those providers or brief times:

| Portable role | Personal candidate | Microsoft/enterprise candidate | Apple/manual candidate |
|---|---|---|---|
| AI runtime / MIRA control plane | ChatGPT/Codex or Claude | approved organizational AI runtime | any approved web/local runtime |
| Source lineage | private GitHub template | GitHub Enterprise, GitLab, Azure Repos, or managed central source | pinned managed release |
| Structured state | Google Sheets | Microsoft Lists or explicit Excel tables in OneDrive/SharePoint | CSV/JSON manual exchange |
| Evidence | Google Drive | OneDrive or SharePoint document library | iCloud Drive/user-mediated file exchange |
| Calendar projection | Google Calendar | Outlook Calendar | ICS manual exchange |
| Local integration agent | optional Linux/desktop agent | approved managed endpoint agent | platform-specific/manual bridge |

These are candidates, not installation claims. `starter/platform-capabilities.json` and `starter/tools/provider_capability_router.py` require observed capability-level read/write/readback. A provider name never proves access, feature parity, scheduling, or organization approval.

Regulated deployments use `starter/ENTERPRISE_PILOT.md`. Personal accounts and public services are never used to bypass organization policy.

## Standalone application and Linux integration

A standalone MIRA application can reuse the same source/feature contracts rather than inventing a second updater. The UI can expose feature inventory, provider readiness, plain-language upgrade differences, approval, rollback history, and connection status while the reconciliation engine remains the single policy implementation.

A Linux integration agent can add local filesystem indexing/watchers, systemd services/timers, D-Bus notifications, constrained local command execution, secret-store access, hardware/device adapters, local backup jobs, container/process isolation, and optional offline/local-model execution. Each capability must be advertised and authorized independently; installing an agent is never blanket root or filesystem permission.
