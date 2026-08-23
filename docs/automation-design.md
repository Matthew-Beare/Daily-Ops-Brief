# Automation Design

One recurring Ops task dispatches both daily briefs:

```text
BEGIN:VEVENT
DTSTART;TZID=America/New_York:<next local 02:45 or 14:45>
RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0
END:VEVENT
```

The dispatcher determines AM before local noon and PM at or after local noon. This retains two brief deliveries while consuming one active task slot.

Scheduler verification is an evidence chain. After create/update, verify title, enabled state, recurrence/local time/TZID, timing mode, required notification state, and duplicate count. A field merely named `default_timezone` is not authoritative unless the provider contract explicitly defines it as persistent task execution state. Do not clear a scheduler incident until a subsequent actual firing or canonical Run Log entry lands in the intended New York slot.

## Legacy-pair migration

1. Snapshot both active legacy jobs, including notification state and last-run metadata.
2. Verify the Ops Sheets, Gmail, Calendar and scheduler dependencies with harmless reads.
3. Update one healthy notification-capable legacy job in place to the combined title, prompt and schedule.
4. Re-inspect and verify that job's schedule, timing mode and notification state.
5. Pause the other active legacy job only after the surviving dispatcher is verified.
6. Re-inspect and verify exactly one active canonical Ops Brief job.
7. Require the next actual canonical firing before declaring a prior scheduler incident cleared.
8. Restore the snapshot if a deterministic mutation/readback fails and rollback can be proven.

Updating in place avoids needing a temporary extra task when the account is already at its active-task limit and avoids accidentally replacing a notification-capable dispatcher with a silent one.

## Receipt and order lifecycle

One additional recurring task handles every purchase:

```text
BEGIN:VEVENT
DTSTART;TZID=America/New_York:<next local 01:45 or 13:45>
RRULE:FREQ=DAILY;BYHOUR=1,13;BYMINUTE=45;BYSECOND=0
END:VEVENT
```

Set `timing_mode=exact_schedule`. The lifecycle run is intentionally one hour before the corresponding brief; allowing it to drift into the brief window creates a race between reconciliation and reporting.

It scans direct merchant/carrier mail and authorized forwarded evidence, updates the normalized receipt tables, synchronizes active Ops shipments and Gmail labels, refreshes Drive filing and inventory side effects, and rebuilds the Audit gate. It never creates per-order scheduled tasks, reminders, retry jobs, or child automations.

If the deployment opted into Calendar Projection for order deliveries, the lifecycle may create or update the one source-linked Google Calendar event through the canonical `Calendar Projection` dedupe table. That is a calendar projection, not a per-order automation, and ETA revisions update the existing event rather than creating another one.

The lifecycle task commits only when Gmail, Drive, Orders, Details, Order Events, Expense Ledger, Classification Queue, Audit, and any required Shipment/Tool Inventory/shopping side effect agree. A failed check leaves the source thread unarchived and produces one actionable failure.