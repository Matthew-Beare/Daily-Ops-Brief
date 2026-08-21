# Email and Shipment Reconciliation

Load this reference completely for order mail, active shipments, inbox filing, archive approval, explicit email deletion, and the Gmail pass of every brief.

## Authoritative state

- `Shipments!A1:N500` in the Ops Status Register is the active shipment queue, not a purchase ledger.
- Its exact columns are `Shipment ID`, `Vendor`, `Order Number`, `Item`, `Carrier`, `Tracking Number`, `Package Count`, `Order Date`, `Shipped Date`, `ETA (ET)`, `Status`, `Last Progress (ET)`, `Notes`, and `Updated (ET)`.
- Allowed active statuses are `Awaiting Shipment`, `Shipped`, and `Exception`.
- Keep one row per fulfillment or tracking number. Split packages may create multiple rows for one order.
- Gmail labels and archived threads are the order/receipt history. Never copy message bodies, Gmail IDs, account numbers, addresses, or live Sheet rows into Git.

## Read and match evidence

1. Read the active queue before searching Gmail.
2. Search new material since the last completed brief, or 24 hours when no completed run exists.
3. Search each active row by exact tracking number and exact order number. Inspect USPS, FedEx, UPS, DHL, and vendor mail as applicable.
4. Read every materially relevant thread in full. A subject or snippet can select a thread, but cannot establish final state.
5. Normalize one evidence event per fulfillment. Include source, event, vendor, order number, item, carrier, tracking number, package count, event time, observed time, ETA, and concise notes when available.
6. Match in this order:
   - exact tracking number;
   - exact vendor plus order number when unique;
   - exact order number plus item/package facts when unique;
   - vendor plus item, order date, recipient, and package facts only when the combination is unique.
7. If more than one active row remains plausible, do not guess. Keep the rows and surface a concise unresolved exception.

## Evidence precedence

Use the strongest evidence, not the newest email blindly:

1. Explicit user statement.
2. Carrier delivery event.
3. Carrier exception or progress event.
4. Vendor delivery or status event.

Within the same class, the newer credible event wins. A stale vendor `Shipped` message cannot resurrect a carrier-confirmed or user-confirmed delivery. Never infer delivery from elapsed time, ETA expiry, an invoice, or shipment age.

## Transaction order

1. Build normalized evidence from complete threads and any explicit user statement.
2. Run `python3 scripts/reconcile_shipments.py reconcile --input <json-file> --pretty`.
3. Apply active-row creates/updates using stable `SHIP-###` IDs.
4. Delete each row returned as delivered from the active `Shipments` queue. Do not move it to another Sheet or render it as delivery history.
5. File the correlated Gmail messages according to the rules below.
6. Re-read `Shipments!A1:N500`. Render only this post-mutation active state.
7. Record only stable shipment/task IDs and concise counts in the Run Log. Never log Gmail message/thread IDs or message bodies.

Any required Sheet or Gmail mutation failure makes the brief run `Error`; report the failed operation once and do not claim reconciliation completed.

## Gmail filing

Use these labels when available, creating only `Ops/Archive Approval` if missing:

- `Receipts`
- `Receipts/Automotive`
- `Orders/Awaiting Shipment`
- `Orders/Shipped`
- `Ops/Archive Approval`

For a delivered order:

- add `Receipts` and, when automotive, `Receipts/Automotive` to the original order, invoice, shipment, and delivery messages;
- remove `Orders/Awaiting Shipment` and `Orders/Shipped`;
- archive the routine correlated threads after the Sheet row is deleted.

For an active order:

- use `Orders/Awaiting Shipment` before credible shipment evidence and `Orders/Shipped` after it;
- remove the opposite active-order label;
- archive routine confirmations and carrier progress messages after the Sheet state is updated. The active row, not Inbox residence, drives the brief.

For important or decision-bearing email:

- add `Ops/Archive Approval` and keep the thread in Inbox;
- group related messages into one concise brief item;
- end the `IMPORTANT EMAIL` section with exactly `Is it OK to archive these emails?`;
- if the user does not answer, leave the queue untouched and prompt again on the next brief;
- when the user approves all queued mail, archive the threads currently carrying `Ops/Archive Approval` in Inbox, then remove that label;
- when approval names only a subset, archive and unlabel only that subset.

Routine noise may be archived after it is processed. Never delete email merely to clean Inbox. Delete only a specific message/thread or bounded set the user explicitly orders deleted, and report the completed scope.

## Excluded scope

- Do not search Promotions for discounts or sales.
- Do not calculate discount percentages or add sale alerts to a brief.
- Do not reinstate promotion monitoring unless the user explicitly requests it later.
