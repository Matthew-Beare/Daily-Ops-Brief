# LyfeOS / Daily Ops Brief

LyfeOS is a version-controlled personal-operations framework for briefs, persistent state, receipts/orders, planning/accountability, work/context, meal planning, appointments/calendar reconciliation, assets/knowledge, travel/hobbies, and evidence-backed automation.

This repository is **intentionally public**. It is the stable upstream plus a public reference deployment. Mutable operational state does not belong in portable Git source.

## State and source architecture

For new-user starter deployments:

- **Git** is source/version lineage: policy, schemas, migrations, non-secret configuration, enabled features, tests, onboarding, provenance, and custom feature work.
- **Google Sheets** is the default structured mutable state authority.
- **Google Drive** is the default retained evidence/document authority when selected modules need files.
- **Google Calendar** is an optional projection/reminder surface.
- Another supported database may replace Sheets when explicitly selected.

The current Daily Ops reference deployment already follows this external-authority model with its configured Sheets/Drive authorities.

See `starter/STATE_AUTHORITY_MODEL.md`. `starter/GIT_STATE_MODEL.md` is retained only as a compatibility redirect from the short-lived Git-native-state design.

## Start here as a new user

Use [`starter/START_HERE.md`](starter/START_HERE.md). The normal lifecycle is:

1. inherit a pinned public LyfeOS release/commit/tree into a user-controlled Git repository;
2. run adaptive first boot;
3. inspect existing capabilities/evidence before asking the user to recreate information;
4. create/select the structured state authority and Drive evidence root;
5. create an `Authority Registry` and durable `Interview Ledger`;
6. generate schemas/migrations/configuration/feature lock/policy in Git;
7. verify state-authority writes and Git source checkpoint independently;
8. continue unresolved interview items across future conversations instead of assuming one perfect setup chat;
9. evolve custom behavior on feature branches;
10. when a feature becomes reusable, ask whether the user wants to contribute a sanitized portable version upstream.

**Do not inherit the reference deployment's Google IDs, schedules, aliases, vehicles, tasks, receipts, or mutable state.**

## Fail-forward onboarding

The interview is tracked in canonical state, not merely remembered in chat. Each question ID becomes one of:

`Unresolved` · `Asked` · `Answered` · `Resolved from evidence` · `Not applicable` · `Deferred`

Setup is complete only when every applicable question is resolved. A user may change topics freely: LyfeOS handles the immediate request, records any incidental answers, then resumes the next useful open interview item later. Evidence can resolve factual questions; preferences/permissions cannot be silently inferred.

See `starter/INTERVIEW_LEDGER.md`.

## Inherit → customize → improve → share

```text
public LyfeOS upstream
        ↓ inherit
user Git source lineage + selected state authorities
        ↓ personal customization
feature/* + optional experimental integration
        ↓ tested personal feature
        ↓ "Do you want to make this feature available to other people?"
sanitation + synthetic fixtures + CI
        ↓
public upstream PR
```

Sharing a **feature** is different from sharing **state**. A deployment may explicitly share a whole Google authority or a scoped shared workbook/folder with another person. That is recorded and verified separately from public Git contribution.

## What LyfeOS can organize

The adaptive interview can surface domains the user may not know to request, including:

- briefs and prioritized next actions;
- working/retired/other life-pattern discovery;
- tasks, projects, household/admin, and recurring accountability;
- exercise/fitness/hiking with optional supported wearable/activity evidence;
- school/study planning and context-aware coaching;
- meal planning, recipes, pantry/freezer/leftovers, grocery intent, and cost/waste workflows;
- hobbies, hiking/outdoor preparation, vacations/trip planning, and travel logistics;
- appointments/reservations with verified email → Calendar reconciliation;
- orders, receipts, cancellations, replacements, refunds, and active shopping intent;
- assets, manuals/reference knowledge, warranties, and maintenance;
- household/reimbursement and optional finance evidence;
- actionable email and durable reference material.

Before proposing new connections, first boot follows `starter/CAPABILITY_DISCOVERY.md` and reuses accessible existing systems when possible.

## Meal planning

First boot explicitly asks `Do you want help with meal planning?` If selected, existing accessible recipes/meal plans are reconciled before starting over. Structured recipe indexes, accepted plans, pantry/freezer state, meal history, and shopping intent live in the canonical structured state authority. Long recipe bodies/images/documents may live in Drive with stable links.

## Appointments and reminders

Appointment reconciliation can:

1. read complete evidence;
2. dedupe against canonical appointment/source state;
3. identify provider type from evidence;
4. if still unclear and research is allowed, research the provider using official/reliable public sources;
5. create/update one linked Calendar event;
6. apply a configured reminder profile;
7. read the Calendar event back;
8. write/read back canonical appointment + Calendar Projection state;
9. only then mark the source reconciled.

Supported organizational labels can include cardiology, endocrinology, audiology, primary care, dental, etc. Specialty is never treated as diagnosis/treatment evidence.

Reminder profiles may include multiple reminders such as day-before, a configured morning-of local clock time, and one hour before. Calendar owns event-specific reminders rather than spawning one ChatGPT Scheduled Task per appointment.

## Canonical scheduler clock

Recurring dispatchers use a canonical IANA timezone. Runtime comparisons convert the current instant into that timezone and compare the canonical local clock with the intended slot. They never depend on travel/device timezone or a hand-maintained UTC offset.

For example, a 2:45 New York dispatcher asks whether `America/New_York` is 02:45 or 14:45 at that instant, regardless of where the user currently is. IANA timezone rules handle DST.

## Dependency design

Use the fewest authorities necessary:

- one canonical mutable authority per data class;
- Drive only when retained files/evidence are useful;
- Git for durable source/versioning;
- optional integrations as module-scoped adapters;
- one consolidated scheduler per purpose/cadence;
- Calendar events for event-specific reminders;
- write/readback verification at every authority boundary.

## Repository layout

- `starter/` — portable onboarding/distribution boundary
- `starter/STATE_AUTHORITY_MODEL.md` — mutable-state/evidence authority contract
- `starter/INTERVIEW_LEDGER.md` — durable fail-forward onboarding contract
- `starter/features/` — portable feature contracts/manifests
- `skill/ops-brief-policy/` — current reference deployment policy/runtime
- `project/INSTRUCTIONS.md.tmpl` — reference deployment bootstrap
- `scripts/` — validation/source/privacy/bootstrap/fingerprint/import tools
- `tests/` and `starter/tests/` — regression and portable lifecycle tests

## Validate

```bash
python3 scripts/validate_repo.py .
python3 scripts/audit_public_source.py . --history
python3 scripts/audit_starter_privacy.py starter
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skill/ops-brief-policy/scripts -p 'test_*.py'
python3 starter/tools/validate_feature_manifest.py
python3 -m unittest discover -s starter/tests -p 'test_*.py'
```

## Reliability rules

- Mutable state lives in canonical authorities, never only chat/Git.
- Important mutations receive provider/state readback before success.
- Use the fewest recurring dispatchers; no hidden retry/child/per-order/per-appointment task fan-out.
- Retry is optional/bounded. Repeated/no-progress/ambiguous failure trips the **Pants Filling With Shit Report** circuit breaker and stops only the affected module.
- One purchase is one Receipt ID/total; shopping intent, refund, and reimbursement remain distinct.
- People/assets/retained knowledge use immutable UUID identity.
- Email sending remains approval-gated.
- CI success never substitutes for live provider readback when provider behavior matters.

`main` is the stable public upstream only after repository validation, public-source audit, starter privacy audit, deterministic/runtime tests, portable feature/starter tests, and merge authority pass.