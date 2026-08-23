# Automation Contracts

Scheduled prompts are dispatchers, not policy databases. Durable behavior lives in the skill/repository and mutable state lives in canonical authorities.

## Scheduling timezone integrity

Every deployment has one canonical IANA timezone. A scheduled job is healthy only when **both** of these agree with that timezone:

1. the visible VEVENT/RRULE definition and its intended local clock time;
2. the provider's stored/default/execution timezone returned by readback.

Do not infer scheduler health from `TZID` text alone. A provider may retain a separate execution timezone and may silently stamp the current travel/device timezone during a task edit. Current location is context, not scheduling authority.

For every create/update/consolidation:
- snapshot existing jobs before mutation;
- write the smallest required change;
- read the task back;
- verify title, enabled state, exact recurrence, local time, visible TZID, provider execution timezone and duplicate count;
- when available, verify the next provider firing or next canonical Run Log entry lands in the intended local slot.

If provider execution timezone differs from canonical timezone and the available scheduler path exposes no reliable setter, fail the automation-maintenance module closed. Do not repeatedly recreate the task, create hidden retry/watchdog jobs, or compensate with a travel-local/UTC schedule that violates the canonical contract. Manual workflows continue while the scheduling layer is degraded.

A timezone incident clears only after provider readback and a subsequent actual firing prove the canonical slot.

## Ops Brief

Title: `2:45 AM/PM Eastern Ops Brief`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

The dispatcher invokes `$ops-brief-policy` for the current Eastern slot. It must not contain mutable task/route/order/routine data or inspect/mutate automations during a scheduled run.

Context such as HOME/ROAD may change brief contents; it does not change the dispatcher timezone. Being physically away from home, offline, or outside a work context must not be treated as a timezone change.

## Receipt & Order Lifecycle

Title: `Receipt & Order Lifecycle`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=1,13;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

Dispatcher responsibilities:

- invoke `$ops-brief-policy` against live canonical authorities;
- apply receipt ingestion/photo intake, classification/fitment, email reconciliation, payment reconciliation, beneficiary/reimbursement, active Shopping & Procurement reconciliation, and vendor-contact approval policy as applicable;
- reconcile same-order revisions before matching account charges;
- keep expected charges open until settlement/no-settlement resolution;
- investigate unmatched/over/undercharges rather than guess;
- keep reimbursements separate from merchant refunds;
- dedupe evidence arriving from multiple conversations/sources;
- remove a fulfilled active shopping intent only after durable purchase/owner-confirmation evidence and verification; missing receipt/product identity remains a separate reconciliation task;
- if external contact is needed, validate the recipient/no-reply state and official support channel, then notify with recipient, subject, full proposed message, and `Do you want me to send this email?`;
- never send external email in the scheduled run;
- never create per-order/child/retry automations;
- never inspect or mutate automation schedules during a scheduled run.

Only meaningful lifecycle/payment/reimbursement/shopping changes, exceptions, classification questions, and contact-approval proposals should produce a notification.

## Accountability / study scheduling

Starter deployments may opt into recurring routine or study check-ins. These must use the fewest scheduled dispatchers practical, preserve mutable routine/study state in canonical authorities, and obey the same scheduler-timezone integrity gate. Do not create one permanent automation per exercise, assignment, course, project, or session when a consolidated dispatcher can resolve due items from state.
