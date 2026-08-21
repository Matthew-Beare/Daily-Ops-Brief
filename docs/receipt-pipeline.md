# Receipt Pipeline

Receipt ingestion is transactional:

1. Read the complete Gmail evidence and classify the transaction.
2. Deduplicate against the canonical receipt index and Drive destination.
3. Save the original attachment or a complete Drive-native email receipt record.
4. Create or update the canonical receipt-index row with its evidence link.
5. Apply supported side effects, such as a deduplicated Tool Inventory upsert.
6. Verify every downstream write.
7. Only then archive or label the Gmail source as requested.

If a downstream step fails, the source email remains unarchived and the exact incomplete stage is reported. Shipping and delivery messages do not become receipt records merely because they reference an order.

The monthly spending report is bounded to email-detected purchases. It is not represented as a complete bank, card, or household ledger.
