# Control cycle and briefs

The user chooses cadence, local slots, IANA timezone, notification mode, sections, and anti-noise rules during onboarding. Do not inherit another deployment's schedule.

## Scheduled entry

1. Capture the runtime's current offset-aware instant.
2. Convert it through the deployment's canonical IANA timezone.
3. Match it against the configured local slot and bounded provider grace window.
4. Derive one deterministic Run ID from deployment UUID, canonical date, and slot.
5. Upsert the Run Log as `Running` before downstream provider mutations.
6. Run enabled modules independently from current canonical state and connected evidence.
7. Update the same Run Log row to `Complete`, `Degraded`, or `Blocked`, with module evidence.
8. Return only the current run's brief. Never reuse an earlier chat response.

## Normal module order

1. Current context, tasks, routines, projects, and appointments.
2. Receipt/order/shipment/payment reconciliation when enabled.
3. Calendar reminder reconciliation when enabled.
4. Qualified-job monitoring when enabled.
5. Weather, travel, mileage/pay, meal planning, and other selected sections.
6. Compact next actions and exact blocked dependencies.

Each module declares its own authority and optional adapters. Continue healthy modules when another failure domain is unavailable.
