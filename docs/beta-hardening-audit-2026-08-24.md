# Daily Ops Brief beta-hardening audit — 2026-08-24

## Release disposition

**Clean-history release: pass. Installed runtime: pass. Production scheduler clearance: pending.** The repaired `main` branch contains only the sanitized release history—not the contaminated legacy commits—and passes the deterministic test suites, repository contract, final policy fingerprint, and current/history privacy gates. Full beta readiness still requires these independent live/provider gates:

1. the next real 2:45 AM/PM `America/New_York` dispatch produces the expected canonical Run Log evidence;
2. `main` has an enforceable required-check/branch-protection rule, or the provider limitation is explicitly accepted.

No test result can substitute for those provider/history facts.

## Root cause of the failed briefs

The failure was a stack, not one magic typo:

| Layer | Evidence-backed cause | Repair |
| --- | --- | --- |
| Scheduler | The recurrence/TZID said New York while stored execution metadata named a different timezone. Observed runs shifted by two hours. | Corrected the notification-capable dispatcher in place to `America/New_York`, consolidated the lifecycle and job-watch phases into it, paused active duplicates, and added IANA runtime entry evidence. |
| Runtime clock handoff | The 2026-08-24 PM task was recorded by the provider at 14:45:29 Eastern, but the agent supplied an earlier timestamp to the policy guard and was rejected before Run Log entry. | Production `slot-check` no longer accepts a model-created timestamp: omitting `--now` makes the executable capture its own UTC clock, wait once for at most 60 seconds of early handoff, and recapture before entry. Explicit `--now` remains diagnostic-only. |
| Delivery context | The task was bound to a long-lived chat and the client resurfaced an exact 2026-08-22 response instead of today's circuit-breaker result. | Production target is a standalone task whose runs start from the saved prompt. Every fresh brief begins with its deterministic `OPS-YYYY-MM-DD-AM|PM` Run ID and may not quote or reuse old chat output. |
| Failure isolation | A malformed or unavailable mileage range could abort the whole brief even when mileage was not due. | Mileage is now Thursday-only, section-scoped, and explicitly degraded when due but unavailable. |
| Deployment drift | The installed skill was older than the repository and routed through a duplicate wrapper that globally coupled optional inputs. | Deleted the wrapper/concurrency patch, made `ops_policy.py` the sole engine, synced the installed private skill, preserved its private locator separately, matched the public fingerprint, reran all 149 skill tests in place, and pushed the private skill commit. |
| Observability | “No Run Log row” was previously treated as proof that the scheduler never entered, even before the wrongly shifted execution instant. | Scheduled entry now upserts `Running` before downstream mutations and records logical slot, effective instant, delay, DST adjustment, phase, and state. |
| Runtime resilience | Work-credit/platform stalls could leave a long run without a trustworthy phase boundary. | Module-scoped circuit breaker, bounded retry, deterministic IDs, and last-known-good readback are explicit contracts. |
| Mode symptom | The visible brief could fall back or abort despite an active ROAD trip because the failing optional path prevented normal rendering. | Mode precedence is explicit override, active trip, then configured weekly schedule; optional module failure cannot erase core mode/tasks. |

## Failure matrix

| Boundary or failure | Required result | Verification |
| --- | --- | --- |
| Exact 02:45/14:45 Eastern entry | Enter once | Slot-engine unit and CLI tests. |
| Equivalent instant displayed in Eastern/Central/Mountain/Pacific/UTC | Convert through IANA timezone and enter one Eastern slot | Five-offset summer/winter matrix tests. |
| Up to 60 seconds early | Runtime waits once until the slot, recaptures its own clock, then enters | Owned-clock early-handoff test. |
| More than 60 seconds early, including one microsecond | Reject as not due | Fractional boundary test. |
| Up to 15 minutes late | Enter and record delay | Delayed-entry tests. |
| More than 15 minutes late, including one microsecond | Reject as not due | Fractional boundary and CLI exit-3 tests. |
| Spring-forward nonexistent slot | Use first valid instant once | DST-gap test. |
| Fall-back repeated slot | Use first occurrence only | DST-fold test. |
| Near midnight | Compare adjacent calendar-day slots | Cross-date nearest-slot test. |
| Naive scheduler instant | Fail cleanly; never guess offset | API/CLI tests. |
| Invalid `strict_inputs` spelling | Fail closed | Strict-flag test. |
| Missing/drifted core task/control schema | Whole core policy errors | Core-schema test. |
| Missing/drifted optional schema | Only affected module degrades | Optional-schema test. |
| Active trip at weekly HOME boundary | ROAD wins | Mode-precedence test. |
| Explicit HOME override during active trip | Override wins | Mode-precedence test. |
| Missing weekly mode configuration | Persistent core tasks survive; action required | Context-degradation tests. |
| Malformed appointment row/range | Appointment module degrades only | Appointment isolation/end/duplicate tests. |
| Malformed mileage on non-Thursday | Ignore mileage path | Non-Thursday isolation test. |
| Unavailable mileage on Thursday | Continue; exact mileage action | Thursday degraded test. |
| Invalid toggle or nonfinite/extreme numeric | Fail affected module explicitly | Toggle, NaN/Infinity, and magnitude tests. |
| Delivered shipment vs stale vendor status | Higher-authority terminal evidence wins | Shipment priority tests. |
| Split tracking list | One active row per package | Split-package tests. |
| Partial cancellation without order/tracking | Match original identity before replacing item | Partial-cancellation fallback test. |
| True replacement | Close/flag original and link distinct replacement | Replacement tests. |
| Merchant says no settlement but nonzero debit remains | Actionable contradiction | Payment test. |
| Debit and credit net to zero | Resolve no settlement | Payment zero-net test. |
| Pending credit against posted debit | Preserve credit in projected net | Pending-credit test. |
| Refund/reversal exceeds five Monday-Friday days | Action required at exact deadline | Financial-resolution tests. |
| Retired vs nonworking | Distinct composable roles | Router tests. |
| Parent/guardian plus another role | Preserve both; explicit primary | Router tests. |
| Dependent minor | Remains primary; away context requires approval | Router tests. |
| “Broadway” job title | Must not match `road` substring | Word-boundary router test. |
| Disabled/not-applicable service | Never recommend or auto-enable | Service-state tests. |
| Feature dependency version mismatch | Reject bundle | Manifest graph/version tests. |
| Untracked or symlinked candidate source | Privacy gate rejects | Source-audit tests. |
| Historical blocked binary/private source | History gate rejects | History-audit tests. |
| Failed bootstrap render | Preserve known-good output | Atomic bootstrap tests. |

## Code and executable-contract inventory

Every current Python source was parsed/compiled, its imports were checked for use, and its public entry/error behavior was reviewed. The old duplicate runtime wrapper and its concurrency monkeypatch tests were deleted; they added a second policy path without adding a capability.

| File or group | Why it remains | Direct evidence |
| --- | --- | --- |
| `skill/ops-brief-policy/scripts/ops_policy.py` | Sole deterministic mode/task/appointment/travel/mileage/slot engine and Run Log field producer. | Policy and entry suites, DST/mode/input/failure tests. |
| `reconcile_shipments.py` | Deterministic active-fulfillment reducer with authority priority, package split, cancellations, and replacements. | Shipment and ordering suites. |
| `payment_reconciliation.py` | Exact-cent expected/posted/pending debit-credit reconciliation. | Payment suite. |
| `financial_resolution.py` | Separate five-business-day refund/reversal deadline gate. | Financial suite. |
| `starter/tools/onboarding_profile_router.py` | Composable profile/context/service activation router, including retiree and parent/guardian support. | Router suite. |
| `starter/tools/validate_feature_manifest.py` | Closed portable-module schema, file-boundary, failure-domain, dependency/version, and honest-delivery validator. | Manifest/isolation suites. |
| `scripts/bootstrap.py` | Strict, atomic project-instructions renderer. | Bootstrap suite. |
| `scripts/import_run_sheet.py` | Deterministic terminal-pair evidence importer without personal aliases or fabricated history. | Import suite. |
| `scripts/audit_public_source.py` | Current/untracked/history credential, personal-data, authority-ID, symlink, and mutable-export gate. | Public-source audit suite and intentional history failure. |
| `scripts/audit_starter_privacy.py` | Narrow portable-starter contamination gate. | Starter privacy suite. |
| `scripts/policy_fingerprint.py` | Content-sensitive deployed-skill checkpoint, including agent metadata/assets but excluding tests and the explicit private authority locator. | Fingerprint suite. |
| `scripts/validate_repo.py` | Cross-document/release invariant gate. | Root contract test. |
| All `test_*.py` files | Regression evidence for the executable or contract named by the file; no test-only runtime path is deployed. | Three independent discovery suites plus manifest CLI. |
| CI/YAML/JSON schemas and manifests | Machine-readable release, scheduling, compatibility, profile-question, and module-boundary contracts. | Repository validator, JSON parsing, manifest validator, privacy gates. |

The large policy functions remain only where they execute one cohesive reducer over one authoritative dataset. Splitting them merely to reduce line count would add call indirection without a new failure boundary. New capabilities must be separate modules when they have different authorities, permissions, mutations, or failure behavior.

## Removed or rejected bloat

- duplicate `ops_policy_runtime.py` wrapper and concurrency monkeypatch;
- duplicate legacy skill copy under `skills/`;
- deployment-only override document from public source;
- personal IDs, URLs, email, aliases, assets, routes, rates, and schedule details from the public candidate tree;
- hard-coded personal weekly mode/terminal defaults;
- stale unprofessional circuit-breaker filename/label;
- UTC-candidate scheduler branch, which would create four candidates a day and violate the exact two-brief contract;
- universal-onboarding branch implementation claims that were not backed by provisioning/readback/tests.

## Live state changes already verified

- exactly one active `LyfeOS Control Cycle` dispatcher, with the only scheduled entries at 2:45 AM and 2:45 PM `America/New_York`;
- receipt/order lifecycle, PM qualified-job monitoring, and brief rendering are module-isolated phases inside that dispatcher; the former standalone lifecycle and job-watch tasks are paused;
- the dispatcher uses a thin policy-indirection prompt and read back with the exact recurrence, `exact_schedule`, `default_timezone=America/New_York`, and no active diagnostics;
- the canonical Ops Status Register now contains validated `Job Watch` and private `Job Watch Settings` tables for durable dedupe/report state without embedding a personal qualification baseline in portable source;
- Run Log expanded additively from 13 to 21 columns and read back without losing existing rows;
- weekly HOME and ROAD transition settings added to private Travel Settings and read back;
- active-trip authority preserved; no mutable personal row was copied into this public repository.
- installed private skill matches policy fingerprint `3e25de602af03bdddfab996e62768f66af23ca5aaacd038e9b57fc6ae52ba5e4`; its deployment-only locator remains outside the public fingerprint.

## Verification snapshot

- 154/154 policy/runtime/reconciliation tests pass in the source tree and again in the installed private skill.
- 53/53 starter/profile/manifest tests pass.
- 80/80 repository/bootstrap/import/privacy/fingerprint/metadata tests pass.
- Python compilation, JSON/YAML parsing, manifest file/dependency validation, whitespace checks, current-tree public-source audit, and starter privacy audit pass.
- Clean reachable-history privacy audit passes. The legacy repository's 16 historical findings were not imported; weakening the gate remains prohibited.
- The first clean-`main` CI run correctly failed because checkout exposed twelve legacy remote branches to the deliberate `--all` history scan. Those twelve named refs were then force-repointed to the sanitized release, read back at the expected commit, and the same all-ref history audit passed locally before the follow-up push.

## Known blockers and non-claims

- The `main` tree and all history reachable from `main` are sanitized. The 16 contaminated legacy findings are no longer reachable from a named branch; weakening the history gate remains prohibited.
- Branch protection/required CI is not currently enforceable through the available repository surface. That is a provider configuration blocker, not a code pass.
- Scheduler repair is not declared cleared until a subsequent real firing lands in Run Log at the intended Eastern slot.
- Contracts/speculation for SQL, mobile, Home Assistant, hardware sensing, complete meal planning, broad finance ingestion, backups, and other future modules are catalogued in the feature ledger. They are not falsely labelled implemented.
