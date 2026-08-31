# MIRA // MIRROR Product Roadmap

Git is the authority for product-development state. This roadmap defines phase order and product gates; `project/FEATURES.yaml` defines feature state, `project/CURRENT_WORK.yaml` defines the single active work packet, and `project/BACKLOG.yaml` holds work that is not active.

## Product identity

- **MIRROR is the reality layer:** memory, integrations, evidence, Reality Record, reconciliation, provenance, and durable canonical state.
- **MIRA is the intelligence layer:** conversation, reasoning, planning, recommendations, and execution.
- Default assistant name: **MIRA**.

## Development operating rule

Only one work packet may be active at a time. A packet may contain one substantial behavioral change or up to three tightly coupled small changes plus the tests and documentation required to prove them. New unrelated work discovered during a packet goes to `project/BACKLOG.yaml`; it does not expand the active packet.

Development must be interruption-safe. A chat/tool interruption must be recoverable from Git state, the active branch/PR, checkpoint commits, and `project/CURRENT_WORK.yaml` without relying on chat history.

## Phase 1 — Native MIRA v1

**Active production target:** ChatGPT MIRA + MIRROR core + Android.

Windows and Linux implementation work is deferred until this phase passes its acceptance gate. Core contracts must remain platform-neutral so deferred clients can implement them later without redesigning MIRROR.

### Phase 1 capability groups

1. **ChatGPT-native MIRA**
   - Normal users can operate MIRA in ChatGPT without requiring Linux, Docker, a homelab, VPS, or a separate MIRROR server.
   - Google Workspace is the primary native reality/storage integration for the stock path.
   - Provider access, reconciliation, and authority decisions remain explicit and auditable.

2. **MIRROR reality and reconciliation core**
   - Canonical reality/evidence contracts.
   - Deterministic reconciliation.
   - Idempotent retries and duplicate suppression.
   - Explicit ambiguity/conflict handling rather than silent guessing.
   - Provider outage and partial-failure safety.
   - Provenance and reversible/traceable changes where appropriate.

3. **Daily operating loop**
   - Daily Cleanup contracts and execution.
   - LyfeOS/MIRROR Control Cycle.
   - `$ops brief` manual invocation.
   - Exactly two scheduled Ops Briefs daily at **02:45** and **14:45** `America/New_York`; no duplicate/legacy schedules.
   - Mutable operational facts are read from their canonical authorities before conclusions are produced.

4. **AI execution modes**
   - Hybrid AI routing.
   - Manual/no-AI operation for workflows that must remain usable without model execution.
   - AI may assist interpretation but may not silently replace canonical authority semantics.

5. **Receipts, evidence, orders, and ingestion**
   - Receipt/evidence queue.
   - Deduplication and provenance.
   - Safe reconciliation into canonical records.
   - Recovery after interrupted processing.

6. **Android companion**
   - Reliable build/install path.
   - Authentication/reconnection.
   - Shared canonical state with ChatGPT/MIRROR.
   - Notifications/reminders and local TTS where supported.
   - Capture/ingestion surfaces needed by Native MIRA v1.
   - Restart/retry recovery and duplicate-safe behavior.

7. **Onboarding, migration, and recovery**
   - Boomer-level first-run path for nontechnical users.
   - Existing-user migration without losing canonical identity/provenance.
   - Interrupted-run recovery.
   - Disaster/rebuild recovery from durable authorities and versioned contracts.

### Native MIRA v1 acceptance gate

Phase 1 is complete only when all required Phase 1 features in `project/FEATURES.yaml` are marked accepted and verified. At minimum:

- ChatGPT-native bootstrap works without requiring self-hosted infrastructure.
- Android authenticates/reconnects and reads the same canonical reality model.
- Google-native reconciliation is deterministic, idempotent, conflict-safe, and tested for partial failure.
- Daily Cleanup works end to end.
- `$ops brief` works manually and on exactly the two canonical Eastern-time schedules.
- Receipt/evidence ingestion and reconciliation work end to end without duplicate canonical records.
- Hybrid-AI and manual/no-AI modes both satisfy the same authority contracts.
- Interrupted runs resume safely.
- Provider outages do not corrupt canonical state.
- Existing-user migration and fresh-user onboarding are tested.
- Android restart/device-restart recovery is tested for required background behavior.
- Required unit, contract, integration, security, and Native-MIRA smoke tests are green.
- The release candidate has no unresolved P0/P1 Native-v1 blockers.

## Phase 2 — Windows client

**Status: deferred until Native MIRA v1 passes.**

Implement the existing platform-neutral MIRROR contracts on Windows. Do not redesign core semantics for Windows-specific convenience.

## Phase 3 — Linux client

**Status: deferred until Native MIRA v1 passes.**

Implement the same platform-neutral MIRROR contracts on Linux after Native MIRA v1 is accepted. Self-hosting remains optional rather than a stock-user requirement.

## Scope discipline

A new idea does not become active development merely because it is useful. It enters the backlog with priority, dependency, platform, and acceptance notes. Reprioritization requires an explicit packet transition; otherwise the current packet continues.