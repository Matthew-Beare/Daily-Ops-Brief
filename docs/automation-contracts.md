# Automation Contracts

Scheduled prompts are dispatchers, not policy databases. Durable behavior lives in the skill/repository and mutable state lives in canonical authorities.

## Ops Brief

Title: `2:45 AM/PM Eastern Ops Brief`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

The dispatcher invokes `$ops-brief-policy` for the current Eastern slot. It must not contain mutable task/route/order data or inspect/mutate automations during a scheduled run.

## Receipt & Order Lifecycle

Title: `Receipt & Order Lifecycle`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=1,13;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

Dispatcher responsibilities:

- invoke `$ops-brief-policy` against live canonical authorities;
- apply receipt ingestion/photo intake, classification/fitment, email reconciliation, payment reconciliation, beneficiary/reimbursement, and vendor-contact approval policy as applicable;
- reconcile same-order revisions before matching account charges;
- keep expected charges open until settlement/no-settlement resolution;
- investigate unmatched/over/undercharges rather than guess;
- keep reimbursements separate from merchant refunds;
- dedupe evidence arriving from multiple conversations/sources;
- if external contact is needed, validate the recipient/no-reply state and official support channel, then notify with recipient, subject, full proposed message, and `Do you want me to send this email?`;
- never send external email in the scheduled run;
- never create per-order/child/retry automations;
- never inspect or mutate automation schedules during a scheduled run.

Only meaningful lifecycle/payment/reimbursement changes, exceptions, classification questions, and contact-approval proposals should produce a notification.
