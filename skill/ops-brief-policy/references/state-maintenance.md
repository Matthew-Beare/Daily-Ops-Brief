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

- Keep the scheduled prompt a dispatcher, not a policy copy. The canonical prompt is: `Use $ops-brief-policy to run the Daily Ops Brief for the current America/New_York slot. Use AM before noon and PM at or after noon; the PM brief is my morning brief. Return only the brief.`
- Use the title `2:45 AM/PM Eastern Ops Brief`.
- Keep one exact schedule with `TZID=America/New_York`, `default_timezone=America/New_York`, and `RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0`. Set `DTSTART` to the next applicable 2:45 local occurrence.
- For ordinary prompt or schedule changes, update the existing canonical job in place.
- Identify the canonical Ops Brief job by the combined title, the twice-daily 2:45 Eastern rule, and an `$ops-brief-policy` invocation. Treat legacy AM-only or PM-only jobs as migration candidates, not additional required schedules. If more than one plausible combined job is active, stop before mutation and report the conflict.
- To consolidate a healthy legacy AM/PM pair without burning another active task slot, use this transaction:
  1. Snapshot the exact legacy job IDs, prompts, schedules, titles, timezones, and enabled states.
  2. Before mutation, harmlessly read both Sheet metadata/ranges, the Gmail account profile or labels, and the Calendar profile or calendar list. If any dependency is unavailable, stop and report `Action Required — <dependency> unavailable.`
  3. Update one healthy legacy job in place to the canonical combined title, prompt, schedule, and timezone.
  4. Re-inspect and verify that updated job before pausing the other active legacy Ops Brief job.
  5. Re-inspect and verify exactly one active Ops Brief automation with the canonical fields.
  6. If any update, pause, or verification fails, restore every snapshotted job to its former fields and enabled state, re-inspect once, and report the rollback result.
- When the user explicitly requests a clean rebuild because the job or its chat context is stuck/bloated, snapshot every active Ops Brief job, verify dependencies, pause them, create one fresh canonical combined job, and verify exactly one active canonical job. If creation or verification fails, pause the new job, restore every old job to its snapshotted fields and enabled state, re-inspect once, and report the rollback result.
- Never create AM/PM child jobs, supporting scheduled jobs, retries, or duplicate schedules. Segment workflow inside the skill references instead.
- A scheduled run must not edit, create, duplicate, reschedule, inspect, or repair automations.

## Repository and project-instruction synchronization

- Treat the version-controlled `project/INSTRUCTIONS.md.tmpl` as the complete ChatGPT Project bootstrap contract when the Daily-Ops-Brief repository is available.
- The user's standing authorization covers scoped commits and pushes of non-secret policy, schema, tests, onboarding, recovery, and bootstrap files to the configured private repository. After every lasting policy, schema, workflow, authority, schedule, onboarding, or output-contract change, update the installed skill and repository copy, run validation, refresh the fingerprint/template, commit, push, and verify the remote head and CI without asking for a separate Git confirmation. Temporary Sheet state does not trigger a repository write.
- Never auto-merge a pull request, make a repository public, publish a release, or commit mutable Sheet exports, Gmail content, receipts, credentials, tokens, keys, or full payment data without separate explicit authority.
- If the configured repository or GitHub write path is unavailable, preserve the validated local change and report `Action Required — repository synchronization unavailable`; never claim the lasting change is fully saved.
- If the project-instructions contract changed, return the entire rendered replacement under the exact heading `PROJECT INSTRUCTIONS UPDATE`; never return a partial patch or make the user splice text.
- If the project-instructions contract did not change, state `Project instructions unchanged.`
- Do not claim that repository code silently changed the ChatGPT Project instruction field. Code versions, renders, and verifies the replacement; the user must paste it unless the current surface exposes an explicit project-instructions write tool.

## Continuation and recovery

Treat clear equivalents of “continue Daily Briefs,” “we’re here now,” “the old thread got too long,” or “pick up the briefs here” as bootstrap commands. Inspect the automation list and both live Sheets, apply the routing above, and continue without making the user restate prior state.

When a newly available capability would materially improve reliability or maintenance, surface one concise `OPTIONAL UPGRADE` with benefit and tradeoff. Never install, connect, or migrate without approval.
