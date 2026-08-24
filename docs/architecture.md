# Architecture

The system separates mutable state, deterministic policy, evidence, scheduled dispatch, and versioned recovery material.

| Layer | Authority | Responsibility |
|---|---|---|
| Mutable Ops state | Ops Status Register | Tasks, controls, routes, trips, shipments, suppressions, run logs |
| Mileage state | Mileage & Pay Tracker | Company-paid miles, frozen rate, gross estimate, pay-week history |
| Purchase state | Purchase & Receipt Archive | Transactions, items, lifecycle events, expense allocations, classification queue, audit gate |
| Evidence | Gmail, Calendar, Drive | Complete threads, appointments, receipt attachments and archives |
| Policy | `skill/ops-brief-policy` | Routing, invariants, deterministic workflow, failure boundaries |
| Control-cycle dispatcher | One ChatGPT task | Reconcile receipts/orders, run the PM qualified-job watch, and emit briefs at 2:45 AM and 2:45 PM Eastern |
| Recovery | Private GitHub repository | Tests, templates, documentation, policy fingerprints |

The task carries no mutable database. The dispatcher chooses the slot and invokes the skill; receipt/order, qualified-job, and brief phases remain separate failure domains inside one scheduled run. Receipt work must pass the Audit gate before archiving source mail. No order, job, or calendar event receives its own automation.

See [LyfeOS 0.0.1 Data Model](lyfeos-data-model.md) for keys, relationships, and the self-hosting boundary.

The generic starter is separate from the current deployment. It may generate a new bootstrap contract, but it must not inherit the current user's identifiers or operational rows.
