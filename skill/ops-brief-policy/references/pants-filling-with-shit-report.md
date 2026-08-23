# Pants Filling With Shit Report

Load this reference for connector/API failures, repeated tool errors, validation loops, ambiguous partial writes, scheduler timezone drift, stalled workflows, CI failures, or any run that stops making measurable forward progress.

This is the deployment's fail-fast circuit breaker. Its job is to stop a localized failure from turning into a long chain of retries, duplicate writes, conflicting state, wrong-time notifications, or silence while useful unrelated work could still continue.

## Core rule

**Stop escalation before stopping useful work.** A failure in one module degrades that module only unless the failed authority is shared by the whole run or continuing would risk corrupting canonical state.

Never keep retrying because a run might work this time. Never create child/retry automations. Never replace a failed authority with chat memory or guessed state.

## Trip conditions

Generate a **Pants Filling With Shit Report** and trip the circuit breaker when any of these occurs:

1. **Repeated identical failure:** the same external operation fails twice with materially the same error and no new evidence/state change between attempts. Default budget is the initial attempt plus at most one retry.
2. **No forward progress:** two consecutive workflow cycles produce no new evidence, no state transition, and no narrower diagnosis.
3. **Permission/dependency failure:** a required connector, Sheet, Drive folder, repository permission, account authorization, scheduler capability, or provider capability is unavailable. Do not retry permission failures unless authorization/state changed.
4. **Ambiguous/partial mutation:** a non-atomic write may have partially succeeded, the provider response is ambiguous, or write/readback disagree. Stop additional mutations in that module until canonical readback establishes exact state.
5. **Integrity failure:** validation, Audit, fingerprint, schema, dedupe, allocation, payment, identity, or scheduler-timezone checks fail in a way that makes more writes unsafe.
6. **Scheduler execution timezone mismatch:** the requested/visible schedule uses the canonical timezone but provider readback shows a different stored/default/execution timezone, or an actual firing occurs at the travel/device-local clock instead of the canonical local clock. Do not treat matching RRULE/TZID text as proof of repair.
7. **CI loop:** the same failing job/test is rerun without a code/configuration change that addresses the diagnosed cause. Inspect first; never blind-rerun.
8. **Scope creep under failure:** fixing one error starts creating unrelated jobs, databases, routes, receipts, assets, or other state.

## Retry policy

Retry is **not mandatory**.

- Retry once only when the operation is read-only or idempotent and the error plausibly looks transient, or when the first failure revealed a corrected argument that makes the next attempt materially different.
- Do **not** retry permission/authentication failures, deterministic validation failures, invalid schemas, known bad arguments, destructive mutations, ambiguous writes, or scheduler-timezone mismatches until the underlying state changes or canonical readback resolves uncertainty.
- Recreating the same scheduled task while the provider keeps stamping the same wrong execution timezone is not a materially different retry. Stop.
- Validation/test reruns after a real code/data fix are new attempts because the input changed.
- Provider backoff may be honored inside the current execution path, but never by creating a hidden retry automation.

## Pants Filling With Shit transaction

When tripped:

1. Stop writes for the affected module.
2. Preserve verified state; do not erase known-good commits merely to make the run appear clean.
3. Read back canonical/provider state when reachable and determine exactly what committed versus what did not.
4. Reconcile partial effects only when the correction is deterministic and evidence-backed.
5. Continue unrelated modules whose authorities/invariants remain healthy.
6. Record one concise failure fact in the normal Run Log/Audit surface when applicable. Do not create a separate failure database.
7. Report once in this form:
   `Pants Filling With Shit Report — <module>: <trigger>. Preserved: <known-good state>. Blocked: <operation>. Next: <specific action>.`
8. Do not recursively invoke the failed workflow again during the same run.

## Scheduler-specific preservation

When the trigger is scheduler timezone drift:
- snapshot/read back every affected task before another write;
- preserve the canonical desired timezone/schedule in policy/state;
- require exactly the configured canonical job count and avoid spawning compensating child/watchdog jobs;
- if deterministic rollback to a previously verified canonical execution timezone is possible, perform it once and verify;
- if the provider offers no write path for the stored/default/execution timezone, stop task mutations and require a platform-side correction rather than inventing a UTC/Pacific/local workaround;
- manual runs remain available while scheduling is degraded;
- clear the incident only after provider readback shows the canonical execution timezone **and** a subsequent actual run/Run Log timestamp lands in the intended canonical slot.

Being offline, outside a workspace, or physically away from home is not itself evidence that a server-side scheduled task should stop. Context modes affect content, not scheduling authority.

## CI / Git hygiene

CI should validate coherent checkpoints, not every temporary half-edit.

- Feature-branch `push` should not run the main CI workflow. Validate through a PR or deliberate manual dispatch; `main` may validate after merge.
- During a multi-file change, keep the PR closed/draft or otherwise non-triggering until the batch is internally consistent.
- Use concurrency cancellation so a newer PR revision cancels an obsolete in-flight CI run.
- Inspect the first failing job/test/log before changing code.
- Fix the diagnosed cause, then rerun.
- Do not weaken a real invariant just to get green CI.
- Policy, tests, schema, docs and fingerprint must be updated as one coherent release checkpoint before reopening for CI.

## Scheduled-run behavior

Scheduled Ops/receipt runs use this circuit breaker without changing automation definitions. A degraded subsystem produces one actionable report while unrelated safe work continues.

Examples:

- Mileage Sheet unavailable on a non-Thursday brief: mileage degrades; other brief sections continue.
- Gmail permission failure: stop Gmail mutations, preserve verified Sheet state, report authorization needed; do not retry repeatedly.
- Scheduler task returns `America/Los_Angeles` while policy requires `America/New_York`: stop automation writes and require scheduler/platform correction; do not recreate the job repeatedly or call the visible TZID sufficient.
- Drive manual upload response is ambiguous: read back Drive and Knowledge Index before another upload so the same manual is not duplicated.
- GitHub test fails on one assertion: inspect the failure, change the actual cause, then run CI after the coherent change rather than generating a chain of red runs.

## Recovery

The next manual or scheduled run may retry the degraded module from canonical state only after its underlying condition changed. It must not assume the failed run completed. Re-read authoritative state, apply idempotent reconciliation, and clear the failure only after verified readback proves recovery.
