---
name: ops-brief-policy
description: Run and maintain the user's Daily Ops Brief and LyfeOS control room using canonical Sheets, Gmail/Drive/Calendar/account evidence, deterministic travel policy, receipt/order/payment reconciliation, asset acquisition, reimbursements, and safe external-contact proposals. Use for scheduled/manual briefs; task/control changes; ROAD trips/routes/mileage; order/receipt lifecycle work; receipt photos/screenshots/barcodes; product/serial/model intake; expected charges; reimbursements; calendar projections; Gmail filing/retention; and clear named-LifeOS changes from supported conversations where required authorities are available.
---

# Ops Brief Policy

Keep mutable operational state in canonical Sheets, durable policy/code/tests/onboarding in the configured private Git repository, and scheduled prompts thin. The installed skill is a deployed runtime copy, not a second authority. Chat history is an intake/reasoning surface, never the sole database.

## Authority

- Timezone: `America/New_York`.
- Ops Status Register: `https://docs.google.com/spreadsheets/d/10WMU_hDMfSJcACel--8LekT7So5MXKgWuLVxvnSCPNU/edit`.
- Mileage & Pay Tracker: `https://docs.google.com/spreadsheets/d/1OUzdjZaVTidLnMX2xuIZ3mRVDOF5oAfT8-pdl6KfUfI/edit`.
- Purchase & Receipt Archive: `https://docs.google.com/spreadsheets/d/1pHkTdCxmdBdZjnVu97FkpkiSjysLkhjuTEcfcEXzmW8/edit`.
- Runtime engine: `scripts/ops_policy_runtime.py`; shipment reconciler: `scripts/reconcile_shipments.py`.
- `Shipments` is active fulfillment only; durable purchase/lifecycle/payment/asset history belongs in canonical tables/evidence.
- If Ops is unavailable, report `Action Required — Ops Status Register unavailable.` Mileage failure is section-scoped; on Thursday report mileage/pay unavailable and continue other valid sections.

## Route the request

- Brief: read `references/brief-run.md` completely.
- Persistent Ops/mode/mileage/automation state: read `references/state-maintenance.md`.
- Order/shipment/Gmail filing/archive/deletion: read `references/email-reconciliation.md`.
- Receipt ingestion/cancellation/refund/Drive filing: read `references/receipt-ingestion.md` plus `references/receipt-classification-fitment.md`.
- Receipt/image/barcode/label photo: additionally read `references/receipt-photo-intake.md`.
- New/enriched tool/equipment/asset from photo/model/serial/receipt: additionally read `references/asset-acquisition.md`.
- Purchase for another person/external asset or reimbursement: read `references/household-reimbursement.md`.
- Expected/pending/posted merchant charge, over/undercharge or unmatched charge: read `references/payment-reconciliation.md`.
- Calendar event projection from canonical state: read `references/calendar-projection.md`.
- External email/contact: read `references/vendor-contact.md`; never reply blindly to no-reply/unmonitored routes.
- Cross-chat intake/deletion/recovery: read `references/chat-portability.md`.
- Route/trip/ETA/location/weather: read `references/route-weather.md`.

## Non-negotiable invariants

- Exactly one active Ops Brief automation at 2:45 AM/PM Eastern and exactly one consolidated Receipt & Order Lifecycle at 1:45 AM/PM Eastern. No per-order/child/retry/3:00/UTC/Pacific duplicates.
- Scheduled runs perform their work and do not mutate automation definitions.
- Mode precedence: unexpired explicit override, then active trip forces ROAD, then weekly default. Home early immediately closes supported work accrual and holds HOME through the next Friday 2:45 PM brief (exclusive 3:00 PM ET expiry).
- Appointment reminder visibility is mode-independent and follows configured brief rules; never expose hidden anti-nag confirmation state.
- Mileage accrual closes at confirmed HOME arrival, normally Wednesday PM or earlier; Thursday is reporting-only. Use company/user/run-sheet paid miles, never map distance.
- **Paid terminal mileage is symmetric by terminal pair** unless the user explicitly gives an exception. When A↔B is reconciled, store/use the same paid-mile value both directions. Route geometry/runtime may remain directional.
- Shared/employer run sheets reconcile into existing Routes/Trips/Mileage using stable evidence and dedupe; never create a duplicate route database.
- Read complete relevant Gmail and reconcile active Shipments before brief/order output. Delivered fulfillment leaves active Shipments after durable event recording and is reported once.
- Correlated order mail is grouped under durable Gmail order-history labels. After delivery, carrier-originated FedEx/UPS/DHL logistics mail may be automatically moved to Trash only under the explicit audited 90-day retention rule in `email-reconciliation.md`; merchant/order/payment/support evidence is retained.
- One Receipt ID = one underlying merchant transaction/total. Line items may have different categories/assets/projects/beneficiaries; allocations balance to the supported total and spend is counted once.
- Receipt email/photo/screenshot/account evidence for the same purchase enriches one Receipt ID; do not create chat-local receipt state or duplicates.
- Investigate UPC/GTIN/SKU/part/model/serial and exact compatibility against the full owned/external asset registry, modifications and exclusion evidence. Auto-assign unique supported fitment; queue only after reachable evidence is exhausted.
- Asset acquisition dedupes by stable identifiers/evidence and links physical assets to receipt lines/evidence rather than duplicating financial transactions.
- Outside-person purchases remain merchant purchases. Reimbursement is separate from merchant refund; preserve gross purchase and verified net household cost.
- Same merchant order revision stays one Receipt ID and becomes the expected-charge source when strongest. A true replacement with a distinct merchant order gets a distinct linked Receipt ID.
- Every supported expected merchant charge stays open in `Payment Reconciliation` until matched/split-matched/no-settlement/resolved. Compare eventual posted amount with the latest supported revision; investigate unexplained over/under/unmatched charges instead of guessing.
- Cancellation != refund. Determine whether money settled; only an actually expected unresolved correction receives the five-business-day action.
- Calendar projection is opt-in per event class and deduped through `Calendar Projection`; revisions update existing Google events rather than creating duplicates. Never create one automation per event.
- Important mail remains under `Ops/Archive Approval` until explicit archive approval.
- Never send email automatically. Validate the recipient/channel, reject no-reply/unmonitored routes, research official support when needed, show recipient + subject + complete draft, and ask exactly `Do you want me to send this email?`.
- Outside the explicit 90-day FedEx/UPS/DHL carrier-retention class, Gmail deletion requires explicit bounded authority.
- Do not monitor promotions/sales unless explicitly reinstated.
- Durable behavior changes update validation/tests and are committed/pushed to the private repo. Never auto-merge/publish/force-push/commit mutable data or secrets.
- Prefer an explicit degraded result over loops or silent failure.
