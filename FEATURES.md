# MIRROR FEATURES

This is the canonical human-readable feature registry front door. The full registry is being reconstructed under roadmap milestone G0.

## Audit status

**IN PROGRESS.** Until G0 completes, the existing forensic ledger (`docs/feature-ledger-2026-08-24.md`), generated catalog (`docs/feature-catalog.json` / `.md`), current `main`, tests, PR #31, and relevant branch evidence are audit inputs. No single legacy artifact is sufficient by itself.

A feature is not considered delivered merely because code, a test, a document, or a branch exists.

## Stable feature record

Every audited feature will receive a permanent semantic ID and these fields:

- **ID** — stable; never changes because a table is reordered.
- **Name** — concise capability name.
- **Description** — complete user-observable purpose and scope.
- **Decision state** — required / accepted / proposed / deferred / rejected / superseded / unresolved.
- **Delivery state** — desired / specified / implemented / test-verified / integration-verified / live-verified.
- **Milestone** — current roadmap target.
- **Dependencies** — feature IDs that must exist first.
- **Enables** — downstream capabilities materially unlocked by this feature.
- **Acceptance criteria** — observable conditions required for the next delivery state.
- **Evidence** — source, test, branch, provider-readback, or runtime proof.
- **Notes/constraints** — safety, privacy, compatibility, migration, or UX constraints.

## ID families

The audit may extend these families, but IDs must remain semantic and immutable once assigned:

- `CORE-*` — authority, identity, state, reconciliation, provenance.
- `OPS-*` — briefs, runtime control, work/trip/operational state.
- `CAL-*` — calendar, appointments, reminders.
- `MAIL-*` — email ingestion/triage/communication safety.
- `ORDER-*` — orders, shipments, returns, replacements.
- `FIN-*` — spending/payment/refund/reimbursement organization.
- `ASSET-*` — assets, evidence, fitment, specifications.
- `INV-*` — inventory, locations, movement, QR/RFID.
- `HOUSE-*` — household routines, pantry, meals, laundry.
- `ONBOARD-*` — onboarding, profiles, configuration.
- `PROVIDER-*` — Google/Microsoft/Apple/portable provider capabilities.
- `CLIENT-*` — ChatGPT, web, Android, desktop, CLI surfaces.
- `DIST-*` — packaging, distribution, updates, channels.
- `ENTERPRISE-*` — locked-down/institutional deployment boundaries.
- `DEV-*` — development/recovery/control-plane capabilities.

## Verification rule

Repository CI proves only repository behavior. It does not prove provider permissions, live scheduler firing, physical-device behavior, production signing, external API registration, or mutable-state readback. Those require their own evidence.

## Data preservation rule

Legacy production Google spreadsheets, Drive artifacts, briefs, schedules, and state are not MIRA 2.0 development fixtures. New implementation must use a separate sandbox namespace until an explicit migration packet is approved.

## Current audit queue

See `ROADMAP.md` G0 and `CURRENT_WORK.md` for the single active audit slice. The registry below will be populated slice-by-slice and committed after each bounded audit packet rather than reconstructed in one fragile mega-session.
