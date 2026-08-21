# Receipt Pipeline

Receipt ingestion and lifecycle reconciliation are one transaction:

1. Read the complete Gmail evidence and classify the transaction.
2. Deduplicate against the canonical receipt index and Drive destination.
3. Save or update one canonical, mobile-readable receipt with a compact summary and expandable details.
4. Upsert one transaction row and searchable line items under a stable Receipt ID.
5. Append the lifecycle event instead of overwriting history.
6. Allocate the single transaction total across cost owners without double counting.
7. Synchronize the active shipment queue, Gmail labels, Drive vehicle/tool links, and supported Tool Inventory side effects.
8. Queue unknown classifications for the next brief instead of guessing.
9. Rebuild the Audit gate and require every applicable check to pass.
10. Only then archive routine Gmail source threads.

If a downstream step fails, the source email remains unarchived and the exact Receipt ID/remediation is written to Audit. Shipping and delivery messages enrich the transaction's Order Events; they do not create duplicate receipts.

Cancellation is a lifecycle transition, not deletion. A request remains `Exception` with unchanged financials until confirmation. A confirmed full cancellation leaves the receipt searchable, excludes its financial rows from spend, and removes its active fulfillment. A confirmed partial cancellation retains the cancelled line as excluded history, applies only merchant-confirmed revised totals to the surviving allocation, and rewrites `Shipments` to the surviving item. Returns do not reduce spend until exact refund evidence exists; refunds are linked negative adjustments or confirmed revised net totals and are counted once.

The monthly spending report is bounded to email-detected purchases. It is not represented as a complete bank, card, or household ledger.

The user-facing front end is the Receipt Browser plus expandable detail ranges, not the legacy full-text Doc. Search tags remain visible and searchable while the long line-item body stays minimized.
