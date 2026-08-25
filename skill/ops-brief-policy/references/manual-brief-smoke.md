# Manual Brief Smoke Test

Use this when the owner asks to prove that the **actual Ops Brief pipeline can run now**, outside the normal 2:45 AM/PM `America/New_York` scheduler slot.

This is not a synthetic-only demo. The real manual smoke path reads the same live canonical authorities and applicable evidence adapters as a normal brief, writes a uniquely namespaced manual Run Log record, and renders a fresh user-facing brief from the current run. It deliberately does **not** count as evidence that the scheduled dispatcher fired.

## Invocation contract

1. Read `brief-run.md` completely and use its normal live-authority, reconciliation, module-isolation, Gmail, Calendar, mileage, weather, Run Log, and output rules.
2. Do **not** run the scheduled `slot-check` gate. The purpose of this path is to be callable at any clock time.
3. Select the intended brief semantics explicitly as `AM` or `PM`. This controls the same task and appointment windows used by a scheduled brief.
4. Read the real required authorities first, then build the same strict JSON payload used by a scheduled brief, except do not invent `now`.
5. Run `python3 scripts/manual_brief_smoke.py --input <json-file> --slot AM --pretty` or `--slot PM`. For a real smoke run, omit `--now`; the executable captures its own system UTC instant and converts it through `America/New_York`.
6. `--now` is diagnostic/test-only. It exists so CI can prove off-slot behavior deterministically at any wall-clock time.
7. Require `invocation_mode: manual_smoke`, `manual_smoke.actual_brief_pipeline: true`, `manual_smoke.slot_gate_bypassed: true`, and `manual_smoke.scheduled_firing_evidence: false`.
8. Use the returned `OPS-MANUAL-...-AM|PM` Run ID for the manual Run Log row. Never overwrite or masquerade as the scheduled `OPS-YYYY-MM-DD-AM|PM` identity.
9. Upsert the manual Run ID as `Running` before downstream state-changing modules, then update that same row to `OK`, `Degraded`, or `Error` at completion, following `brief-run.md`.
10. Render and deliver the actual brief using the normal output contract. The manual Run ID is the first line.

## Scheduler evidence boundary

A successful manual smoke proves that the policy engine, current authorities, applicable evidence adapters, reconciliation path, Run Log mutation, and user-facing rendering can work **at the time of the test**. It does not prove that ChatGPT Scheduled Tasks entered at 02:45 or 14:45 Eastern, and it must never clear a scheduler incident by itself.

Scheduler health still requires an observed scheduled firing or canonical scheduled Run Log entry in the intended `America/New_York` slot.

## CI contract

CI must test the manual smoke wrapper with an explicit offset-aware diagnostic instant that is intentionally outside the 02:45/14:45 gate. The test passes only if the real policy engine resolves without a scheduler rejection and the result is visibly namespaced as manual, with `scheduled_firing_evidence: false`.

This makes the code test independent of whatever time GitHub Actions happens to execute while preserving a separate, honest test for the real scheduler.
