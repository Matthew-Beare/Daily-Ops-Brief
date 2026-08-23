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

- For an unambiguous “got home early” statement, run `python3 scripts/ops_policy_runtime.py home-early --now <current-Eastern-ISO> --pretty`, then add or update the `Home early` row from `sheet_fields`. Reuse the active row or allocate the next stable `CTRL-###`. Do not ask for priority/classification.
- `Home early` starts immediately and remains HOME through the next Friday 2:45 PM brief. Its exclusive expiry is Friday 3:00 PM Eastern, giving the scheduled 2:45 PM run enough execution grace. A later explicit work departure may start the next work cycle after the override expires.
- When Home early is confirmed, close current work-cycle mileage accrual at the confirmed home-arrival time and mark the final active leg `Arrived` when the user's statement supports that transition. Do not fabricate an arrival time or company-paid miles.
- For vacation or another temporary HOME interval, create a HOME Mode Override with an explicit Eastern start and exclusive expiry. Ask only when a required boundary is materially ambiguous.
- Never manually clear an expired override; the engine ignores it.

## Mileage and pay

- Log only company-paid miles stated by the user or shown by credible company/settlement evidence. Never substitute map, odometer, route, or estimated distance.
- Treat a work cycle as the actual sequence of paid dispatch legs from the first work departure until confirmed HOME arrival. It normally closes Wednesday PM but closes earlier when the user reports Home early. Thursday is reporting-only unless a real paid leg is explicitly recorded after HOME.
- The Thursday `Week Ending` remains the reporting/grouping bucket. It is not permission to keep accruing phantom miles after the user is HOME.
- Every actual dispatch leg gets its own Trip ID and mileage entry. Never assume the first outbound destination returns directly to the home terminal. Example: Morristown → Rialto, Rialto → Phoenix, Phoenix → Dallas, and Dallas → another terminal are separate legs whose paid miles are aggregated into the same work-cycle/reporting bucket when applicable.
- Start the next cycle with the next actual work departure/first new paid leg, normally Friday. Do not pre-create mileage for a planned leg whose company-paid miles are unknown.
- Use a stable `MILE-###` row with Thursday week ending, Trip ID, route, departure/arrival, endpoints, company-paid miles, miles source, status, notes, and update timestamp.
- For a new actual entry, replace that row's rate formula with the current numeric `Rate per mile` value so historical pay remains frozen when the default changes.
- Gross estimate equals company-paid miles times that row's frozen rate.
- Use `Planned`, `Estimated`, `Final`, or `Voided`. Correct or void in place; never delete history. Settlement evidence outranks an earlier estimate.
- On both Thursday briefs, render the engine's mileage summary even though mode is normally HOME. If a known completed/active paid leg lacks company-paid mileage, ask only for the missing company-paid miles.

## Routes, terminal pairs, trips, and watches

Read `references/route-weather.md` before changing any route, trip, runtime, departure, ETA, location, arrival, or watch. Write explicit changes immediately; never rely on conversational memory.

- `Routes` is the learned terminal-pair database. Store route geometry/runtime and company-paid mileage separately for A → B and B → A.
- `Paid Miles A → B` and `Paid Miles B → A` are independent facts, each with its own `Miles Source`. Never mirror, average, or infer the reverse company's paid mileage from the known direction or from map distance.
- A reverse route geometry/runtime may use an explicitly documented fallback when no reverse observation exists, but the paid-mile fields may not.
- When a user/company source provides a terminal-pair paid mileage, update the matching directional Route field and still write the actual Trip/Mileage Log entry. The Route row is learned reusable knowledge; the Mileage Log is the auditable occurrence used for pay.
- If terminal codes or endpoint identities are ambiguous, preserve the known code/location and ask rather than merging two terminals based only on similar names.

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

- Treat the configured private Daily-Ops-Brief repository as the sole source of truth for lasting policy, code, tests, recovery material, and bootstrap contracts. Its version-controlled `project/INSTRUCTIONS.md.tmpl` is the complete ChatGPT Project bootstrap contract.
- Treat the installed skill as a deployed runtime copy of the committed repository source, never as a competing authority. If it diverges, the repository wins and the skill must be redeployed from the verified commit.
- The user's standing authorization covers scoped commits and pushes of non-secret policy, schema, tests, onboarding, recovery, and bootstrap files to the configured private repository. After every lasting policy, schema, workflow, authority, schedule, onboarding, or output-contract change, update the repository source and tests, refresh the fingerprint/template, validate, commit, push, verify the remote head and CI, then deploy and verify the installed skill without asking for a separate Git confirmation. Temporary Sheet state does not trigger a repository write because the Sheets are already the sole mutable-data authorities.
- Never auto-merge a pull request, make a repository public, publish a release, or commit mutable Sheet exports, Gmail content, receipts, credentials, tokens, keys, or full payment data without separate explicit authority.
- If the configured repository or GitHub write path is unavailable, preserve the validated local change and report `Action Required — repository synchronization unavailable`; never claim the lasting change is fully saved.
- If the project-instructions contract changed, return the entire rendered replacement under the exact heading `PROJECT INSTRUCTIONS UPDATE`; never return a partial patch or make the user splice text.
- If the project-instructions contract did not change, state `Project instructions unchanged.`
- Do not claim that repository code silently changed the ChatGPT Project instruction field. Code versions, renders, and verifies the replacement; the user must paste it unless the current surface exposes an explicit project-instructions write tool.

## Continuation and recovery

Treat clear equivalents of “continue Daily Briefs,” “we’re here now,” “the old thread got too long,” or “pick up the briefs here” as bootstrap commands. Inspect the automation list and both live Sheets, apply the routing above, and continue without making the user restate prior state.

When a newly available capability would materially improve reliability or maintenance, surface one concise `OPTIONAL UPGRADE` with benefit and tradeoff. Never install, connect, or migrate without approval.
