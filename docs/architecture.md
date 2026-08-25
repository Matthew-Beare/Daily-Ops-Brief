# Architecture

M.I.R.R.O.R. separates mutable state, deterministic policy, evidence, scheduled dispatch, versioned recovery material, feature ownership/dependency lineage, and replaceable runtime adapters.

At the product boundary, **MIRA is the control plane**: conversation, reasoning, planning, dependency analysis, user approval, reconciliation, recommendations, model routing, and approved execution. **M.I.R.R.O.R. is the reality/data plane plus durable structure**: canonical state/evidence interfaces, policy, schemas, provenance, feature lineage, and the records that describe reality. The data-plane analogy is useful but intentionally approximate because M.I.R.R.O.R. owns more durable structure than a classic packet-forwarding plane.

| Layer | Authority | Responsibility |
|---|---|---|
| Mutable Ops state | Selected structured-state adapter via Authority Registry | Tasks, controls, routes, trips, shipments, suppressions, run logs |
| Mileage state | Selected structured-state adapter via Authority Registry | Company-paid miles, frozen rate, gross estimate, pay-week history |
| Purchase state | Selected structured-state adapter via Authority Registry | Transactions, items, lifecycle events, expense allocations, classification queue, audit gate |
| Evidence | Selected evidence adapters | Complete threads, appointments, receipt attachments, manuals, photos and archives |
| Policy | `skill/ops-brief-policy` + portable feature contracts | Routing, invariants, deterministic workflow, failure boundaries |
| Feature ownership/dependencies | `starter/features.lock.json` + `starter/feature-dependency-map.json` | Durable owner/origin/lineage, feature dependencies, required/optional capabilities, rollback/conflict policy |
| Behavior dependencies | `starter/behavior-dependencies.json` | Dependency coverage and readiness contract for every cataloged behavior |
| Integration health | Deployment Integration Registry | Verified connected capabilities, provider/resource references and dependency health |
| MIRA reconciliation control plane | `starter/tools/feature_reconciliation.py` + approved AI runtime | Non-mutating upgrade comparison, dependency readiness, overlap/consolidation proposals, Boomer-mode explanation, user approval boundary |
| Runtime interface boundary | `starter/runtime-interface-contract.json` | Provider-neutral state, evidence, scheduler, notification, client API, model and scan interfaces |
| Control-cycle dispatcher | Selected scheduler adapter | Reconcile selected workflows and emit configured briefs at deployment-owned times |
| Recovery | Git source + verified provider state | Tests, templates, documentation, policy fingerprints, feature rollback checkpoints, state/evidence readback |

The current reference deployment can use Google authorities and a hosted scheduler, but those are adapters rather than product assumptions. The dispatcher carries no mutable database. It invokes the same policy/service boundary regardless of whether the eventual scheduler is hosted, `systemd`, or cloud-native.

See [M.I.R.R.O.R. Runtime Platform Architecture](runtime-platform-architecture.md) for the service/API, storage-adapter, client, Linux, cloud, barcode/QR, notification, networking, and model-routing boundaries. See [LyfeOS Data Model](lyfeos-data-model.md) for keys, relationships, and migration semantics.

The generic starter is separate from the current deployment. It may generate a new bootstrap contract, but it must not inherit the current user's identifiers or operational rows.

## Feature and upgrade architecture

Features are modular packages with explicit manifests, failure domains, dependencies, permissions, state boundaries, and tests. They normally remain in one repository/process. Separate network services are introduced only for a real isolation, privilege, scaling, hardware, or platform boundary; microservices are not used merely to simulate modularity.

Every feature has durable ownership and lineage. User-created features default to user ownership. Locally modified stock features retain their upstream base plus a local revision. CI rejects unowned features and a stale dependency map.

Upstream updates are three-view reconciliations: originally adopted upstream state, current deployment state, and candidate upstream state. The candidate is a proposal, never a replacement image. User-owned/local behavior is preserved by default and every changed feature remains user-in-the-loop. AI may propose consolidation or compatibility repair, but cannot delete or overwrite local behavior on its own.

Before an approved upgrade, MIRA creates a rollback checkpoint, applies the candidate away from the known-good deployment, runs dependency/capability checks, migrations, stock/local tests, privacy/source audits, and CI, then verifies remote readback before promotion.

Stable capability contracts are required instead of reaching into another feature's private implementation or a provider-specific API from core behavior. This allows M.I.R.R.O.R. internals and storage providers to change without unnecessarily breaking local extensions.

## Portable deployment architecture

The reusable starter supports multiple topologies without changing behavior semantics:

| Portable role | Browser/connector | Self-hosted Linux | Cloud/managed |
|---|---|---|---|
| AI runtime / MIRA control plane | ChatGPT/other approved runtime | local and/or approved hosted model adapters | approved hosted/local service runtime |
| Source lineage | private/user Git or managed release | Git/managed source | Git/managed source |
| Structured state | Sheets/Lists/verified equivalent | PostgreSQL through service API | managed PostgreSQL/compatible relational store through service API |
| Evidence | Drive/OneDrive/verified equivalent | S3-compatible/object storage or bounded local evidence adapter | managed object storage |
| Calendar projection | Google/Outlook/verified adapter | provider calendar adapter | provider calendar adapter |
| Scheduler | hosted task adapter | `systemd` service/timer adapter | managed scheduler/queue |
| Client surfaces | browser/chat | web + Windows/Linux desktop + Android | web + Windows/Linux desktop + Android |

These are candidates, not installation claims. `starter/platform-capabilities.json`, `starter/runtime-interface-contract.json`, and the provider/integration routers require observed capability-level read/write/readback. A provider name never proves access, feature parity, scheduling, or organization approval.

Regulated deployments use `starter/ENTERPRISE_PILOT.md`. Personal accounts and public services are never used to bypass organization policy.

## State and evidence migration rule

Google Sheets and Drive are supported current adapters, not schema authorities. Canonical UUIDs, relationship/event semantics, idempotency keys, evidence hashes, provenance, and source identities belong to M.I.R.R.O.R. and survive backend migration.

A future PostgreSQL/object-storage cutover uses staged mirror/parity/readback/restore validation. Business features do not change from `GoogleSheetsThing` to `PostgresThing`; the Authority Registry points the same capability contract to a different verified adapter.

Clients and AI runtimes never receive unrestricted database credentials. Normal writes flow through the bounded M.I.R.R.O.R. service/API so validation, authorization, deduplication and audit semantics remain identical across storage engines.

## Standalone application and Linux integration

Web, Windows/Linux desktop, and Android clients reuse the same service contracts rather than inventing separate business policy. Clients handle presentation, local capture, secure local credentials, device capability reporting, notification/TTS delivery, and bounded offline queues. The server/control plane owns canonical behavior.

A Linux integration agent can add local filesystem indexing/watchers, `systemd` services/timers, D-Bus notifications, constrained local command execution, secret-store access, hardware/device adapters, local backup jobs, container/process isolation, barcode/QR bridges, and optional offline/local-model execution. Each capability must be advertised and authorized independently; installing an agent is never blanket root or filesystem permission.

Deterministic Linux jobs do not inherently consume model tokens. They may run dependency checks, scheduling, database reconciliation, backups, barcode processing, and other rule-based work locally. Model usage begins only when a workflow explicitly invokes a model adapter under `starter/model-routing-policy.json`.

## Networking boundary

A self-hosted database stays private. Local clients may use LAN access; remote personal clients should normally use an authenticated private overlay such as WireGuard/Tailscale or an intentionally published HTTPS API behind a reverse proxy. PostgreSQL itself is not exposed merely to serve Android/web/AI clients.

Public API deployment requires TLS, scoped short-lived credentials, server-side authorization, audit logging, rate limiting, and strong account authentication/MFA where practical. Service-to-service mTLS is optional when justified. The same API/storage boundary can later run in a cloud environment without changing the feature model.
