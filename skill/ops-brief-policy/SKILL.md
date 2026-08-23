---
name: ops-brief-policy
description: Run and maintain the user's Daily Ops Brief and LyfeOS control room using canonical state, Gmail/Drive/Calendar/account evidence, deterministic travel policy, personal planning/accountability, study workflows, receipt/order/payment reconciliation, active shopping-list reconciliation, asset acquisition, knowledge/manual indexing, reimbursements, fail-fast recovery, and safe external-contact proposals. Use for scheduled/manual briefs; task/control changes; personal routines or study next actions; ROAD trips/routes/mileage; order/receipt lifecycle work; shopping-list purchase reconciliation; receipt photos/screenshots/barcodes; product/serial/model intake; manuals/reference documents; expected charges; reimbursements; calendar projections; Gmail filing/retention; repeated connector/API failures; and clear named-LifeOS changes from supported conversations where required authorities are available.
---

# Ops Brief Policy

Keep mutable operational state in canonical Sheets, durable policy/code/tests/onboarding in the configured private Git repository, retained files/evidence in canonical Drive, and scheduled prompts thin. The installed skill is a deployed runtime copy, not a second authority. Chat history is an intake/reasoning surface, never the sole database.

## Authority

- Timezone: `America/New_York`.
- Ops Status Register: `https://docs.google.com/spreadsheets/d/10WMU_hDMfSJcACel--8LekT7So5MXKgWuLVxvnSCPNU/edit`.
- Mileage & Pay Tracker: `https://docs.google.com/spreadsheets/d/1OUzdjZaVTidLnMX2xuIZ3mRVDOF5oAfT8-pdl6KfUfI/edit`.
- Purchase & Receipt Archive: `https://docs.google.com/spreadsheets/d/1pHkTdCxmdBdZjnVu97FkpkiSjysLkhjuTEcfcEXzmW8/edit`.
- Runtime engine: `scripts/ops_policy_runtime.py`; shipment reconciler: `scripts/reconcile_shipments.py`.
- `Shipments` is active fulfillment only; durable purchase/lifecycle/payment/asset/knowledge history belongs in canonical tables/evidence.
- If Ops is unavailable, report `Action Required — Ops Status Register unavailable.` Mileage failure is section-scoped; on Thursday report mileage/pay unavailable and continue other valid sections.

## Route the request

- Brief: read `references/brief-run.md` completely.
- Persistent Ops/mode/mileage/automation state: read `references/state-maintenance.md`.
- Personal planning, recurring routines, accountability, exercise-session organization, study/school planning, or project next actions: read `references/life-planning-accountability.md`.
- Order/shipment/Gmail filing/archive/deletion: read `references/email-reconciliation.md`.
- Receipt ingestion/cancellation/refund/Drive filing **and shopping/procurement reconciliation**: read `references/receipt-ingestion.md` plus `references/receipt-classification-fitment.md`.
- Receipt/image/barcode/label photo: additionally read `references/receipt-photo-intake.md`.
- New/enriched tool/equipment/asset from photo/model/serial/receipt: additionally read `references/asset-acquisition.md`.
- Manual, datasheet, technical PDF, download URL, or durable reference: read `references/knowledge-manual-ingestion.md` and link it to asset UUIDs when applicable.
- Purchase for another person/external asset or reimbursement: read `references/household-reimbursement.md`.
- Expected/pending/posted merchant charge, over/undercharge or unmatched charge: read `references/payment-reconciliation.md`.
- Calendar event projection from canonical state: read `references/calendar-projection.md`.
- External email/contact: read `references/vendor-contact.md`; never reply blindly to no-reply/unmonitored routes.
- Cross-chat intake/deletion/recovery: read `references/chat-portability.md`.
- Route/trip/ETA/location/weather: read `references/route-weather.md`.
- Repeated connector/API/tool failure, ambiguous partial write, scheduler execution timezone mismatch, CI loop, stalled workflow, or no forward progress: read `references/pants-filling-with-shit-report.md` and generate the Pants Filling With Shit Report when its circuit-breaker conditions are met.

## Non-negotiable invariants

- Exactly one active Ops Brief automation at 2:45 AM/PM Eastern and exactly one consolidated Receipt & Order Lifecycle at 1:45 AM/PM Eastern. No per-order/child/retry/3:00/UTC/Pacific duplicates.
- Scheduled runs perform their work and do not mutate automation definitions.
- A schedule is not verified by RRULE/TZID text alone. After every automation create/update, provider readback must show the stored/default/execution timezone equals the canonical `America/New_York` timezone as well as the intended local schedule. Travel/device timezone must never redefine scheduling authority. If provider readback disagrees and no reliable timezone setter is available, fail the automation-maintenance module closed and generate the Pants Filling With Shit Report rather than claiming success.
- Mode precedence: unexpired explicit override, then active trip forces ROAD, then weekly default. Home early immediately closes supported work accrual and holds HOME through the next Friday 2:45 PM brief (exclusive 3:00 PM ET expiry).
- Appointment reminder visibility is mode-independent and follows configured brief rules; never expose hidden anti-nag confirmation state.
- Mileage accrual closes at confirmed HOME arrival, normally Wednesday PM or earlier; Thursday is reporting-only. Use company/user/run-sheet paid miles, never map distance.
- **Paid terminal mileage is symmetric by terminal pair** unless the user explicitly gives an exception. When A↔B is reconciled, store/use the same paid-mile value both directions. Route geometry/runtime may remain directional.
- A historical/shared run sheet used as terminal-pair knowledge imports/upserts only unique canonical terminal pairs into `Routes`; do not manufacture hundreds of historical `Trips`/Mileage rows merely because the source lists repeated occurrences. Normalize proven terminal aliases/typos before dedupe and never create a second route database.
- Personal goals, routines, study plans and next actions use canonical mutable state and evidence. Do not infer completion from silence, do not nag after acknowledgement when prohibited, and let context modes change actionability without changing canonical time.
- Read complete relevant Gmail and reconcile active Shipments before brief/order output. Delivered fulfillment leaves active Shipments after durable event recording and is reported once.
- Correlated order mail is grouped under durable Gmail order-history labels. After delivery, carrier-originated FedEx/UPS/DHL/USPS logistics mail may be automatically moved to Trash only under the explicit audited 90-day retention rule in `email-reconciliation.md`; merchant/order/payment/support evidence is retained.
- One Receipt ID = one underlying merchant transaction/total. Line items may have different categories/assets/projects/beneficiaries; allocations balance to the supported total and spend is counted once.
- Receipt email/photo/screenshot/account evidence for the same purchase enriches one Receipt ID; do not create chat-local receipt state or duplicates.
- `Shopping & Procurement` is an active shopping list, not purchase history. When durable purchase evidence or explicit owner confirmation satisfies an open intent, preserve the durable purchase/reconciliation evidence in canonical receipt/order authorities and remove the fulfilled shopping row after verification. Revisions/replacements satisfy the same intent; a cancellation without replacement leaves it open. If exact receipt/product identity is unresolved but the owner confirms purchase, remove the fulfilled intent and keep missing identity as a separate reconciliation task rather than a `Purchased` tombstone.
- Investigate UPC/GTIN/SKU/part/model/serial and exact compatibility against the full owned/external asset registry, modifications and exclusion evidence. Auto-assign unique supported fitment; queue only after reachable evidence is exhausted.
- Every person/physical asset and retained knowledge object uses an immutable collision-resistant RFC 4122 UUID as canonical cross-database identity. Friendly IDs/names are aliases and UUIDs survive rename, ownership change, family expansion, or database migration.
- Asset acquisition dedupes by UUID/stable identifiers/evidence and links physical assets to receipt lines/evidence rather than duplicating financial transactions.
- Retained manuals/references live in canonical Drive and are indexed by immutable Knowledge UUID plus manufacturer/model/part/asset relationships so later queries can return the canonical Drive link and relevant source section.
- Outside-person purchases remain merchant purchases. Reimbursement is separate from merchant refund; preserve gross purchase and verified net household cost.
- Same merchant order revision stays one Receipt ID and becomes the expected-charge source when strongest. A true replacement with a distinct merchant order gets a distinct linked Receipt ID.
- Every supported expected merchant charge stays open in `Payment Reconciliation` until matched/split-matched/no-settlement/resolved. Compare eventual posted amount with the latest supported revision; investigate unexplained over/under/unmatched charges instead of guessing.
- Cancellation != refund. Determine whether money settled; only an actually expected unresolved correction receives the five-business-day action.
- Calendar projection is opt-in per event class and deduped through `Calendar Projection`; revisions update existing Google events rather than creating duplicates. Never create one automation per event.
- Important mail remains under `Ops/Archive Approval` until explicit archive approval.
- Never send email automatically. Validate the recipient/channel, reject no-reply/unmonitored routes, research official support when needed, show recipient + subject + complete draft, and ask exactly `Do you want me to send this email?`.
- Outside the explicit 90-day FedEx/UPS/DHL/USPS carrier-retention class, Gmail deletion requires explicit bounded authority.
- Retry is not mandatory. For a plausibly transient read/idempotent operation, the default maximum is the initial attempt plus one retry. Permission/authentication failures, deterministic validation failures, known-bad arguments, destructive operations, ambiguous writes, and scheduler timezone mismatches do not receive blind retries.
- If the same operation fails twice, two cycles make no forward progress, an ambiguous/partial mutation occurs, or scheduler readback contradicts canonical time, generate the Pants Filling With Shit Report: stop writes for that module, read back/preserve verified state, continue healthy unrelated modules, report one specific next action, and never create hidden retry jobs.
- Do not monitor promotions/sales unless explicitly reinstated.
- Durable behavior changes update validation/tests and are committed/pushed to the private repo. Never auto-merge/publish/force-push/commit mutable data or secrets.
- Prefer an explicit degraded result over loops or silent failure.