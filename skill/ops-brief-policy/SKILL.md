---
name: ops-brief-policy
description: Run and maintain the user's Daily Ops Brief control room using the live Ops Status Register, Mileage & Pay Tracker, Gmail evidence, and deterministic HOME/ROAD policy. Use for scheduled or manual 2:45 AM/PM briefs; inbox and shipment reconciliation; archive-approval replies; mode, vacation, or “got home early” changes; task/control updates; ROAD trips, learned routes, ETA, current-location status, company-paid mileage and estimated gross pay, optional severe-weather/road-condition watches; continuation/recovery requests; explicit rebuilds of stuck or bloated Ops Brief automations; and any clear request from any Chat, Work, project, supported voice, or dictation conversation to add, update, complete, pause, or remove something from the Daily Brief, Ops Brief, or Ops list. Do not use for unrelated reminders or generic spreadsheets.
---

# Ops Brief Policy

Keep mutable state in the two live Sheets, lasting policy/code/tests/bootstrap in the configured private Git repository, and scheduled prompts limited to slot selection. The installed skill is a deployed runtime copy, not a second policy authority. Never copy the mutable task, route, trip, mileage, suppression, override, shipment, or run-log database into prompts, instructions, memory, or another file.

## Authority

- Timezone: `America/New_York`.
- Ops Status Register: `https://docs.google.com/spreadsheets/d/10WMU_hDMfSJcACel--8LekT7So5MXKgWuLVxvnSCPNU/edit`.
- Mileage & Pay Tracker: `https://docs.google.com/spreadsheets/d/1OUzdjZaVTidLnMX2xuIZ3mRVDOF5oAfT8-pdl6KfUfI/edit`.
- Purchase & Receipt Archive: `https://docs.google.com/spreadsheets/d/1pHkTdCxmdBdZjnVu97FkpkiSjysLkhjuTEcfcEXzmW8/edit`.
- Deployed engine: `scripts/ops_policy.py`.
- Deployed shipment reconciler: `scripts/reconcile_shipments.py`.
- The `Shipments` tab is an active queue only. Durable purchase and lifecycle history belongs in the Purchase & Receipt Archive; Gmail remains the source evidence.
- If either Sheet is unavailable, report `Action Required — <sheet name> unavailable.` Never substitute remembered or previously rendered state.

## Route the request

- For a scheduled or manual brief, read [the brief-run workflow](references/brief-run.md) completely and execute it. Do not load state-maintenance instructions during the run.
- For task, control, mode, mileage, automation, or other persistent-state maintenance, read [the state-maintenance workflow](references/state-maintenance.md) completely before acting.
- For shipment, order-email, inbox-filing, archive-approval, or explicit email-deletion work, read [the email-reconciliation workflow](references/email-reconciliation.md) completely before acting.
- For purchase-receipt ingestion, Drive receipt filing, monthly receipt rollups, or inventory side effects, read [the receipt-ingestion workflow](references/receipt-ingestion.md) completely before acting.
- For any route, trip, ETA, location, arrival, or ROAD-weather-watch change—or when the brief engine activates route weather—read [the route-weather workflow](references/route-weather.md) completely before acting.
- For a continuation/recovery phrase, read state maintenance, inspect the live automation list and Sheets, then continue from those authorities without requiring a magic sentence.

## Non-negotiable invariants

- Keep exactly one active Ops Brief automation. It dispatches at both 2:45 AM and 2:45 PM Eastern; the PM brief is the user's “morning” brief.
- Never revive 3:00 AM/PM, Pacific, UTC-shifted, noon, midnight, duplicate, or extra Ops Brief schedules.
- Keep each scheduled run single-purpose: render one brief and record one deterministic Run Log result.
- Never hard-code task-specific exceptions; use the live row fields and engine result.
- Never display appointment-confirmation state. It is hidden anti-nag state only.
- Appointment reminders are mode-independent: Saturday 2:45 AM previews the next seven calendar days (Saturday through Friday); all other 2:45 AM briefs show appointments for that day, and every 2:45 PM brief shows appointments for the next day.
- Reconcile Gmail against the active `Shipments` queue before rendering either brief. Read complete materially relevant threads; snippets alone are not evidence.
- Delete delivered items from the active `Shipments` queue immediately. Report a newly observed delivery once from `Order Events`, then never re-report it.
- Treat a replacement with a new merchant order number as a new Receipt ID linked bidirectionally to the original; never overwrite the cancelled order. A same-order revision stays under the original Receipt ID.
- Never guess an unknown purchase classification. Keep it in `Classification Queue` and ask for the smallest useful choice in the next brief.
- Keep important email in Inbox under `Ops/Archive Approval` until the user approves archiving. Silence is not approval.
- Do not monitor promotions or sales unless the user explicitly reinstates that scope.
- For a lasting Ops policy change, provide the complete revised project-instructions block when the bootstrap contract changes; never provide a partial instructions patch.
- The configured private Daily-Ops-Brief repository is the sole policy source of truth. Treat versioning as part of every lasting policy, schema, workflow, schedule, onboarding, or output-contract change: update tests and fingerprints, commit and push that repository, redeploy the installed skill from the committed source, and verify the remote result without waiting for a separate Git prompt. Never auto-merge, publish publicly, or commit mutable data or secrets.
- Prefer an explicit degraded brief over retries, loops, or a run that never finishes.
