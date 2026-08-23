# Ops State and Automation Maintenance

Load this reference completely before changing task, control, mode, mileage, automation, calendar-projection, or other persistent Ops state. Preserve Sheet identity, headers, validation, row formatting, provenance and history.

## Global capture from supported conversations

- A clear request to add/update/complete/pause/remove something from the named Daily/Ops system is a command to update the canonical Ops Status Register immediately when that authority is reachable from the current surface.
- Chat is an intake surface, not an authority. Never leave a durable Ops change only in chat memory, a project-local note, prompt, or second database.
- If a required connected Sheet/app cannot be reached or written from the current conversation, say the change was not persisted. Never claim account-wide interception of every ChatGPT conversation.
- For guaranteed LifeOS receipt/state ingestion, use a conversation where the configured project/skill and write-capable authorities are actually available. Global Custom Instructions may identify intent across chats but do not manufacture missing connector/tool access.

## Tasks

- Apply additions, completions, removals, pauses, renames, tier/classification changes, scheduling and visibility directly to the existing Ops Status Register.
- Mark completion `Done` and removal `Removed`; never delete task history or infer completion from silence.
- Ask only for a genuinely missing required field.

## Mode overrides

Use Control type `Mode Override`; Vacation and Home early are `Item` values.

- For an unambiguous “got home early” statement, run `python3 scripts/ops_policy_runtime.py home-early --now <current-Eastern-ISO> --pretty`, then upsert the returned Home early control row.
- Home early starts immediately, closes the current work-cycle mileage accrual at supported HOME arrival, and remains HOME through the next Friday 2:45 PM brief; runtime uses exclusive Friday 3:00 PM Eastern expiry.
- Mark a final active leg Arrived only when the user's statement/evidence supports it. Never fabricate arrival time or miles.
- Expired overrides are ignored by the engine rather than manually erased.

## Mileage and pay

- Log only company-paid miles stated by the user or credible company/settlement/run-sheet evidence. Never substitute map, odometer or estimated distance.
- A work cycle is the actual sequence of paid dispatch legs from work departure through confirmed HOME arrival. It normally closes Wednesday PM or earlier; Thursday is reporting-only unless a real paid leg is explicitly recorded after HOME.
- Every real dispatch leg gets its own Trip ID and Mileage Log occurrence when trip tracking is enabled. Never assume the first outbound destination returns directly home.
- A reusable route pair may be learned even when the user does not want a current Trip occurrence created. Do not create a Trip merely because a Route was updated.
- Use stable `MILE-###` rows and preserve corrections/voids in place. Settlement evidence outranks estimates.
- Freeze the applicable rate on each historical mileage row so future rate changes do not rewrite prior gross estimates.

## Routes, terminal pairs, trips and imported run sheets

Read `references/route-weather.md` before changing route/trip/runtime/departure/ETA/location/arrival/watch state.

- `Routes` is the learned reusable terminal-pair database; `Trips` and Mileage Log are occurrence history. Never create a parallel route database for an employer/shared run sheet.
- **Standing paid-mile rule:** company-paid terminal mileage is symmetric by terminal pair. Once A↔B is reconciled, write/use the same paid-mile value in both `Paid Miles A → B` and `Paid Miles B → A`, unless the user later gives an explicit exception for that pair.
- Route geometry/runtime may remain directional even when paid miles are symmetric.
- A shared/employer run sheet is an evidence source. Reconcile/upsert into existing Routes/Trips/Mileage using the strongest stable source/date/terminal/run identifiers; do not duplicate an occurrence already represented.
- Historical source variants and obvious human-entry errors remain provenance. For a reusable Route value, prefer explicit user/company corrections, then current/latest consistent evidence, then a strong repeated/modal value. Material conflicts that cannot be reconciled must be surfaced rather than silently averaged.
- When a paid-mile pair is learned, update the reusable Route record. Record an actual Trip/Mileage occurrence only when that leg happened and occurrence tracking is enabled/supported.
- Preserve terminal codes when location identity is unknown; enrich later rather than guessing a city from a similar code.

## Calendar projection state

- `Calendar Projection` is the dedupe/link table for optional projections from canonical LifeOS state to Google Calendar.
- Calendar projection is opt-in by event type. Never assume that enabling appointments also enables deliveries, work travel, trials, bills, deadlines, routines, study sessions or tasks.
- Each projected event stores source type/source ID plus Google Calendar event ID so revisions update the existing event instead of creating duplicates.
- If source state changes (delivery ETA, cancellation, reschedule), update/cancel the linked event according to that user's selected policy. Calendar is a presentation/scheduling surface; the underlying Sheet remains authoritative.
- Do not create a new automation per calendar event.

## Inbox and shipment maintenance

Read `references/email-reconciliation.md` before order-mail processing, shipment mutations, Gmail filing, archive approval or deletion. The standing 90-day FedEx/UPS/DHL/USPS carrier-retention exception lives there; all other Gmail deletion still requires explicit bounded authority.

## Automation maintenance

- Keep the scheduled prompt a thin dispatcher, not a policy copy.
- Keep exactly one active combined `2:45 AM/PM Eastern Ops Brief` and exactly one active consolidated Receipt & Order Lifecycle schedule.
- Scheduled runs never inspect/mutate automation definitions.
- The canonical timezone is scheduling authority. Current device/location/travel timezone is context only.

### Scheduler-timezone integrity gate

A visible `TZID=America/New_York` or correct RRULE is **necessary but not sufficient**. Some scheduling surfaces/providers also retain a separate stored/default/execution timezone. That second field can govern actual firing time.

Before any automation create/update/consolidation:
1. read the canonical IANA timezone from policy/state;
2. snapshot each affected job's title, prompt, schedule, enabled state, provider stored/default/execution timezone and last-run metadata;
3. inspect current provider/task capability and avoid changing a healthy canonical job if the available write path is known to restamp it with a travel-local timezone and offers no way to set the canonical timezone;
4. perform only the smallest required mutation.

After every automation create/update:
1. read the task back from the provider;
2. verify exact title/cadence/local clock time/RRULE and intended TZID;
3. independently verify the provider stored/default/execution timezone equals the canonical IANA timezone;
4. require exactly one active canonical job of each required type and no active child/retry/legacy duplicates;
5. when possible, verify the next provider run time or the next actual Run Log entry resolves to the intended canonical local slot.

Do **not** report a timezone repair successful from VEVENT text alone.

If provider readback stamps a travel/device timezone instead of the canonical timezone and the available API/UI exposes no reliable timezone setter:
- do not keep repeatedly recreating or editing jobs;
- restore the last verified healthy snapshot when a deterministic rollback is possible;
- otherwise preserve exactly the safest known task state, stop further automation writes, and generate `Pants Filling With Shit Report — automation scheduler`;
- state the exact platform-side action required to make the provider execution timezone canonical;
- keep manual briefs and unrelated modules operating from canonical state;
- do not compensate with UTC/Pacific aliases, hidden hourly checks, AM/PM child tasks, or travel-location-specific schedules that violate the deployment contract.

A repair is not cleared until provider readback shows canonical execution timezone and a subsequent firing/run-log timestamp proves the intended slot.

### Healthy consolidation transaction

For ordinary changes, update the existing canonical job in place only when the scheduler-timezone integrity gate is healthy.

To consolidate a healthy legacy AM/PM pair without burning another active task slot:
1. snapshot exact legacy job IDs/prompts/schedules/titles/timezones/enabled states;
2. harmlessly verify required authorities and scheduler-timezone integrity;
3. convert one healthy job into the canonical combined schedule;
4. read back both TZID and provider execution timezone before pausing the other legacy job;
5. re-inspect and require exactly one active canonical job;
6. on failure restore the snapshot and verify rollback.

Never create AM/PM child jobs, hidden retries, per-order jobs or support schedules.

## Repository and Project-instruction synchronization

- Treat the configured private Daily-Ops-Brief repository as the **sole source of truth** for lasting policy, code, tests, onboarding, schemas and recovery contracts. The installed skill is a **deployed runtime copy**, never a competing authority.
- Standing authorization covers scoped commits/pushes of non-secret durable changes without asking for a separate Git confirmation. Mutable Sheets/Gmail/calendar/account data never belongs in source control.
- Never auto-merge, publish publicly, force-push, commit secrets, or export mutable personal state without separate explicit authority.
- The ChatGPT Project-instructions field is not writable from every surface. Repository code must never claim it silently changed that UI field.
- Prefer a **stable bootstrap contract** in the Project instructions: fixed authorities, safety boundaries and repo/skill indirection. Routine policy/feature changes should update Git/skill without changing the Project field. Change the Project bootstrap only when its actual authority/safety/recovery contract changes.
- When the Project bootstrap genuinely changes and no direct Project-instructions write tool exists, return the full replacement under `PROJECT INSTRUCTIONS UPDATE`; never make the user splice a patch.
- If Git write/verification is unavailable, report `Action Required — repository synchronization unavailable` and do not claim the lasting change is fully saved.

## Continuation and recovery

Clear equivalents of “continue Daily Briefs,” “old chat is gone,” or “pick this up here” are bootstrap commands. Re-read canonical authorities and continue without requiring prior chat history.

When a newly available capability would materially improve reliability or maintenance, surface one concise `OPTIONAL UPGRADE` with benefit/tradeoff. Never install/connect/migrate a new external service without approval.
