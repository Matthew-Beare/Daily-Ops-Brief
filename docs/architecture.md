# Architecture

The system separates mutable state, deterministic policy, evidence, scheduled dispatch, and versioned recovery material.

| Layer | Authority | Responsibility |
|---|---|---|
| Mutable Ops state | Ops Status Register | Tasks, controls, routes, trips, shipments, suppressions, run logs |
| Mileage state | Mileage & Pay Tracker | Company-paid miles, frozen rate, gross estimate, pay-week history |
| Evidence | Gmail, Calendar, Drive | Complete threads, appointments, receipt attachments and archives |
| Policy | `skill/ops-brief-policy` | Routing, invariants, deterministic workflow, failure boundaries |
| Dispatcher | One ChatGPT task | Invoke the skill at 2:45 AM and 2:45 PM Eastern |
| Recovery | Private GitHub repository | Tests, templates, documentation, policy fingerprints |

The dispatcher never carries the mutable database. It chooses the slot and invokes the skill. The skill reads live authorities and calls the deterministic engine. Scheduled runs do not maintain their own automation.

The generic starter is separate from the current deployment. It may generate a new bootstrap contract, but it must not inherit the current user's identifiers or operational rows.
