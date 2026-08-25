# M.I.R.R.O.R. Runtime Platform Architecture

## Purpose

M.I.R.R.O.R. must be able to begin as a low-cost browser/connector deployment and later move to an always-on Linux service with PostgreSQL and object storage without rewriting behavior policy or user-created features. The same core must also support web, Windows/Linux desktop, Android, and future cloud-native deployment.

This document is a design constraint, not an aspirational diagram. New production behavior must cross the interfaces below rather than binding directly to a provider or client surface.

## Architectural rule

**MIRA is the control plane. M.I.R.R.O.R. is the durable reality/data plane plus policy and lineage. Clients, storage engines, schedulers, notification systems, AI models, and provider integrations are replaceable adapters.**

Business behavior may depend on a capability such as `structured_state_write`, `evidence_write`, `spoken_notification`, `calendar_read`, or `barcode_decode`. It must not require a particular implementation such as Google Sheets, Drive, PostgreSQL, Android, Windows, or one model vendor unless the feature itself is explicitly provider-specific.

## Stable service boundary

All client surfaces and AI runtimes should converge on one bounded service/API layer. That service owns mutation validation, identity, idempotency, authorization, dependency preflight, audit logging, and readback. It is the only normal writer to canonical structured state.

The long-term logical stack is:

1. **Clients** — web, Android, Windows desktop, Linux desktop, command-line/admin, and approved AI runtimes.
2. **MIRA control plane** — conversation, planning, semantic reconciliation, upgrade proposals, model routing, and user approval.
3. **M.I.R.R.O.R. service/API** — deterministic policy, dependency checks, validation, idempotency, authorization, transaction boundaries, audit, and provider-neutral domain operations.
4. **Adapters** — state, evidence, calendar, mail, scheduler, notifications, barcode/QR decoding, model runtime, search/enrichment, and source control.
5. **Authorities** — PostgreSQL/Sheets/List-style structured state, object storage/Drive-style evidence, provider calendars/mailboxes, source repositories, and append-only audit/event history.

No client receives direct database credentials. No AI runtime receives unrestricted SQL credentials. No UI owns business policy.

## Deployment topologies

### Browser/connector starter

Lowest operational burden. ChatGPT or another approved AI runtime uses verified connectors/adapters. Google Sheets/Drive/Calendar may provide structured state, evidence, and projection. This is a supported deployment, not the architectural center.

### Self-hosted Linux

An always-on Linux host runs the M.I.R.R.O.R. service, scheduler, integration workers, optional local-model runtime, PostgreSQL, and optionally S3-compatible object storage. Desktop/web/Android clients reach the API through authenticated private networking or a deliberately published HTTPS endpoint.

Use `systemd` services and timers rather than requiring cron. Timers perform deterministic preflight, ingestion, reconciliation, backup, and dispatch work. AI inference is invoked only when the selected workflow actually needs a model.

### Cloud native

The same service can run in containers or managed application platforms with managed PostgreSQL/object storage and a managed scheduler/queue. Deployment may be a single service at first; splitting into separate services is driven by isolation, scaling, privilege, or reliability requirements rather than fashion.

The core must not depend on local filesystem paths, local process state, a specific cloud vendor, or a particular scheduler.

## Storage contracts

### Structured state adapter

Every structured-state implementation must support the equivalent of:

- health/readiness;
- schema/version discovery;
- exact-key get and bounded query;
- idempotent create/upsert;
- append-only event insertion where required;
- atomic or explicitly compensated multi-record mutation;
- uniqueness and relationship validation;
- readback of the committed material fields;
- export/migration without changing canonical UUIDs.

Google Sheets may implement this contract today. PostgreSQL should implement the same contract later with stronger transactions and constraints. Features call the contract, not the provider.

### Evidence adapter

Evidence implementations must support stable evidence UUIDs, content hashes, metadata, provenance, put/read/readback, retention policy, and canonical locator/reference. Google Drive, OneDrive/SharePoint, local/S3-compatible object storage, or another verified provider may implement it.

Moving evidence from Drive to object storage changes a locator and adapter, not the identity of the evidence object or linked asset/transaction/knowledge record.

### Scheduler adapter

Scheduling is deployment state. The scheduler contract accepts explicit user-configured timezone and slots, lists installed schedules, verifies them by readback, records observed firing evidence, and supports removal/update without changing behavior code.

A Linux implementation should prefer `systemd` timers. A cloud implementation may use a managed scheduler. A browser-only deployment may use an approved hosted task system. No product-default brief time is required.

### Notification adapter

Notifications are intents, not direct platform calls. Supported capability classes include visual notification, spoken notification, email projection when explicitly approved, and client in-app delivery. A reminder remains one canonical reminder even if it projects to more than one delivery channel.

## Client contract

Web, Windows/Linux desktop, and Android clients must use a versioned API contract. Client responsibilities are presentation, local capture, local barcode/QR decoding when available, local notification/TTS delivery, device capability reporting, secure token storage, and offline queueing where supported.

Clients must not reproduce canonical reconciliation policy. An Android client and a Windows client should obtain the same answer for the same canonical state because the server/control-plane contract owns the behavior.

The API should support at minimum:

- authenticated identity/session;
- capability/integration registration and health;
- query/read models;
- bounded command/mutation requests with idempotency keys;
- evidence upload/download metadata;
- reminder/notification intents;
- barcode/QR scan events;
- synchronization cursor/event feed;
- feature/dependency health;
- rollback/update status.

## Android-first mobile architecture

Android is the first native mobile target. The client should support camera barcode/QR decoding, secure local credentials, notification channels, Text-to-Speech delivery, Bluetooth-routed audio as provided by Android/device configuration, background work within Android platform limits, and upload/sync of evidence when connectivity returns.

A spoken reminder is considered supported only after the Android client verifies the device's `spoken_notification` capability. The server produces the canonical reminder plus speech intent; Android owns TTS/audio routing. The server does not pretend it can directly select a hearing aid output path from the cloud.

## Appointment ingestion and identity enrichment

Appointment evidence may originate from email, calendar, manual entry, document/photo, or another verified source. Ingestion should:

1. extract candidate time, location, organization/person name, contact details, and source identity;
2. correlate against known appointment/provider entities and aliases before any public research;
3. reuse a previously verified entity/specialty/category rather than researching it again;
4. when unresolved and public research is allowed, perform bounded source-backed enrichment and retain provenance/confidence;
5. write the canonical appointment and linked entity identity;
6. project the appointment to a calendar if enabled;
7. create reminder intents from the canonical appointment;
8. accept owner correction as authoritative evidence, update aliases/bindings, and avoid repeating the same mistaken lookup.

The reminder engine never infers medical diagnosis, medication timing, or treatment advice.

## Barcode and QR architecture

Barcode/QR capture is an event source, not a database schema.

Supported scan classes are:

- **commercial product identifier** — UPC/EAN/GTIN or another namespaced product code;
- **asset tag** — opaque M.I.R.R.O.R. Entity UUID or signed/encoded reference printed on a user label;
- **location tag** — immutable Location UUID for shelf/bin/room/vehicle/container assignment;
- **evidence/reference tag** — optional link to a knowledge/evidence object.

Preprinted blank QR/barcode labels should be assigned to an Entity UUID or Location UUID at first use. The printed code itself is an identifier alias, never the only identity.

A product scan preserves the raw code and symbology, validates check digits when applicable, resolves product identity using cached identifiers first, then bounded product/OEM research, and only then creates/enriches an asset. Model/part/manual discovery retains provenance. A scan that cannot prove identity enters a classification queue rather than inventing a model number.

## Financial reconciliation boundary

Financial records must separate economic spending from account settlement. A card purchase may create merchant spend; the later checking-account payment to that card is a liability/transfer settlement and must not count as a second purchase. Refunds, reimbursements, transfers, debt payments, income, and merchant purchases retain separate event semantics.

Any financial adapter must preserve provider transaction identity, account identity, pending/posted state, transfer linkage where available, and reconciliation confidence. Ambiguous rows remain visible and unresolved rather than being silently counted twice or dropped.

## Model routing

Deterministic code is the default for clocks, dependency graphs, identity keys, database writes, dedupe, arithmetic, barcode decoding, migrations, scheduler logic, and permission checks. A model is used only for work requiring language/semantic reasoning.

Model routing is policy-driven and provider-neutral:

- deterministic/no-model path when rules can decide safely;
- local model for low-risk extraction/classification/summarization when allowed and validators can verify output;
- economical hosted model for ordinary semantic work when local quality is inadequate or unavailable;
- stronger hosted model for complex ambiguity, conflicting evidence, high-impact changes, difficult code/reconciliation, or failed lower-tier validation.

Escalation is triggered by explicit confidence/validation/conflict rules, not by a model deciding that it would like another try. A failed local result never mutates canonical state before escalation.

## Networking and security

PostgreSQL and object storage are not exposed directly to the public Internet for normal client use.

For a homelab deployment, preferred access is:

- private LAN for local devices;
- WireGuard/Tailscale-style authenticated private overlay for remote personal devices; or
- a deliberately published HTTPS API behind a reverse proxy when private overlay access is unsuitable.

If an API is publicly reachable, use TLS, strong identity authentication, short-lived scoped tokens, server-side authorization, rate limiting, audit logging, and MFA/passkey-capable identity where practical. Device/service credentials are scoped by capability. mTLS may be used for service/agent links when operationally justified.

Never expose PostgreSQL on the public Internet merely to make an Android or AI client work. Never embed database passwords in a client app.

## Migration rule

Provider migration is an adapter migration, not a domain rewrite.

Sheets/Drive to PostgreSQL/object-storage migration must preserve canonical UUIDs, event history, evidence hashes/provenance, ownership, relationships, and source identifiers. Run mirror/parity validation before cutover, then switch the Authority Registry to the new adapter only after read/write/readback and restore tests pass.

## Compatibility rule for new features

Every new feature must declare:

- canonical state classes;
- required and optional capabilities;
- provider-neutral interfaces it consumes;
- client capabilities if any;
- whether AI is required and which routing class applies;
- failure domain;
- offline behavior if applicable;
- privacy/security class;
- migrations and rollback behavior.

CI should reject a feature whose core behavior directly requires a provider implementation where a stable capability contract exists.
