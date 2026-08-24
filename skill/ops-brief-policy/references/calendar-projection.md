# Calendar Projection

Load this reference when canonical LifeOS state should create/update Google Calendar events or when first boot configures which event classes are projected.

## Principle

Calendar is a synchronized projection of canonical LifeOS state, not the primary database. Every projected event must have a row in `Calendar Projection` linking the source entity to the Google Calendar event ID so revisions update/cancel the existing event instead of creating duplicates.

## First-boot choices

Offer each event class independently and default to off unless the user chooses it:

- appointments and reservations;
- order delivery dates/windows;
- work trips/departures/arrival commitments;
- subscription/trial renewal or cancellation deadlines;
- bills/payment due dates;
- school/work deadlines;
- maintenance/warranty deadlines;
- selected high-priority tasks;
- user-defined event classes.

Ask which target calendar should receive each enabled class, whether tentative dates should be shown, and whether updated ETAs should move the event automatically. Do not imply that enabling one class enables all others.

## Event identity and updates

Use a stable Projection ID based on source type + source ID + event class. Store source type, source ID, target calendar, Google event ID, title, start/end, source-updated timestamp, projection status and sync timestamp.

- Source revision: update the linked event in place.
- Cancelled source: cancel/delete the linked event according to the user's configured projection policy, while retaining the projection audit row.
- Delivered/completed source: mark/update event according to selected behavior; do not create a second completion event.
- Missing Google event: recreate only after verifying the canonical projection row and avoiding a duplicate by source identity/time/title.

## Delivery projections

If order deliveries are enabled, use carrier/vendor evidence only after shipment correlation. Prefer credible carrier ETA/window; update the same event when ETA changes. A delivery event does not replace the active `Shipments` queue or `Order Events`. Multiple packages may be one order-level event or package-level events according to user preference; default to one order-level event to limit clutter.

## Appointments

Appointments parsed from verified email/Docs/user input may be projected only when date/time/location identity is sufficiently supported. Preserve source provenance and never silently invent confirmation state.

## Safety

Creating/updating normal user-selected calendar projections is authorized by the configured projection policy after first-boot approval. Inviting other people, adding external attendees, or sending invitation updates is a separate consequential action and requires explicit authority unless the user deliberately configured that behavior.

Never create a separate automation per event. The consolidated lifecycle/brief pipelines maintain projections.
