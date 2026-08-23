# Automation Contracts

Scheduled prompts are dispatchers, not policy databases. Durable behavior lives in the skill/repository and mutable state lives in canonical authorities.

## Scheduling timezone integrity

Every deployment has one canonical IANA timezone. A scheduled job is healthy only when the evidence that actually controls execution agrees with that timezone.

Required evidence:

1. the normalized VEVENT/RRULE contains the intended local clock time and an explicit canonical `TZID` when the scheduler supports it;
2. exactly one intended dispatcher is enabled, with the expected `timing_mode`;
3. notification channels required by the user are enabled;
4. after creation or repair, an actual firing and canonical Run Log entry land in the intended local slot.

Do not infer scheduler health from a field merely named `default_timezone`. Connector/tool readbacks may expose the current session, device, or travel timezone rather than a persistent scheduler execution timezone. Treat such a field as authoritative only when the provider/tool contract explicitly defines it as the task's stored execution timezone. A value that changes as the user travels is diagnostic context, not scheduling authority.

For every create/update/consolidation:
- snapshot existing jobs before mutation;
- prefer editing the existing notification-capable canonical dispatcher over replacing it;
- write the smallest required change;
- read the task back;
- verify title, enabled state, exact recurrence, intended local time, visible TZID, timing mode, required notification state, and duplicate count;
- if replacement is unavoidable, verify the replacement's notification state before disabling the known-good dispatcher;
- verify the next actual firing or canonical Run Log entry before declaring a scheduler incident cleared.

Do not repeatedly recreate tasks to chase travel-local metadata. Do not compensate with hidden retry/watchdog jobs or a travel-local/UTC schedule that violates the deployment contract. If the intended scheduled slot is missed despite correct readback, generate the Pants Filling With Shit Report, preserve manual workflows and canonical state, and treat the scheduler as degraded until a subsequent actual firing proves recovery.

Leaving ChatGPT Work, closing the app, changing HOME/ROAD mode, or being physically away from home does not redefine the canonical schedule. Platform-level task pause/deletion/inactivity behavior is a separate condition and must be diagnosed separately.

## Ops Brief

Title: `2:45 AM/PM Eastern Ops Brief`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

The dispatcher invokes `$ops-brief-policy` for the current Eastern slot. It must not contain mutable task/route/order/routine data or inspect/mutate automations during a scheduled run.

Context such as HOME/ROAD may change brief contents; it does not change the dispatcher timezone. Being physically away from home, offline, or outside a work context must not be treated as a timezone change.

The dispatcher must write the canonical Run Log for every attempted scheduled slot. Missing Run Log evidence after the intended slot is a scheduler/runtime incident, not a silent success.

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

Starter deployments may opt into recurring routine or study check-ins. These must use the fewest scheduled dispatchers practical, preserve mutable routine/study state in canonical authorities, and obey the same scheduler integrity gate. Do not create one permanent automation per exercise, assignment, course, project, or session when a consolidated dispatcher can resolve due items from state.
