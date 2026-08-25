# Household Financial Reconciliation Extension

This extends M.I.R.R.O.R. without changing the one-transaction/one-Receipt-ID invariant and explicitly prevents account-settlement activity from being counted as spending twice.

## Economic event rule

A merchant purchase and the later movement of money used to settle that purchase are different events.

- A card purchase may count as merchant spend once when supported by transaction/receipt evidence.
- A checking-account payment to that credit card is a transfer/liability settlement, **not a second purchase**.
- A credit-card payment observed on both sides of the transfer remains one settlement relationship, not two expenses.
- Merchant refunds reduce merchant spend according to refund semantics and are not income.
- Reimbursements from another person/organization are separate from merchant refunds.
- Transfers between owned accounts do not become income or spending merely because they appear as debit/credit transaction rows.
- Loan/debt principal payments, interest/fees, payroll/income, cash withdrawals, and merchant purchases retain distinct event classes.

A financial adapter must preserve account identity, provider transaction identity, pending/posted status, transfer/linkage evidence when available, amount/sign semantics, and reconciliation confidence. Ambiguous rows remain unresolved and visible rather than being silently discarded or counted twice.

## Canonical mutable tables/entities

### People & Assets

Stores people/entities, aliases, relationship, household financial scope, and optional asset rows. Every person and physical asset uses one immutable RFC 4122 `Entity UUID` as canonical cross-database identity. Friendly IDs, display names and aliases are human-facing attributes and never replace or recycle the UUID.

### Reimbursements

Stores expected/received money back from an outside beneficiary or other reimbursing party. This remains independent of merchant refund events.

Suggested fields include `Reimbursement ID`, `Receipt ID`, `Beneficiary Entity UUID`, allocated purchase amount, amount expected, amount received, status, payment evidence/account reference, dates, net household cost, provenance and audit timestamps.

### Payment Reconciliation

Tracks the merchant charge expected from the latest authoritative order/revision evidence until settlement is matched.

Suggested fields include `Payment Case ID`, `Receipt ID`, vendor/order identity, expected charge, evidence, account hint, status, observed posted/pending amount, difference, timestamps, source and notes.

### Account Transactions

A future SQL-backed implementation should persist source account transactions separately from normalized economic events. Suggested fields include:

`Account Transaction UUID`, provider transaction ID, Account UUID, posted/pending status, observed amount, currency, merchant/description, provider category, transaction timestamp, transfer linkage/reference, raw evidence reference, normalization status, normalized event UUID, confidence and timestamps.

The normalized event may be a merchant purchase, transfer, liability settlement, fee/interest, refund, reimbursement, income, cash movement, or unresolved class. Source rows are never destroyed merely because normalization changes.

## Reconciliation relationships

- `Receipt ID` represents one merchant transaction/purchase outcome.
- Expense allocations reconcile to that supported merchant total.
- Reimbursements link to the Receipt ID but reduce net household cost separately.
- Payment cases reconcile the expected merchant amount with actual account settlement evidence.
- Source account transaction rows link to normalized economic events without becoming the economic event themselves.
- Transfer pairs/linkages may bind two account transaction rows to one transfer/settlement event.
- Assets/beneficiaries use immutable UUIDs.

## Financial views

Expose separate measures instead of collapsing unlike concepts:

- **Gross Merchant Spend** — supported purchases, with merchant cancellations/refunds applied exactly once.
- **Net Household Cost** — household-attributable merchant spend minus verified outside reimbursements.
- **Account Cash Flow** — actual cash movement by account without pretending transfers are spending/income.
- **Debt/Liability Settlement** — principal/card payments separately from merchant spend; interest and fees remain their own expense classes.
- **Expected Unsettled Charges** — supported merchant totals still awaiting settlement.
- **Merchant Charge Variance** — posted merchant charge minus latest supported expected charge.
- **Unmatched Account Activity** — account rows not yet safely linked/classified.

## Deduplication keys

Use the strongest available provider identity first. Fallback correlation may consider account UUID, amount, timestamp window, merchant, source evidence, receipt/order number and transfer linkage. A fuzzy match is never promoted to a hard duplicate without sufficient confidence/evidence.

One source transaction may enrich an existing Receipt ID/payment case. It must not create a second Receipt ID merely because both receipt/email evidence and card-account evidence exist.

## PostgreSQL path

Future relational tables map naturally to `parties`, `party_aliases`, `assets`, `transactions`, `transaction_items`, `expense_allocations`, `reimbursement_obligations`, `reimbursement_events`, `payment_cases`, `account_transactions`, `normalized_financial_events`, `transfer_links`, `payment_observations`, `order_events`, and `evidence_objects`.

Use immutable UUIDs, unique provider-source identities, append-only events, database constraints and service-layer idempotency. Migration preserves existing canonical IDs and never reinterprets a reimbursement as revenue, a merchant refund as generic income, or a credit-card payment as a second purchase.
