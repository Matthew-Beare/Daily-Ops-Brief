# Automation Design

One recurring task can dispatch both exact daily runs:

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
