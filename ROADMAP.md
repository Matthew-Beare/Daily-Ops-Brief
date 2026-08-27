# MIRROR ROADMAP

Git is authoritative. This roadmap orders milestones by dependency and product proof, not by idea arrival time.

## Governance and recovery

### G0 — Authoritative product-state audit
Goal: recover and classify every known MIRA/MIRROR feature, requirement, rejection, implementation candidate, and verification claim.

Audit slices are intentionally bounded so work survives session/tool failure:

1. `G0-001` — install control plane and preservation boundary.
2. `G0-002` — governance/core runtime + Brief/Time/Operational State.
3. `G0-003` — Calendar/Appointments/Mail/Communication Safety.
4. `G0-004` — Orders/Shipments/Receipts/Payments/Spending.
5. `G0-005` — Assets/Fitment/Inventory/Shopping/Household Storage.
6. `G0-006` — Profiles/Onboarding/Family/Customization.
7. `G0-007` — Portability/Providers/Distribution/Enterprise/Deployment.
8. `G0-008` — clients/platforms: ChatGPT, web/PWA, Android, Windows/Linux, CLI, notifications, packaging.
9. `G0-009` — PR #31 and significant unmerged-branch reconciliation against the registry.
10. `G0-010` — dependency graph validation, duplicate/superseded feature reconciliation, acceptance-criteria completeness, final audit signoff.

No product feature implementation is permitted inside G0 except fixes required to make the audit/control files valid and durable.

### G1 — Engineering control plane hardening
Goal: enforce stable feature/work IDs, dependency validity, packet rules, status transitions, and CI checks so project state cannot silently drift.

Includes creation of a separate MIRA 2.0 Google sandbox/reality namespace with explicit proof that legacy production artifacts are untouched.

### G2 — PR #31 salvage plan
Goal: turn the oversized integration PR into a reference quarry. Map reusable work into bounded future packets; never merge the whole feature surface merely because code exists.

## Product proof milestones

The exact order may change after G0 dependency analysis. Dependencies outrank this provisional ordering.

### M0 — Stock ChatGPT + Google MIRROR core
Prove one canonical entity can be created, read, mutated, deduplicated, and read back from stock ChatGPT using Google Workspace as the reality layer.

### M1 — Android companion vertical slice
Prove Android reads and mutates the same canonical entity without a second authority or duplicate state.

### M2 — Ops Brief vertical slice
Generate and deliver a real brief from canonical MIRROR state with deterministic run identity, failure isolation, and readback evidence.

### M3 — Orders, shipments, receipts, and reconciliation
Deliver one complete purchase lifecycle with cancellation/replacement/refund/evidence reconciliation.

### M4 — Assets and household inventory
Deliver stable asset identity, hierarchical locations, evidence linkage, and one scan-based movement flow before broad QR/RFID expansion.

### Later milestones
Windows/Linux/PWA parity, self-hosted MIRROR server, RFID hardware, Home Assistant/Plex/Paperless integrations, institutional deployment, broad Feature Studio, and other surfaces remain valid product directions but must follow dependency and vertical-slice evidence.

## Preservation invariant

Legacy production Google data remains untouched until a specifically approved migration packet exists. MIRA 2.0 development uses separate sandbox state. Migration is never an incidental side effect of development.
