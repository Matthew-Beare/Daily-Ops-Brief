---
name: ops-brief-policy
description: Run and maintain the user's Daily Ops Brief and LyfeOS receipt control room using the live Ops Status Register, Mileage & Pay Tracker, Purchase & Receipt Archive, Gmail evidence, and deterministic HOME/ROAD policy. Use for scheduled/manual briefs; inbox/shipment reconciliation; archive approval; mode/vacation/home-early changes; task/control updates; ROAD trips/routes/mileage; receipt/order lifecycle work; reimbursements and payment reconciliation; vendor-contact proposals; and any receipt, invoice, packing slip, product-label, barcode, screenshot, or receipt photo supplied in any supported Chat, Work, Project, voice, dictation, or connected-file context. Also use for any clear request from any supported conversation to add/update/complete/pause/remove something from the Daily Brief, Ops Brief, or Ops list. Do not use for unrelated reminders or generic spreadsheets.
---

# Ops Brief Policy

Keep mutable state in the live Sheets, lasting policy/code/tests/bootstrap in the configured private Git repository, and scheduled prompts limited to slot selection. The installed skill is a deployed runtime copy, not a second policy authority. Never copy the mutable task, route, trip, mileage, suppression, override, shipment, receipt, payment, reimbursement, alias, or run-log database into prompts, instructions, memory, or another file.

## Authority

- Timezone: `America/New_York`.
- Ops Status Register: `https://docs.google.com/spreadsheets/d/10WMU_hDMfSJcACel--8LekT7So5MXKgWuLVxvnSCPNU/edit`.
- Mileage & Pay Tracker: `https://docs.google.com/spreadsheets/d/1OUzdjZaVTidLnMX2xuIZ3mRVDOF5oAfT8-pdl6KfUfI/edit`.
- Purchase & Receipt Archive: `https://docs.google.com/spreadsheets/d/1pHkTdCxmdBdZjnVu97FkpkiSjysLkhjuTEcfcEXzmW8/edit`.
- Deployed runtime engine: `scripts/ops_policy_runtime.py`; it wraps `scripts/ops_policy.py` until hardened behavior is folded into the base engine.
- Deployed shipment reconciler: `scripts/reconcile_shipments.py`.
- The `Shipments` tab is an active queue only. Durable purchase/lifecycle history belongs in the Purchase & Receipt Archive; source email/images remain evidence.
- If the Ops Status Register is unavailable, report `Action Required — Ops Status Register unavailable.` Never substitute remembered or previously rendered mutable state.
- Mileage/pay failure is section-scoped. It never destroys an otherwise valid brief; on Thursday emit `Action Required — mileage/pay Sheet unavailable` and continue other sections.

## Route the request

- For a scheduled or manual brief, read [the brief-run workflow](references/brief-run.md) completely and execute it. Do not load state-maintenance instructions during the run.
- For task, control, mode, mileage, automation, or other persistent-state maintenance, read [the state-maintenance workflow](references/state-maintenance.md) completely before acting.
- For shipment, order-email, inbox-filing, archive-approval, or explicit email-deletion work, read [the email-reconciliation workflow](references/email-reconciliation.md) completely before acting.
- For purchase-receipt ingestion, Drive receipt filing, monthly receipt rollups, cancellation/refund resolution, fitment/part-number assignment, or inventory side effects, read both [the receipt-ingestion workflow](references/receipt-ingestion.md) and [line classification/fitment/financial resolution](references/receipt-classification-fitment.md) completely before acting.
- If the purchase evidence is an image, screenshot, scanned receipt, product-label photo, barcode, or photographed paper receipt, additionally read [receipt photo/screenshot intake](references/receipt-photo-intake.md) completely. The receiving conversation is only an intake surface; write the canonical LifeOS receipt state, never a chat-local copy.
- For a purchase made for another person or external asset, or any expected/received payback, additionally read [household, beneficiary, and reimbursement reconciliation](references/household-reimbursement.md).
- For expected merchant charges, posted/pending card evidence, unmatched charges, over/undercharges, or settlement that has not appeared yet, additionally read [payment and merchant-charge reconciliation](references/payment-reconciliation.md).
- Before proposing or sending any external email/contact, read [vendor contact discovery and email approval](references/vendor-contact.md). Never reply blindly to an unmonitored/no-reply address.
- For cross-chat intake, chat deletion/recovery safety, or a fresh conversation continuing prior LifeOS work, read [cross-chat intake and disposable chat history](references/chat-portability.md).
- For any route, trip, ETA, location, arrival, or ROAD-weather-watch change, or when the brief engine activates route weather, read [the route-weather workflow](references/route-weather.md) completely before acting.
- For a continuation/recovery phrase, read state maintenance and chat portability, inspect the live automation list and Sheets, then continue from those authorities without requiring a magic sentence.

## Non-negotiable invariants

- Keep exactly one active Ops Brief automation. It dispatches at both 2:45 AM and 2:45 PM Eastern; the PM brief is the user's “morning” brief.
- Never revive 3:00 AM/PM, Pacific, UTC-shifted, noon, midnight, duplicate, or extra Ops Brief schedules.
- Keep each scheduled run single-purpose: render one brief and record one deterministic Run Log result.
- Mode precedence is: live unexpired explicit Mode Override, then an active trip forces ROAD, then the weekly default. Expired overrides are ignored.
- A clear `got home early` statement is an immediate HOME override and work-cycle close. It keeps briefs HOME through the next Friday 2:45 PM brief; runtime uses an exclusive Friday 3:00 PM Eastern expiry.
- Never hard-code task-specific exceptions; use live row fields and engine result.
- Never display appointment-confirmation state. It is hidden anti-nag state only.
- Appointment reminders are mode-independent: Saturday 2:45 AM previews the next seven calendar days; other 2:45 AM briefs show that day, and every 2:45 PM brief shows the next day.
- Thursday mileage/pay is mode-independent. Mileage accrual closes at confirmed HOME arrival, normally Wednesday PM or earlier; Thursday reports the closed work cycle. Use company/user-reported paid miles only; never infer settlement miles from map distance or copy terminal mileage into the reverse direction.
- Reconcile Gmail against active `Shipments` before either brief. Read complete materially relevant threads; snippets alone are not evidence.
- Delete delivered items from active `Shipments` immediately. Report a newly observed delivery once from `Order Events`, then never re-report it.
- One Receipt ID may contain line items in different categories and assigned to different assets/projects/beneficiaries. Classify items independently; count the transaction once and keep allocations balanced to the one supported merchant total.
- A receipt image, screenshot, email, and account transaction that refer to the same purchase are evidence sources for one transaction, not separate purchases. Reconcile/dedupe before creating another Receipt ID.
- When a UPC, GTIN, SKU, manufacturer part/model, serial, exact dimensions, or sufficiently specific product identity exists, investigate exact identity and compatibility before final assignment. Cross-reference the complete owned/external asset registry, known modifications, surrounding order evidence, and exclusion evidence. Auto-assign when one asset uniquely survives the material checks. Queue only after reachable evidence has been exhausted, and record what ambiguity remains.
- Outside-person purchases remain normal merchant transactions. Track beneficiary/asset assignment and reimbursement separately; reimbursement never becomes a merchant refund and never erases gross purchase history. Household dashboards may show both gross paid and net household cost.
- Treat a replacement with a new merchant order number as a new Receipt ID linked bidirectionally to the original; never overwrite the cancelled order. A same-order revision stays under the original Receipt ID and becomes the expected-charge source when it is the strongest merchant evidence.
- Every supported expected merchant charge remains open in `Payment Reconciliation` until matched, split-matched, resolved as no-settlement, or otherwise financially resolved. Missing settlement is a valid waiting state; later posted amounts must be compared to the latest same-order revision. A larger unexplained posted charge is a possible merchant overcharge, not an acceptable variance.
- Investigate material card charges that do not align with any known purchase by searching receipt/order evidence before classifying them as unmatched. Never fabricate a receipt to explain a charge.
- Cancellation lifecycle and refund state are separate. Determine whether money actually settled before expecting a refund. Preserve cancelled history, remove it from active fulfillment/spend when confirmed, and require exact merchant/account evidence for any expected settled refund/reversal. Only an expected correction still unresolved after five business days becomes `Action Required`.
- Never guess unknown classification or fitment. `Classification Queue` is the last resort after investigation, not the first response to incomplete receipt text.
- Mutable people/asset aliases and reimbursement/payment state live in canonical Sheets. Operational history must remain recoverable after old chats are deleted; chat history is never the sole authority.
- Keep important email in Inbox under `Ops/Archive Approval` until the user approves archiving. Silence is not approval.
- Never send email automatically. Before any external email, validate the recipient, detect unmonitored/no-reply instructions, research the current official support channel when needed, show recipient + subject + complete proposed message, and obtain explicit pre-send confirmation for that specific message. Do not delete Gmail without an explicit bounded request.
- Do not monitor promotions or sales unless the user explicitly reinstates that scope.
- For a lasting Ops policy change, provide the complete revised project-instructions block when the bootstrap contract changes; never provide a partial instructions patch.
- The configured private Daily-Ops-Brief repository is the sole policy source of truth. For every lasting policy/schema/workflow/schedule/onboarding/output change, update validation/tests/fingerprint, commit and push, redeploy the installed skill from committed source, and verify the remote result without waiting for a separate Git prompt. Never auto-merge, publish publicly, or commit mutable data or secrets.
- Prefer an explicit degraded result over retries, loops, or a run that never finishes.
