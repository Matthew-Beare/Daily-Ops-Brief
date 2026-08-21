# Automation Design

One recurring Ops task dispatches both daily briefs:

```text
BEGIN:VEVENT
DTSTART;TZID=America/New_York:<next local 02:45 or 14:45>
RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0
END:VEVENT
```

The dispatcher determines AM before local noon and PM at or after local noon. This retains two brief deliveries while consuming one active task slot.

## Legacy-pair migration

1. Snapshot both active legacy jobs.
2. Verify the Ops Sheets, Gmail, and Calendar dependencies with harmless reads.
3. Update one healthy legacy job in place to the combined title, prompt, schedule, and timezone.
4. Re-inspect and verify that job.
5. Pause the other active legacy job.
6. Re-inspect and verify exactly one active canonical Ops Brief job.
7. Restore the snapshot if any mutation or verification fails.

Updating in place avoids needing a temporary sixth task when the account is already at its active-task limit.

## Receipt and order lifecycle

One additional recurring task handles every purchase:

```text
BEGIN:VEVENT
DTSTART;TZID=America/New_York:<next local 01:45 or 13:45>
RRULE:FREQ=DAILY;BYHOUR=1,13;BYMINUTE=45
END:VEVENT
```

It scans direct merchant/carrier mail and forwarded Amazon evidence from `jbeare92@gmail.com`, updates the normalized receipt tables, synchronizes active Ops shipments and Gmail labels, refreshes Drive filing and inventory side effects, and rebuilds the Audit gate. It never creates per-order tasks, reminders, or calendar events.

The lifecycle task commits only when Gmail, Drive, Orders, Details, Order Events, Expense Ledger, Classification Queue, Audit, and any required Shipment/Tool Inventory side effect agree. A failed check leaves the source thread unarchived and produces one actionable failure.
