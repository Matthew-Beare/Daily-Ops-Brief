# Automation Contracts

Scheduled prompts are dispatchers, not policy databases. Durable behavior lives in the skill/repository and mutable state lives in canonical authorities.

## Scheduling timezone integrity

Every deployment has one canonical IANA timezone. A scheduled job is healthy only when both the provider definition and the runtime canonical clock agree with that timezone.

Required evidence:

1. the normalized VEVENT/RRULE contains the intended local clock time and explicit canonical `TZID` when the scheduler supports it;
2. exactly one intended dispatcher is enabled with the expected `timing_mode`;
3. notification channels required by the user are enabled;
4. at execution, the current instant is converted through the IANA timezone database into the canonical timezone and that canonical local clock matches the intended slot;
5. after creation or repair, an actual firing and canonical Run Log entry land in the intended local slot.

Do not infer scheduler health from a field merely named `default_timezone`. Connector/tool readbacks may expose current session, device, or travel timezone rather than persistent scheduler execution state. Treat such a field as authoritative only when the provider/tool contract explicitly defines it as the task's stored execution timezone.

### Canonical runtime clock

Execution-time comparisons never use the user's current travel/device timezone and never use a hand-maintained UTC offset. Convert the current offset-aware instant with the configured IANA timezone, conceptually:

```python
canonical_now = now.astimezone(ZoneInfo(canonical_timezone))
```

Then compare `canonical_now.hour` / `canonical_now.minute` to the configured local slot. This makes DST an IANA database concern rather than a pile of seasonal arithmetic.

For the reference Ops Brief, `2026-08-23T12:45:00-06:00` is the same instant as 14:45 in `America/New_York` and is a valid PM slot. `12:40-06:00` converts to 14:40 New York and is not a valid slot. In winter, `12:45-07:00` converts to 14:45 New York because both regions' IANA DST rules are applied.

For every create/update/consolidation:
- snapshot existing jobs before mutation;
- prefer editing the existing notification-capable canonical dispatcher over replacing it;
- write the smallest required change;
- read the task back;
- verify title, enabled state, exact recurrence, intended local time, visible TZID, timing mode, required notification state, and duplicate count;
- if replacement is unavoidable, verify replacement notification state before disabling the known-good dispatcher;
- verify the next actual firing or canonical Run Log entry before declaring a scheduler incident cleared.

For every entered scheduled run:
- run the deployment's canonical-clock guard before downstream state-changing modules;
- if the canonical slot does not match, do not reinterpret travel/device time, do not proceed as if the intended slot fired, and apply the scheduler Pants Filling With Shit Report boundary;
- preserve the known-good scheduler definition and canonical state rather than manufacturing compensating UTC/Pacific/local jobs.

Leaving ChatGPT Work, closing the app, changing HOME/ROAD mode, or being physically away from home does not redefine the canonical schedule. Platform-level task pause/deletion/inactivity behavior is a separate condition.

## Cross-authority transaction isolation

Independent authorities are not treated as one distributed database transaction.

For every declared cross-authority projection or side effect:

1. identify the canonical source authority and stable source identity;
2. commit the canonical source mutation first and read it back;
3. derive desired target state from the verified source plus current target state;
4. write the target projection using stable correlation identity;
5. read the target back before marking that projection healthy;
6. if the target fails, preserve the canonical source record and mark only the target projection/module `Degraded` or `Pending`;
7. on a later run, reconcile source-to-target from current canonical state instead of replaying a blind mutation or creating a hidden retry job.

Never roll back, clone, renumber, or delete canonical source identity merely because an unrelated target is unavailable. Do not create active-active shadow state as an outage workaround. A provider-wide outage may affect several resources hosted by that provider, but unrelated providers/modules continue when their own invariants remain healthy.

## Ops Brief

Title: `2:45 AM/PM Eastern Ops Brief`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

The dispatcher invokes `$ops-brief-policy` for the current **canonical Eastern** slot. Runtime uses `scripts/ops_policy_runtime.py slot-check` / canonical clock evidence to verify that the current instant corresponds to 02:45 or 14:45 in New York before downstream module mutations.

The dispatcher must not contain mutable task/route/order/routine data or inspect/mutate automations during a scheduled run. Context such as HOME/ROAD may change brief contents; it does not change dispatcher timezone.

The first external mutation after deterministic entry should upsert the canonical Run Log row as `Running`; completion updates that same row. Missing Run Log evidence after an intended slot is a scheduler/runtime incident, not silent success.

Within the Ops Brief service, a writable core Ops Run Log is an intentional entry barrier for downstream state-changing brief modules. This is a service-local safety dependency, not a global LyfeOS dependency: A failed Ops Brief does not block the separately scheduled receipt/order lifecycle or other independent module families.

## Receipt & Order Lifecycle

Title: `Receipt & Order Lifecycle`

Schedule: `RRULE:FREQ=DAILY;BYHOUR=1,13;BYMINUTE=45;BYSECOND=0` with `TZID=America/New_York`.

The same canonical runtime clock rule applies: convert the current instant to `America/New_York` and require 01:45 or 13:45 for a scheduled lifecycle entry. Travel/device timezone never moves the lifecycle slot.

Dispatcher responsibilities:
- invoke `$ops-brief-policy` against live canonical authorities;
- apply receipt ingestion/photo intake, classification/fitment, email reconciliation, payment reconciliation, beneficiary/reimbursement, active Shopping & Procurement reconciliation, and vendor-contact approval policy as applicable;
- commit/read back the canonical Purchase & Receipt Archive transaction before reconciling downstream Ops `Shipments`, shopping, or asset/inventory projections;
- if a downstream projection is unavailable, preserve the canonical Receipt ID/order/event/allocation/evidence and report only that projection `Degraded/Pending`;
- later retries re-derive desired target state from canonical purchase state and current target state rather than cloning/replaying the purchase;
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

Starter deployments may opt into recurring routine or study check-ins. These use the fewest scheduled dispatchers practical, preserve mutable routine/study state in canonical authorities, and obey the same scheduler evidence chain and IANA canonical-clock guard. Do not create one permanent automation per exercise, assignment, course, project, or session when a consolidated dispatcher can resolve due items from state.
