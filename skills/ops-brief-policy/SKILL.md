---
name: ops-brief-policy
description: Canonical Daily Ops Brief policy for briefs, Ops maintenance/recovery, receipt lifecycle work, and Ops-list changes.
version: 3.0.1
---

# Ops Brief Policy

Use `policy/ops-brief-policy.yaml` as machine-readable policy. The Ops Status Register and Mileage & Pay Tracker are the only mutable authorities named there. Never substitute memory for unavailable canonical mutable state.

## Brief dispatcher

- Canonical timezone is `America/New_York`.
- Exactly two brief slots exist: 02:45 ET and 14:45 ET. The 14:45 PM slot is the user's morning brief.
- Resolve mode before rendering content.
- Mode precedence is: unexpired explicit `Control` Mode Override, then an `Active` row in `Trips` forces ROAD, then the weekly default.
- Weekly default is ROAD from Friday 12:00 ET through Wednesday 16:30 ET, HOME otherwise.
- Expired overrides are ignored.
- In ROAD mode, suppress ordinary HOME-only chores and HOME weather. Include active route, current location, ETA/status when live evidence exists.

## Failure isolation

Inputs are section-scoped, not a single all-or-nothing blob. A broken optional section must not destroy a valid brief.

- The Ops Status Register is core. If it is unavailable, emit `Action Required — Ops Status Register unavailable` and do not invent mutable state.
- Mileage/pay is required for the Thursday mileage summary and for mileage mutations. It is not a global prerequisite for every brief.
- On a non-Thursday brief, mileage read/shape/parse failure must not abort output. Continue the brief; log `Degraded` only if the failed input was consulted.
- On Thursday, if mileage authority is unavailable, emit `Action Required — mileage/pay Sheet unavailable` and continue every other valid section.
- Use run status `Error` only when a core authority or required write makes the run invalid. Use `Degraded` for isolated section failure.

## Appointment cadence

- Saturday 02:45 AM is the weekly appointment look-ahead and includes appointments in the next 7 days.
- Otherwise remind the day before and the morning of.
- Never show appointment confirmation status.

## Change handling

A clear user correction to Ops state is an immediate canonical Sheet write. Preserve history with `Done`, `Removed`, lifecycle events, or equivalent existing schema rather than deleting history.

Durable policy, engine, schema-contract, or regression-test changes require a verified commit to `Matthew-Beare/Daily-Ops-Brief`. Do not claim Git success without a returned commit SHA/readback.

## Mail safety

Never send email automatically. Important actionable mail stays pending approval under the established archive-approval workflow. Never delete Gmail without an explicit bounded request.
