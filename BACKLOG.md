# MIRROR BACKLOG

This backlog is **not FIFO**. Arrival order never determines implementation order by itself. Priority is recomputed from dependency, active milestone value, blocking risk, architectural leverage, user value, and verification needs.

New customer ideas are captured here by default and do not expand `CURRENT_WORK.md` unless they are required to satisfy the active packet or the customer explicitly reprioritizes.

## Priority classes

1. **BLOCKER** — prevents active packet/milestone acceptance or protects data/security/integrity.
2. **PREREQUISITE** — foundational dependency that unlocks higher-value work.
3. **VERTICAL** — user-visible end-to-end slice for the active milestone.
4. **HARDENING** — reliability, test, migration, observability, recovery.
5. **ENHANCEMENT** — useful but not required for the active proof.
6. **LATER** — valid direction intentionally outside current milestone.

## Open work

| Work ID | Class | Related features | Work | Dependencies | Status / disposition |
|---|---|---|---|---|---|
| `DEV-001` | BLOCKER | `DEV-*` | Complete G0 authoritative feature audit in bounded slices and assign stable semantic IDs. | `G0-001` control-plane checkpoint | active roadmap |
| `DEV-002` | PREREQUISITE | `DEV-*` | Add machine-readable dependency metadata and validation for feature IDs, cycles, status transitions, and packet references. | full G0 registry | queued for G1 |
| `DATA-001` | BLOCKER | `CORE-*` | Preserve all existing Google spreadsheets, Drive artifacts, briefs, schedules, and live MIRA state as read-only legacy production during MIRA 2.0 development. | none | invariant |
| `DATA-002` | PREREQUISITE | `CORE-*`, `PROVIDER-*` | Create a separate MIRA 2.0 Google sandbox/reality namespace and prove by provider readback that no legacy artifact was overwritten, renamed, or repurposed. | G0 audit + control-plane rules | queued for G1 |
| `MIG-001` | LATER | `CORE-*` | Design an explicit legacy-to-MIRA-2.0 migration with backup, rollback, dry-run/diff, reconciliation, and provider readback. | stable MIRA 2.0 schema + vertical proof | deferred; never implicit |
| `PR31-001` | HARDENING | multiple | Freeze PR #31 as integration/reference work; map every capability to the audited registry and salvage only bounded pieces. | G0 registry | queued for G2 |
| `CORE-ROUNDTRIP-001` | VERTICAL | `CORE-*`, `PROVIDER-*`, `CLIENT-*` | Prove stock ChatGPT can create/read/mutate/dedupe/read-back one canonical Google-backed entity. | dependency graph after G0, MIRA 2.0 sandbox | provisional M0 |
| `ANDROID-SYNC-001` | VERTICAL | `CLIENT-*`, `CORE-*` | Prove Android reads and mutates the same canonical entity without becoming a second authority. | core roundtrip | provisional M1 |
| `OPS-VSLICE-001` | VERTICAL | `OPS-*`, `CLIENT-*` | Generate/deliver one real Ops Brief from canonical MIRA 2.0 state with run identity and failure isolation. | core + Android delivery prerequisites | provisional M2 |
| `DESKTOP-PARITY-001` | LATER | `CLIENT-*` | Windows/Linux/PWA/CLI product parity and packaging. | working core vertical slices | deferred |
| `RFID-001` | LATER | `INV-*`, `ASSET-*`, `CLIENT-*` | RFID inventory capture and handheld/wand hardware direction. | stable asset/location/movement schemas | deferred |
| `LOCAL-SVC-001` | LATER | `PROVIDER-*` | Optional Home Assistant/Plex/Paperless/Node-RED/MQTT/local-service integrations. | authority model + integration contracts | deferred |
| `ENTERPRISE-001` | LATER | `ENTERPRISE-*` | Institutional/locked-down deployment and policy-compliant integration path. | stock product core + provider abstraction | deferred |

## Re-ranking rule

When a new idea is added, the developer must:

1. assign or link stable feature/work IDs;
2. identify hard dependencies and downstream capabilities it enables;
3. determine whether it blocks the active packet or milestone;
4. re-rank affected backlog items;
5. leave active work unchanged unless required for acceptance or explicitly reprioritized by the customer.

A newly added item may therefore become the next packet immediately if it is a prerequisite, even though it was the most recently added backlog item.
