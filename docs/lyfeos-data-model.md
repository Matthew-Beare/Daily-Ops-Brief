# LyfeOS Data Model

LyfeOS keeps stable transaction/asset/trip identities while allowing many evidence sources, tags, beneficiaries, events and allocations. Google Sheets is the current mutable implementation; keys and relationships are designed to migrate to PostgreSQL without rewriting history.

## Core entities

| Entity | Current authority/tab | Primary key | Purpose |
|---|---|---|---|
| Transaction | Purchase Archive `Orders - Database` | `Receipt ID` | One counted merchant transaction |
| Transaction item | `Receipt Details - Expandable` | Receipt ID + item/SKU/position | Searchable line items, category, fitment |
| Order event | `Order Events` | `Event ID` | Append-only lifecycle/revision/replacement history |
| Expense allocation | `Expense Ledger` | `Allocation ID` | Balanced cost-owner/asset/project allocation |
| Classification case | `Classification Queue` | `Queue ID` | Last-resort unresolved identity/ownership/fitment |
| Payment case | `Payment Reconciliation` | `Payment Case ID` | Expected charge vs pending/posted settlement |
| Person/external asset | `People & Assets` | `Entity ID` | Beneficiaries, aliases and external asset registry |
| Reimbursement | `Reimbursements` | `Reimbursement ID` | Expected/received payback separate from merchant refund |
| Active fulfillment | Ops `Shipments` | `Shipment ID` | Undelivered/exception work queue only |
| Calendar projection | Ops `Calendar Projection` | `Projection ID` | Source entity ↔ Google Calendar event dedupe/link |
| Route knowledge | Ops `Routes` | `Route ID` | Reusable terminal-pair geometry/runtime/paid-mile facts |
| Trip occurrence | Ops `Trips` | `Trip ID` | One real work leg / travel occurrence |
| Mileage occurrence | Mileage `Mileage Log` | `Mileage ID` | Auditable paid mileage/pay occurrence |
| Tool/owned asset | Tool/asset inventory | stable Asset/Tool ID | Physical owned-item identity and evidence links |
| Integrity result | `Audit` | `Check ID` | Commit gate/remediation |

## Purchase and asset invariants

1. A Receipt ID occurs once in the transaction table and its supported total is counted once.
2. A receipt may contain line items with different categories/assets/beneficiaries; included allocations reconcile exactly to the supported merchant total.
3. Email, photographed receipt, screenshot, account transaction and shipment evidence enrich the same transaction when they describe the same purchase.
4. A same-order merchant revision keeps one Receipt ID; a true new replacement order gets a separate Receipt ID and reciprocal relationship events.
5. Lifecycle events append idempotently; corrections supersede earlier interpretations without erasing them.
6. Product/asset identity may be enriched from model, serial, UPC/GTIN, SKU, part number, product photo, receipt and manufacturer evidence. One physical asset uses one stable Asset/Tool ID.
7. Unknown classification/fitment is queued only after reachable evidence and asset-registry exclusion checks are exhausted.
8. Reimbursement is not merchant refund. Gross merchant purchase remains auditable while verified reimbursements reduce net household cost separately.
9. Payment cases remain open until expected settlement is matched, split-matched, resolved as no-settlement or otherwise financially resolved. Actual posted amounts are compared with the latest supported same-order revision.
10. Gmail/archive success requires the applicable Audit gate to pass.

## Fulfillment and Gmail retention

`Shipments` contains only active `Awaiting Shipment`, `Shipped`, or `Exception` fulfillment. Delivered state is durable in `Order Events` and reported once.

Correlated merchant/carrier mail may be grouped by order-history labels. The narrow deployment retention rule may move only carrier-originated FedEx/UPS/DHL logistics messages to Trash after 90 days from durable delivery when tracking evidence is saved, Audit passes, and no claim/return/dispute/investigation requires the message. Merchant receipts/order/payment/support evidence is retained.

## Routes, trips and external run-sheet evidence

`Routes` is reusable knowledge; `Trips` and Mileage Log are occurrences. Employer/shared run sheets are evidence sources that reconcile into these tables using stable source/date/terminal/miles identifiers and must never create a parallel route database.

For the current deployment, company-paid terminal mileage is symmetric by terminal pair unless an explicit exception is supplied. Historical source variants remain provenance; reusable route values prefer explicit corrections, then current/repeated evidence rather than silently averaging conflicting entries.

## Calendar projection

Google Calendar is an optional projection surface, not authoritative state. `Calendar Projection` stores source type/source ID, target calendar, Google event ID, event class, source revision and sync status. A revised delivery ETA/appointment/deadline updates the existing linked event rather than creating a duplicate. Inviting attendees is a separate action boundary.

## Lifecycle financial semantics

- Cancellation request preserves existing financial state until confirmed.
- Full cancellation before settlement excludes spend without inventing a refund.
- Partial cancellation keeps removed lines as excluded history and updates surviving totals only from authoritative merchant revision evidence.
- Return preserves spend until refund evidence exists.
- Refund is linked financial evidence and nets exactly once; it does not erase gross history.
- Replacement financial state is resolved independently for original and replacement orders.

## Self-hosting path

A future relational implementation maps naturally to `transactions`, `transaction_items`, `order_events`, `expense_allocations`, `payment_cases`, `people`, `assets`, `transaction_assets`, `reimbursements`, `shipments`, `routes`, `trips`, `mileage_entries`, `calendar_projections`, `evidence_objects`, and `audit_results`. Stable IDs and append-only evidence/event history must survive migration. Drive/Gmail/provider URLs remain provenance references. Self-hosting changes storage/query/automation power; it does not weaken connector, approval or integrity rules.
