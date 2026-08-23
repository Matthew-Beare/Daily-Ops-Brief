# Emergency Ripcord / Fail-Fast Circuit Breaker

Load this reference for connector/API failures, repeated tool errors, validation loops, ambiguous partial writes, stalled workflows, or any run that is no longer making measurable forward progress.

The deployment nickname may be “pants-full-of-shit emergency ripcord.” The production behavior is a deterministic fail-fast circuit breaker, not a joke: it exists to stop one bad subsystem from filling the rest of the run with increasingly bad state.

## Core rule

**Stop escalation before stopping useful work.** A failure in one module degrades that module only unless the failed authority is shared by the whole run or continuing would risk corrupting canonical state.

Never keep retrying because a run “might work this time.” Never spawn child/retry automations. Never compensate for a failed authority with chat memory or guessed state.

## Trip conditions

Trip the ripcord when any of these occurs:

1. **Repeated identical failure:** the same external operation fails twice with materially the same error and no new evidence/state change between attempts. Default retry budget is one retry after the initial attempt.
2. **No forward progress:** two consecutive workflow cycles produce no new evidence, no state transition, and no narrower diagnosis.
3. **Permission/dependency failure:** a required connector, Sheet, Drive folder, repository permission, account authorization, or provider capability is unavailable. Do not hammer permission errors with retries.
4. **Ambiguous/partial mutation:** a non-atomic write may have partially succeeded, the provider response is ambiguous, or a write/readback disagree. Stop additional mutations in that module until canonical readback/reconciliation establishes exact state.
5. **Integrity failure:** validation, Audit, fingerprint, schema, dedupe, allocation, payment, or identity checks fail in a way that makes further writes unsafe.
6. **CI loop:** the same failing CI job/test is rerun without a code/config change that addresses the diagnosed cause. Inspect the failure first; do not blind-rerun.
7. **Scope creep under failure:** fixing one error starts creating unrelated jobs, databases, routes, receipts, assets, or other state. Stop and preserve the last known-good boundary.

## Allowed retry behavior

- One retry after the initial attempt is allowed only when the operation is idempotent or read-only and the failure looks transient.
- A retry must use either new evidence, a corrected argument, or a transient-error rationale. Repeating the exact same failing mutation more than once is prohibited.
- Validation/test reruns after a real code/data fix do not consume the same failure budget because the input state changed.
- Rate-limit/provider-backoff instructions may delay within the current supported execution path, but never create hidden background/retry jobs.

## Ripcord transaction

When tripped:

1. **Stop writes for the affected module.** Do not continue mutating adjacent records hoping later work will repair it.
2. **Preserve verified state.** Do not delete or roll back known-good committed state merely to make the run appear clean.
3. **Read back canonical state** if the authority is reachable, and determine exactly what committed versus what did not.
4. **Reconcile partial effects** only when evidence makes the correction deterministic and safe. Otherwise leave the module degraded and surface Action Required.
5. **Continue unrelated modules** whose authorities/invariants remain healthy.
6. **Record one concise failure fact** in the normal run/audit surface when applicable. Do not create a new failure database.
7. **Report once, compactly:** `Emergency Ripcord — <module>: <trigger>. Preserved: <known-good state>. Blocked: <operation>. Next: <specific action>.`
8. **Do not recursively invoke the same workflow** during the same run after the ripcord trips.

## CI / Git hygiene

For multi-file durable changes that intentionally create temporary intermediate inconsistency (for example policy + tests + fingerprint):

- avoid keeping an open PR that runs CI on every knowingly incomplete intermediate commit when that creates notification spam;
- make the coherent batch on the feature branch while the PR is closed or otherwise not triggering PR CI;
- reopen once the batch is internally consistent;
- inspect the first failing job/test/log before changing code;
- fix the diagnosed cause, then run CI again;
- do not weaken a real invariant merely to get green CI;
- restore any temporary diagnostic-only validator relaxation before final approval/merge.

A CI failure is evidence, not a command to repeatedly rerun CI.

## Scheduled-run behavior

Scheduled Ops/receipt runs must use this circuit breaker without changing automation definitions. A degraded subsystem should produce one actionable failure summary while the rest of the brief/lifecycle continues when safe.

Examples:

- Mileage Sheet unavailable on a non-Thursday brief: mileage section degrades; other brief sections continue.
- Gmail permission failure during lifecycle: stop Gmail mutations, preserve already-verified Sheet state, report the permission issue; do not repeatedly retry or fabricate mail evidence.
- Drive manual upload ambiguous after a provider timeout: read back Drive/Knowledge Index before any second upload so the same manual is not duplicated.
- GitHub CI fails on one assertion: inspect the failing test/log, fix that cause, and rerun once after the change rather than generating a chain of identical red runs.

## Recovery

The next manual or scheduled run may retry the degraded module from canonical state. It must not assume the previous run completed. Re-read authoritative state, apply idempotent reconciliation, and clear the failure only after verified readback proves recovery.