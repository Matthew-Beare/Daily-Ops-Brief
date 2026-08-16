# Ops State and Automation Maintenance

Load this reference completely before changing task, control, mode, mileage, automation, or other persistent Ops state. Preserve Sheet identity, headers, validation, row formatting, and history.

## Global capture from any conversation

- Treat any clear request to add, update, complete, pause, or remove something from the `Daily Brief`, `Ops Brief`, `Ops list`, or equivalent named project as a command to update the canonical Ops Status Register immediately. This applies from any Chat, Work, project, supported voice, or dictation surface.
- Do not leave an Ops change only in chat memory, a project-local note, a prompt, or a second database. The live Sheet is the acknowledgement boundary.
- For normal task additions, ask only for a missing required Tier or Classification. For Persistent additions, ask only for a missing Classification. Apply unambiguous updates and completions without reconfirming.
- If the connected Sheet cannot be reached or written from the current surface, say that the change was not persisted. Never claim success based on conversational memory.
- Keep unrelated reminders outside this system unless the user explicitly names the Daily Brief/Ops destination.

## Tasks

- Apply additions, completions, removals, pauses, renames, tier/classification changes, scheduling, and visibility directly to the existing Ops Status Register.
- Mark completion `Done` and removal `Removed`; never delete rows or infer completion from silence.
- A normal task requires Tier `High`, `Medium`, or `Low`, plus Classification.
- A `Persistent` task requires Classification and no priority.
- Ask only for a missing required field; never guess Classification.

## Mode overrides

Use only Control type `Mode Override`; Vacation and Home early are `Item` values, not separate engines.

- For an unambiguous “got home early” statement, run `python3 scripts/ops_policy.py home-early --now <current-Eastern-ISO> --pretty`, then add or update the `Home early` row from `sheet_fields`. Reuse the active row or allocate the next stable `CTRL-###`. Do not ask for priority/classification.
- For vacation or another temporary HOME interval, create a HOME Mode Override with an explicit Eastern start and exclusive expiry. Ask only when a required boundary is materially ambiguous.
- Never manually clear an expired override; the engine ignores it.

## Mileage and pay

- Log only company-paid miles stated by the user or shown by credible company/settlement evidence. Never substitute map, odometer, route, or estimated distance.
- Use a stable `MILE-###` row with Thursday week ending, Trip ID, route, departure/arrival, endpoints, company-paid miles, miles source, status, notes, and update timestamp.
- For a new actual entry, replace that row's rate formula with the current numeric `Rate per mile` value so historical pay remains frozen when the default changes.
- Gross estimate equals company-paid miles times that row's frozen rate.
- One pay week runs Friday 12:00 AM through the next Friday 12:00 AM and is labeled by the ending Thursday.
- Use `Planned`, `Estimated`, `Final`, or `Voided`. Correct or void in place; never delete history. Settlement evidence outranks an earlier estimate.
- On both Thursday briefs, render the engine's mileage summary. If a known trip lacks a mileage entry or company-paid miles, ask only for the missing company-paid miles.

## Routes, trips, and watches

Read `references/route-weather.md` before changing any route, trip, runtime, departure, ETA, location, arrival, or watch. Write explicit changes immediately; never rely on conversational memory.

## Inbox and shipment maintenance

Read `references/email-reconciliation.md` before processing order mail, changing the active shipment queue, filing order threads, acting on `Is it OK to archive these emails?`, or deleting email. Important-email silence leaves the queue unchanged. Delete only the specific email or bounded set the user explicitly names.

## Automation maintenance

- Keep the scheduled prompt a dispatcher, not a policy copy. Canonical prompts are:
  - AM: `Use $ops-brief-policy to run the AM Daily Ops Brief. Return only the brief.`
  - PM: `Use $ops-brief-policy to run the PM Daily Ops Brief. This is my morning brief. Return only the brief.`
- Use titles `2:45 AM Eastern Ops Brief` and `2:45 PM Eastern Ops Brief`.
- Keep exact daily schedules at 2:45 AM and 2:45 PM with `TZID=America/New_York`, `RRULE:FREQ=DAILY`, and `default_timezone=America/New_York`. Set `DTSTART` to the next applicable local occurrence.
- For ordinary prompt or schedule changes, update the existing jobs in place.
- Identify Ops Brief jobs by the combination of title, AM/PM schedule, and an `$ops-brief-policy` invocation. If the active pair is ambiguous, stop before mutation and report the conflicting jobs.
- When the user explicitly requests a clean rebuild because the jobs or their chat context are stuck/bloated, use this transaction:
  1. Snapshot the exact old AM/PM job IDs, prompts, schedules, titles, timezones, and enabled states.
  2. Before mutation, harmlessly read both Sheet metadata/ranges, the Gmail account profile or labels, and the Calendar profile or calendar list. If any dependency is unavailable, stop and report `Action Required — <dependency> unavailable.`
  3. Pause the enabled old AM/PM jobs. If either pause fails, restore both old jobs to their snapshotted enabled states, re-inspect once, and abort before creation.
  4. Create fresh independent AM and PM jobs with the canonical fields above.
  5. Re-inspect automations and verify exactly two active Ops Brief jobs with the correct prompts, schedules, and timezone.
  6. If either creation or final verification fails, pause every newly created Ops job and restore each old job to its snapshotted enabled state. Re-inspect once and report the rollback result.
- Never create AM/PM child jobs, supporting scheduled jobs, retries, or duplicate schedules. Segment workflow inside the skill references instead.
- A scheduled run must not edit, create, duplicate, reschedule, inspect, or repair automations.

## Continuation and recovery

Treat clear equivalents of “continue Daily Briefs,” “we’re here now,” “the old thread got too long,” or “pick up the briefs here” as bootstrap commands. Inspect the automation list and both live Sheets, apply the routing above, and continue without making the user restate prior state.

When a newly available capability would materially improve reliability or maintenance, surface one concise `OPTIONAL UPGRADE` with benefit and tradeoff. Never install, connect, or migrate without approval.
