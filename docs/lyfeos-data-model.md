# LyfeOS 0.0.1 Data Model

LyfeOS 0.0.1 keeps one transaction identity while allowing many tags, assets, events, and cost allocations. Google Sheets is the current implementation; the keys and relationships are deliberately portable to PostgreSQL or another self-hosted database.

## Core entities

| Entity | Current tab | Primary key | Purpose |
|---|---|---|---|
| Transaction | `Orders - Database` | `Receipt ID` | One row and one counted total per underlying purchase |
| Transaction item | `Receipt Details - Expandable` | Receipt ID plus item/SKU/position | Searchable line items and fitment |
| Order event | `Order Events` | `Event ID` | Append-only lifecycle plus reciprocal related Receipt IDs and replacement group |
| Expense allocation | `Expense Ledger` | `Allocation ID` | Cost-owner split whose rows sum to the transaction total |
| Classification case | `Classification Queue` | `Queue ID` | Unknown product, category, vehicle, or owner awaiting user input |
| Active fulfillment | Ops `Shipments` | `Shipment ID` | Undelivered work queue only |
| Tool | Tool Inventory `Inventory` | `Tool ID` | Owned-tool inventory side effect |
| Integrity result | `Audit` | `Check ID` | Commit gate and explicit remediation |

## Invariants

1. A Receipt ID occurs exactly once in the transaction table.
2. Every transaction has at least one searchable detail row, a compact detail link, and canonical Drive evidence.
3. Tags and related assets are many-to-many metadata; they never duplicate spend.
4. Included expense allocations for one counted Receipt ID sum exactly to its current confirmed net transaction total; cancelled historical allocations remain linked but excluded.
5. Lifecycle events are appended idempotently; a new status does not erase the prior event.
6. The Ops shipment queue contains only `Awaiting Shipment`, `Shipped`, or `Exception`. Delivery is stored in Order Events and reported once.
7. Unknown classification is queued and omitted from verified allocation until the user resolves it.
8. A vehicle-specific receipt must have both correct data tags and a canonical file or link in that vehicle's receipt folder.
9. A true replacement has two Receipt IDs, reciprocal `Replaced By`/`Replacement For` events, and one shared Replacement Group ID; same-order revisions remain one Receipt ID.
10. Gmail is archived only after every required layer agrees and the Audit gate passes.

## Lifecycle financial semantics

- Requested cancellation: append an event, keep `Exception`, and preserve the current financial state until confirmation.
- Confirmed full cancellation before charge: retain the transaction/details, exclude all allocations from spend, and remove active fulfillment.
- Confirmed partial cancellation: retain the cancelled item as excluded history, update current totals only from merchant evidence, and keep only surviving fulfillment active.
- Return: preserve spend until refund evidence exists.
- Refund: preserve the gross transaction and append the exact refund as a linked negative adjustment or confirmed net-total revision; dashboards count the net effect once.
- Replacement: never transform the original into the new order. Link two transactions bidirectionally; preserve the original cancellation/refund financial state and balance the replacement independently. Until original cancellation is confirmed, keep the original fulfillment in `Exception` while tracking the replacement separately.

## Known vehicle mappings

| Product | Vehicle |
|---|---|
| 245/40ZR15 Hankook R-S4 | 2000 Mazda Miata NB |
| 265/35ZR18 Hankook R-S4 | 2015 Subaru WRX VA |
| 275/35ZR18 Hankook R-S4 | 2025 Honda Civic Type R FL5 |
| 205/45ZR16 General G-MAX AS-07 | 2000 Mazda Miata NB |
| Enkei GTC02 18x9.5 +45 and HR50 M14x1.50 lugs | FL5 |
| Konig Dekagram 15x10, Moss cover, Summit 100-7717 studs | Miata |
| Ignition coils, PCV/tune-up parts, SubaruOnlineParts 855251 | Subaru |
| Soft Socket | Garage Tools |

## Self-hosting path

The current Sheet columns map cleanly to relational tables named `transactions`, `transaction_items`, `order_events`, `expense_allocations`, `classification_cases`, `assets`, `transaction_assets`, and `evidence_objects`. A later migration should preserve the stable IDs, import events without rewriting history, and keep Drive/Gmail URLs as evidence references. Self-hosting changes storage and query power; it does not replace connector access or the integrity rules.
