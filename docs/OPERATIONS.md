# Operating contract

## Scheduled dispatchers

Keep exactly these two active jobs in `America/New_York`:

- 2:45 AM: `Use $ops-brief-policy to run the AM Daily Ops Brief. Return only the brief.`
- 2:45 PM: `Use $ops-brief-policy to run the PM Daily Ops Brief. This is my morning brief. Return only the brief.`

Do not put policy or mutable state into either prompt. Do not create support, retry, or child schedules.

## Gmail labels

- `Receipts`
- `Receipts/Automotive`
- `Orders/Awaiting Shipment`
- `Orders/Shipped`
- `Ops/Archive Approval`

## Shipment reconciliation

1. Read `Shipments`.
2. Search new mail and every active order/tracking number across vendor, USPS, FedEx, UPS, and DHL evidence as applicable.
3. Read materially relevant threads in full.
4. Normalize evidence and run `policy/reconcile_shipments.py`.
5. Apply active-row updates and delivered-row deletions.
6. File routine order mail.
7. Re-read `Shipments`; render only the post-mutation active queue.

Evidence precedence is explicit user statement, carrier delivery, carrier exception/progress, then vendor status. Within a class, newer credible evidence wins. Age and ETA expiry are never proof of delivery.

## Email filing and approval

- Delivered orders: add receipt labels, remove active-order labels, archive correlated routine threads.
- Active orders: apply exactly one active-order label and archive routine confirmations/progress after state capture.
- Important decisions: apply `Ops/Archive Approval` and keep in Inbox.
- Every nonempty important-email section ends with `Is it OK to archive these emails?`
- No reply means leave the queue alone and repeat it next brief.
- Approval archives and unlabels only the approved current queue or named subset.
- Delete only email the user explicitly identifies for deletion.
- Do not monitor promotions, discounts, or sales.

## Cross-conversation capture

A clear request from any supported Chat, Work, project, voice, or dictation surface to add, update, complete, pause, or remove an item from the Daily Brief/Ops list is a write command to the canonical Ops Status Register. Never claim success if that write fails, and never leave the only copy in conversational memory.

## Project instructions

`project/INSTRUCTIONS.md.tmpl` is the complete, version-controlled ChatGPT Project bootstrap contract. Keep it thin: it invokes the skill and names authorities and hard boundaries; detailed policy remains in the skill, engines, and schemas.

Every lasting policy-source change requires an explicit instructions review and refreshed fingerprint. CI rejects stale fingerprints. When the contract changes, render and return the complete replacement block; never provide a partial patch. Temporary operational state never belongs in project instructions.

## Output order

Render only nonempty sections in this order: Weather, Route Weather, Shipments, Upcoming Appointments, Important Email, Ops Status, Miles & Pay, Important/Action Required, Trip Status.
