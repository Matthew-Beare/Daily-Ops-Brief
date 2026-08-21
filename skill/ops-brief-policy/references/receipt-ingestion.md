# Receipt Ingestion and Inventory Side Effects

Load this reference completely before ingesting purchase receipts, filing receipt evidence in Drive, updating the receipt index, producing a receipt-based spending rollup, or applying an inventory side effect.

## Authorities

- Gmail is the evidence source. Read the complete relevant message or thread and its receipt attachment; snippets and shipping-only messages are not receipts.
- The Drive archive is `LyfeOS/02 Receipts & Purchases/Receipt Archive` with `00 Index & Database`, `01 Receipt Backups`, and `02 Receipts by Category`.
- `Purchase & Receipt Archive` is the canonical receipt index. Preserve its identity, schema, validation, formulas, formatting, and stable IDs.
- `2026 Purchase Receipts - Full Text Archive` is supporting searchable text, not a second receipt index.
- Tool Inventory spreadsheet ID: `1fwbt7lDejGJmf_EeY9U1uuwQ8TxXulcnvaKnc_1mNTM`. A tool receipt may update this inventory only after the base receipt record is safely stored.

## Evidence and classification

- Include purchase receipts, paid invoices, and order confirmations with evidence of a transaction. Exclude shipping-only, delivery-only, marketing, quotation, cart, and abandoned-checkout messages unless another message in the same thread supplies the receipt.
- Extract only evidence-backed vendor, order or invoice number, purchase date, item description, quantity, subtotal, tax, shipping, discounts, total, payment suffix when present, and source-message identifiers.
- Deduplicate using the strongest available combination of vendor, order or invoice number, transaction date, amount, item identity, Gmail message/thread ID, and attachment identity. Enrich the existing record when it is the same transaction.
- File into the narrowest supported category under `02 Receipts by Category`: Automotive, Bills & Utilities, Education, Electronics & Computer, Food & Dining, Health, House, Subscriptions & Services, Tools, Travel, or General. Do not invent a category from weak semantics.

## Commit order

Use this order so Gmail is never cleared before downstream state exists:

1. Read and classify the complete receipt evidence.
2. Check the canonical index and destination folder for duplicates.
3. Save the original receipt attachment when one exists. For an email-only receipt, create a Drive-native record containing the complete useful receipt content and source metadata.
4. Create or update the canonical receipt-index row and attach the Drive evidence link.
5. Apply supported side effects. For a tool, deduplicate and then create or enrich the Tool Inventory row using only evidence-backed attributes. Never guess brand, model, power source, platform, ownership, or classification.
6. Verify the Drive evidence, receipt-index row, and every required side effect.
7. Only after verification, apply the requested Gmail label/archive action. Never delete Gmail unless the user explicitly names the bounded messages to delete.

If a downstream write fails, leave the Gmail message unarchived and report the exact incomplete stage. Do not claim the receipt was processed merely because a Drive copy exists.

## Monthly receipt rollups

- A monthly rollup is an email-detected spending report, not a complete financial ledger or bank statement.
- Deduplicate confirmation, shipment, delivery, and attachment variants of the same purchase.
- Preserve the user's shared-Amazon rule: exclude only items strongly evidenced as another household member's clearly gendered beauty purchase; include ambiguous household items instead of silently dropping them.
- Show the covered month, evidence boundary, category totals, monthly total, and any unresolved ambiguous transactions.

## Safety

- Do not expose or reproduce full payment-card numbers, account credentials, access tokens, or unrelated private message content.
- Do not overwrite an original attachment. Preserve originals and make corrections in the index or a clearly versioned native record.
- Keep receipt processing separate from the active shipment queue. A receipt can close a purchase record, but delivery history belongs in Gmail and delivered shipments must not remain in the active `Shipments` queue.
