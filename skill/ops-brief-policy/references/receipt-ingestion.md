# Receipt Ingestion and Inventory Side Effects

Load this reference completely before ingesting purchase receipts, filing receipt evidence in Drive, updating the receipt index, producing a receipt-based spending rollup, or applying an inventory side effect.

## Authorities

- Gmail is the evidence source. Read the complete relevant message or thread and its receipt attachment; snippets and shipping-only messages are not receipts.
- The Drive archive is `LyfeOS/02 Receipts & Purchases/Receipt Archive` with `00 Index & Database`, `01 Receipt Backups`, and `02 Receipts by Category`.
- `Purchase & Receipt Archive` (ID `1pHkTdCxmdBdZjnVu97FkpkiSjysLkhjuTEcfcEXzmW8`) is the canonical LyfeOS 0.0.1 purchase system. Preserve its identity, validation, formulas, formatting, stable Receipt IDs, and foreign-key relationships.
- `Orders - Database` stores one row per underlying transaction; `Receipt Details - Expandable` stores searchable line items; `Order Events` stores append-only lifecycle transitions; `Expense Ledger` stores cost allocations; `Classification Queue` stores unresolved user choices; `Financial Dashboard` is a derived email/receipt-detected view.
- `Legacy - Purchase Receipts Full Text Archive - Search Backup` is backup text only. Never use it as the user-facing receipt view.
- Tool Inventory spreadsheet ID: `1fwbt7lDejGJmf_EeY9U1uuwQ8TxXulcnvaKnc_1mNTM`. A tool receipt may update this inventory only after the base receipt record is safely stored.

## Evidence and classification

- Include purchase receipts, paid invoices, and order confirmations with evidence of a transaction. Exclude shipping-only, delivery-only, marketing, quotation, cart, and abandoned-checkout messages unless another message in the same thread supplies the receipt.
- Extract only evidence-backed vendor, order or invoice number, purchase date, item description, quantity, subtotal, tax, shipping, discounts, total, payment suffix when present, and source-message identifiers.
- Deduplicate using the strongest available combination of vendor, order or invoice number, transaction date, amount, item identity, Gmail message/thread ID, and attachment identity. Enrich the existing record when it is the same transaction.
- Search direct merchant/carrier mail and messages forwarded by `jbeare92@gmail.com`. For forwarded Amazon evidence, parse the embedded Amazon sender, order number, items, amount, status, and tracking facts from the complete forwarded body; the outer sender does not invalidate the evidence.
- An explicit user correction outranks stale email. Preserve both in `Order Events` and annotate the correction source instead of erasing the earlier evidence.
- File into the narrowest supported category under `02 Receipts by Category`: Automotive, Bills & Utilities, Education, Electronics & Computer, Food & Dining, Health, House, Subscriptions & Services, Tools, Travel, or General. Do not invent a category from weak semantics.
- A transaction may have multiple non-exclusive categories, search tags, and related assets. Count it once by Receipt ID. Expense allocations may split the total across cost owners, but their sum must equal the single order total.
- Automotive canonical folders are `2015 Subaru WRX VA`, `2025 Honda Civic Type R FL5`, `2000 Mazda Miata NB`, and `2004 Chevrolet Silverado`. Multi-vehicle orders use `Multi-Vehicle Orders` plus link/reference cards. Tool receipts use `Tools/Garage Tools & Mechanics`; a tool may reference a vehicle without becoming a vehicle part.
- If classification, vehicle, cost owner, or product identity is materially ambiguous, do not guess. Add one unresolved `Classification Queue` row, apply `Shopping/Needs Classification`, exclude it from verified allocations, and let the next brief ask the smallest useful question.

## Commit order

Use this order so Gmail is never cleared before downstream state exists:

1. Read and classify the complete receipt evidence.
2. Check the canonical index and destination folder for duplicates.
3. Save the original receipt attachment when one exists. For email-only evidence, create or update one concise, mobile-readable receipt record with a brief summary and expandable full details.
4. Upsert one `Orders - Database` row and the searchable line items. Point the Receipt Browser's `Show details` link at that receipt's expandable range, never the legacy Doc.
5. Append each new Ordered/Awaiting Shipment, Shipped, Delivered, Exception, Cancelled, Returned, or Refunded transition to `Order Events`. Idempotency is event ID plus Receipt ID, event type, event time, tracking/package, and source.
6. Upsert `Expense Ledger` allocations and verify that allocations for one Receipt ID sum to the one counted transaction total. Do not invent fuel or other unsupported spending.
7. Synchronize the active Ops `Shipments` queue: Awaiting Shipment and Shipped remain active; Exception remains actionable; Delivered is removed after the event is durably recorded.
8. Apply supported inventory side effects. For a tool, deduplicate and create or enrich the Tool Inventory row using only evidence-backed attributes. Never guess brand, model, power source, platform, ownership, condition, or classification.
9. Rebuild or refresh the `Audit` integrity gate. Require PASS for one order row per Receipt ID, at least one detail row, compact detail link, canonical Drive archive link, verified-or-queued classification, exact expense-allocation sum, known vehicle mappings, vehicle-specific Drive placement/link, and active Orders-to-Shipments synchronization.
10. Verify Drive evidence, database rows, lifecycle event, expense allocations, shipment mutation, classification state, inventory side effects, and the Audit gate as one transaction.
11. Only after every required check passes, apply Gmail labels and archive routine threads. Never delete Gmail unless the user explicitly names the bounded messages to delete.

If a downstream write fails, leave the Gmail message unarchived and report the exact incomplete stage. Do not claim the receipt was processed merely because a Drive copy exists.
If any Audit check fails, write the Receipt ID and remediation, leave affected Gmail threads unarchived, and surface one compact `Action Required` summary. A correct Sheet tag with a missing vehicle-folder record is still a failure.

## Monthly receipt rollups

- A monthly rollup is an email-detected spending report, not a complete financial ledger or bank statement.
- Deduplicate confirmation, shipment, delivery, and attachment variants of the same purchase.
- Preserve the shared-Amazon rule: exclude only items strongly evidenced as another household member's purchase. Put ambiguous ownership or classification in `Classification Queue` instead of silently including, excluding, or guessing.
- Show the covered month, evidence boundary, category totals, monthly total, and any unresolved ambiguous transactions.

## Safety

- Do not expose or reproduce full payment-card numbers, account credentials, access tokens, or unrelated private message content.
- Do not overwrite an original attachment. Preserve originals and make corrections in the index or a clearly versioned native record.
- Keep receipt history separate from the active shipment queue. Durable lifecycle history belongs in `Order Events`; delivered shipments must not remain in active `Shipments`.
- Do not create one automation, calendar event, reminder, or permanent task per order. One lifecycle pipeline maintains all purchases; the existing Ops Brief dispatcher reports active and newly delivered state.
