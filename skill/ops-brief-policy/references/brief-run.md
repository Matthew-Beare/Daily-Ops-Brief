# Scheduled and Manual Brief Run

Load this reference completely for one AM or PM Ops Brief. Do not inspect automations, repositories, personal context, broad web results, skill registries, or state-maintenance instructions during the run. Browse only the explicit weather sources when the engine opens a weather gate.

## Fixed inputs

Read these exact Ops Status Register core ranges once:

- `Tasks!A1:L500`
- `Control!A1:I200`
- `Routes!A1:L500`
- `Trips!A1:O1000`
- `'Travel Settings'!A1:F100`
- `'Run Log'!A1:M1000`

Read `Shipments!A1:N500` before Gmail reconciliation. After all required shipment mutations, read `Shipments!A1:N500` exactly once more; that second read is authoritative for the rendered shipment section. Do not render from the pre-reconciliation read.

Read these Purchase & Receipt Archive ranges once:

- `Order Events!A1:Q1000`
- `Classification Queue!A1:L500`

Use the latest prior successful `Completed (ET)` value from Run Log as the delivery-event cutoff. If the receipt workbook is unavailable, mark the brief `Degraded`, skip delivery-once and classification rendering, and continue with the active shipment queue.

Read these exact Mileage & Pay Tracker ranges once:

- `'Mileage Log'!A4:O504`
- `Settings!A3:B8`

Read connected Google Calendar far enough ahead to cover the next seven days. Calendar is non-authoritative evidence: after one failed or unavailable call, use an empty appointments list, mark the run `Degraded`, and continue.

Appointment rendering is slot-based and independent of HOME/ROAD mode: the Saturday 2:45 AM brief shows appointments from Saturday through Friday (a half-open seven-calendar-day window); every other 2:45 AM brief shows appointments occurring that calendar day; every 2:45 PM brief shows appointments occurring the following calendar day. This produces the requested day-before and morning-of reminders without exposing confirmation state.

## Deterministic pass

1. Capture the actual start time in Eastern.
2. Build UTF-8 JSON with the raw range arrays and Calendar evidence:

```json
{
  "now": "current ISO-8601 timestamp with Eastern offset",
  "brief_slot": "AM or PM",
  "strict_inputs": true,
  "tasks_values": [["Task ID", "..."], ["TASK-001", "..."]],
  "control_values": [["Record ID", "..."], ["CTRL-001", "..."]],
  "routes_values": [["Route ID", "..."], ["ROUTE-001", "..."]],
  "trips_values": [["Trip ID", "..."], ["TRIP-001", "..."]],
  "travel_settings_values": [["Setting ID", "..."], ["TRAVEL-001", "..."]],
  "mileage_values": [["Entry ID", "..."], ["MILE-001", "..."]],
  "mileage_settings_values": [["Setting", "Value"], ["Rate per mile", "0.986"]],
  "appointments": [{"id": "...", "title": "...", "start": "ISO-8601", "end": "ISO-8601", "preparation": "optional"}]
}
```

3. Run `python3 scripts/ops_policy.py resolve --input <json-file> --pretty` from the skill directory.
4. Treat the result as authoritative for mode, input health, weather gates, mowing focus, route-watch eligibility, trip status, mileage/pay summary, actions, appointment items, task rendering, Run ID, and Run Log base fields.
5. If execution fails or returns `status: error`, render its error compactly under `ACTION REQUIRED`; never improvise the failed policy.
6. Set `Weather Watch` to `Off` for every returned `expired_watch_trip_ids` value while retaining the trip row.

An authoritative Sheet read, policy execution, or required mutation failure makes the run `Error`. When the Ops Status Register remains writable, upsert one error row for the deterministic Run ID before stopping.

## Bounded evidence pass

Perform one bounded pass per applicable external source. Run only the planned queries and never retry failures, recursively delegate, or block completion on Gmail, Calendar, NWS, or DOT/511. A failed non-authoritative source makes the run `Degraded`; finish with the evidence that succeeded.

### Gmail

- Load and follow `references/email-reconciliation.md`.
- Search new material since the latest completed brief, or the prior 24 hours if none exists.
- Separately inspect each active shipment by exact order number and tracking number, then inspect carrier/vendor delivery evidence first received since the latest completed brief. Search USPS, FedEx, UPS, and DHL evidence when applicable; absence of one carrier is not evidence of delivery.
- Cap each search at 50 results and read at most 20 materially relevant complete threads total.
- Surface only material medical, financial, employment, WGU, VA/USAJOBS, vendor, appointment, subscription, fraud, or security changes.
- Normalize materially relevant order/carrier facts and run `python3 scripts/reconcile_shipments.py reconcile --input <json-file> --pretty` with the pre-reconciliation `Shipments` values. Apply its active-row upserts and delivered-row deletions to the Sheet, then perform the Gmail filing transaction in the email-reconciliation workflow.
- Explicit user delivery statements outrank carrier evidence; carrier delivery/progress evidence outranks vendor status. Never infer delivery from age, an ETA, or a vendor's shipped notice.
- Re-read `Shipments!A1:N500` after mutations. Show active rows as `Item — ETA <date>` or `Item — No ETA`; add status only for a material exception.
- From `Order Events`, show each credible delivery observed after the previous successful brief exactly once as `Delivered — <item>`. Do not retain it in the active queue or show it on later briefs.
- From `Classification Queue`, render unresolved rows under `ACTION REQUIRED` as compact questions with exact vendor/order/item and the smallest useful choices. Do not infer an answer from silence.
- Search `in:inbox label:"Ops/Archive Approval"` after filing. Group related messages into concise decisions under `IMPORTANT EMAIL`, retain them in Inbox, and end that section with the exact line `Is it OK to archive these emails?`. If the user did not answer the prior brief, repeat the queue unchanged. Do not treat silence as approval.
- Do not search promotions, calculate discounts, or monitor sales.
- Exclude obvious wife-only cosmetics/beauty purchases from shared Amazon results. Include ambiguous/shared goods and surface wife-only items only for household-level exceptions.

### Weather

- When `home_weather_allowed` is true, check Shady Valley, Tennessee only if weather materially affects a HOME decision.
- When `mowing_weather_focus` is true, prioritize recent/forecast rain, drying, wetness, and realistic mowing windows. Mowing season is April 1 inclusive through November 1 exclusive.
- Never render Shady Valley weather in ROAD mode.
- When `route_weather_allowed` is true or a travel action requires input, load and follow `references/route-weather.md`. Otherwise do not mention or inspect route weather.

## Run Log

After evidence and required mutations finish, locate the exact deterministic Run ID in the loaded Run Log. Update that row on retries; otherwise use the first blank row. Never create two rows for one Run ID.

- Set `Started (ET)` and `Completed (ET)` to actual Eastern timestamps.
- Preserve engine policy version, mode, input health, action count, and error notes.
- Use `OK` when all requested checks complete, `Degraded` for a completed brief with a non-authoritative source failure, and `Error` for policy, authoritative Sheet, or required-mutation failure.
- In `External Evidence`, write only concise tokens such as `Calendar: OK; Gmail: 2 material threads; NWS: clear`.
- In `Mutations`, write only stable IDs or `None`; never copy message bodies, secrets, or the full brief.
- If the register itself is unavailable, report the blocker without claiming the run was logged.

## Output contract

Render only nonempty sections in this order:

1. `WEATHER`
2. `ROUTE WEATHER`
3. `SHIPMENTS` (active shipments plus newly observed deliveries exactly once)
4. `UPCOMING APPOINTMENTS`
5. `IMPORTANT EMAIL`
6. `OPS STATUS`
7. `MILES & PAY`, only when `mileage_summary_due` is true
8. `IMPORTANT` or `ACTION REQUIRED`, only when necessary
9. `TRIP STATUS`, always last when returned

Insert `ops_status_markdown` and `mileage_summary_markdown` verbatim. Render only `appointments_due`, chronologically, and never expose confirmation state. Render `IMPORTANT EMAIL` only from the current `Ops/Archive Approval` Inbox queue and always include its exact archive question. Keep the brief brutally compact: no empty headings, `None`, `Nothing new`, delivery history, or combined task bullets.
