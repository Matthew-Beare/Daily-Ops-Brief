# Household Financial Reconciliation Extension

This extends LyfeOS 0.0.1 without changing the one-transaction/one-Receipt-ID invariant.

## New canonical mutable tables

### People & Assets

Stores people/entities, aliases, relationship, household financial scope, and optional asset rows. It is the canonical mutable identity/asset layer for household members and outside beneficiaries. External assets are allowed and remain distinguishable from household-owned assets.

Suggested columns:

`Entity ID`, `Display Name`, `Entity Type`, `Relationship`, `Aliases`, `Financial Scope`, `Asset ID`, `Asset Type`, `Asset Label`, `Year`, `Make`, `Model`, `Notes`, `Updated ET`.

### Reimbursements

Stores expected/received money back from an outside beneficiary or other reimbursing party. This table is independent of merchant refund events.

Suggested columns:

`Reimbursement ID`, `Receipt ID`, `Beneficiary / Cost Owner`, `Related Asset(s)`, `Purchase Amount Allocated`, `Amount Expected Back`, `Amount Received`, `Status`, `Payment Evidence / Account Ref`, `Expected / Received Date`, `Net Household Cost`, `Source`, `Notes`, `Updated ET`.

### Payment Reconciliation

Tracks the merchant charge expected from the latest authoritative order/revision evidence until settlement is matched.

Suggested columns:

`Payment Case ID`, `Receipt ID`, `Vendor`, `Order Number`, `Expected Charge`, `Expected Evidence`, `Card Last Four / Account Hint`, `Status`, `Observed Posted Amount`, `Observed Pending Amount`, `Difference`, `First Expected ET`, `Last Checked ET`, `Resolved ET`, `Source`, `Notes`.

## Relationships

- `Orders - Database.Receipt ID` -> one merchant transaction.
- `Expense Ledger.Receipt ID` -> one or more cost allocations whose included rows reconcile to the merchant transaction total.
- `Reimbursements.Receipt ID` -> zero or more non-merchant paybacks reducing net household cost without mutating gross merchant spend.
- `Payment Reconciliation.Receipt ID` -> one or more settlement cases when a merchant legitimately settles separately; normally one case per current merchant order financial outcome.
- `People & Assets` supplies stable beneficiary/asset identities referenced by allocations/reimbursements.

## Financial views

Expose separate measures instead of collapsing unlike concepts:

- Gross Merchant Spend: supported vendor purchases after merchant cancellations/refunds are applied exactly once.
- Reimbursements Received: verified money returned by outside beneficiaries, not merchant refunds.
- Net Household Cost: Gross Merchant Spend attributable to the household minus verified outside reimbursements.
- Expected Unsettled Charges: supported merchant totals still awaiting account settlement.
- Merchant Charge Variance: posted charge minus latest supported expected merchant charge.
- Unmatched Account Charges: material account debits not yet linked to a supported Receipt ID/payment case.

## PostgreSQL path

Future relational tables map naturally to:

- `parties`
- `party_aliases`
- `assets`
- `asset_owners`
- `transactions`
- `transaction_items`
- `expense_allocations`
- `reimbursement_obligations`
- `reimbursement_events`
- `payment_cases`
- `payment_observations`
- `order_events`
- `evidence_objects`

Use stable IDs and append-only events. The migration must not reinterpret an outside-person reimbursement as revenue or a merchant refund.
