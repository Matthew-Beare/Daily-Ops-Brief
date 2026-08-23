# LyfeOS / Daily Ops Brief

LyfeOS is a version-controlled personal-operations framework for briefs, persistent state, receipts/orders, planning/accountability, work/context, meal planning, appointments/calendar reconciliation, assets/knowledge, travel/hobbies, and evidence-backed automation.

This repository is **intentionally public**. It is the stable upstream plus a public reference deployment.

There are now two deliberately different state models:

- **New-user starter deployments:** mutable personal state lives in the user's **private Git deployment repository** under `starter/GIT_STATE_MODEL.md`, alongside policy/configuration/schemas/features/tests/version history.
- **Current Daily Ops reference deployment:** its established **Mutable operational state** remains in its configured Sheets/Drive authorities under `skill/ops-brief-policy/`. That is a deployment-specific compatibility exception, not the generic starter architecture.

The public upstream never receives another user's private `state/` tree.

## Start here as a new user

Use [`starter/START_HERE.md`](starter/START_HERE.md). The normal lifecycle is:

1. pin an audited public LyfeOS release/commit/tree;
2. create a private user-owned deployment repository seeded from that upstream source and record provenance;
3. run the adaptive first boot;
4. inspect existing capabilities/evidence before making the user rebuild information manually;
5. create the user's initial private Git state/config/features/policy;
6. validate, commit, push, and read back the first coherent personal checkpoint;
7. enable only selected provider/scheduler adapters whose own gates pass;
8. record later coherent state/reconciliation changes as small verified Git transactions;
9. evolve custom behavior in the user's own repository;
10. when a personal feature becomes reusable, ask whether the user wants to sanitize and contribute it upstream.

A standard GitHub fork of a public repository is public, so it is **code-only** for this architecture. Personal-state mode uses a private deployment repository that preserves upstream lineage/provenance. If a provider supports a genuinely private fork, that may satisfy the same contract.

**Do not inherit the reference deployment's Google IDs, schedules, aliases, vehicles, tasks, receipts, or mutable state.** Those are reference configuration/state, not starter defaults.

## Inherit → customize → improve → share

```text
public LyfeOS upstream
        ↓ pin + seed private lineage
private user-owned LyfeOS
        ↓ first-boot Git state checkpoint
personal state transactions + feature/fix branches
        ↓ tested personal release
        ↓ opt-in sanitization
public upstream pull request
        ↓ public review/release
other private personal deployments
```

Custom features commit to the user's own Git lineage under their authorization. Sharing is separate. When a coherent feature passes tests/privacy/source checks, LyfeOS asks exactly: `Do you want to make this feature available to other people?` A yes prepares a sanitized portable contribution that excludes private state; it never silently publishes the user's life.

See `starter/GIT_STATE_MODEL.md`, `starter/PERSONAL_FORK_LIFECYCLE.md`, and `starter/SHARED_FEATURE_WORKFLOW.md`.

## What LyfeOS can organize

The adaptive interview can surface domains the user did not know to request, including:

- concise briefs and prioritized next actions;
- working/retired/other life-pattern discovery;
- tasks, projects, household/admin, and recurring accountability;
- exercise/fitness/hiking with optional supported wearable/activity evidence;
- school/study planning and context-aware coaching;
- **meal planning**, grocery intent, recipes, leftovers/pantry/freezer workflows;
- hobbies, hiking/outdoor preparation, vacations/trip planning, and travel logistics;
- appointments/reservations with verified email → Calendar reconciliation and Git state readback;
- orders, receipts, cancellations, replacements, refunds, and active shopping intent;
- assets, fitment, manuals/reference knowledge, warranties, and maintenance;
- household/reimbursement and optional finance evidence;
- actionable email and durable reference material.

Before proposing new connections, first boot follows `starter/CAPABILITY_DISCOVERY.md`: inspect current context/files and relevant already-connected capabilities when possible. Arbitrary old ChatGPT conversations are not assumed globally searchable; inaccessible prior-chat content gets an explicit ingestion path into durable Git state.

## State and dependency design

For starter deployments, private Git is the **one canonical personal-state authority**. Optional integrations are adapters:

- Gmail/email → evidence;
- Calendar → projections/reminders;
- fitness/wearable → optional activity evidence;
- finance → optional account evidence;
- Drive/files → optional bulky evidence/import/export;
- maps/weather/travel tools → current planning inputs.

Accepted operational state and stable provider references commit into Git. Provider credentials do not.

Each coherent state mutation/reconciliation cycle reads remote HEAD, appends/updates state, validates, commits, pushes fast-forward only, and reads back the remote result. If the branch moved, re-read/reconcile instead of force-pushing.

This intentionally minimizes the number of independent state layers that can fail together.

## Meal-planning model

First boot explicitly asks `Do you want help with meal planning?` If selected, it looks for accessible existing recipes/meal plans before rebuilding them. Accepted recipes, meal plans, pantry/freezer facts, meal history, and shopping intent become private Git state. Shopping intent remains distinct from purchase history.

## Appointment verification model

For an approved appointment-email class:

1. read complete relevant evidence;
2. dedupe against canonical private Git appointment/source state;
3. create/update one linked Calendar event when Calendar is enabled;
4. read the Calendar event back and verify ID/calendar/title/time/timezone/reminders/source linkage;
5. commit the verified appointment/reconciliation state plus provider references into Git;
6. read the Git commit back;
7. only then mark reconciliation complete.

Revisions/cancellations update the same Git appointment and linked Calendar event. Ambiguity asks instead of guessing. Calendar handles event-specific reminders rather than spawning one ChatGPT task per appointment.

## Repository layout

- `starter/` — portable onboarding/distribution boundary
- `starter/GIT_STATE_MODEL.md` — canonical private Git state contract for new-user deployments
- `starter/features/` — portable feature contracts/manifests
- `skill/ops-brief-policy/` — current public reference deployment policy/runtime
- `project/INSTRUCTIONS.md.tmpl` — reference deployment bootstrap
- `scripts/` — validation/source/privacy/bootstrap/fingerprint/import tools
- `tests/` and `starter/tests/` — regression and portable lifecycle tests
- `docs/` — architecture/data/automation/privacy/lifecycle notes

## Validate

The public upstream release gate runs:

```bash
python3 scripts/validate_repo.py .
python3 scripts/audit_public_source.py . --history
python3 scripts/audit_starter_privacy.py starter
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skill/ops-brief-policy/scripts -p 'test_*.py'
python3 starter/tools/validate_feature_manifest.py
python3 -m unittest discover -s starter/tests -p 'test_*.py'
```

CI runs the coherent checkpoint on pull requests and `main`.

## Source and privacy policy

The public upstream is intentionally public. **Unintended private state exposure is an error.**

Never publish upstream:
- private deployment `state/`;
- credentials/secrets/tokens/keys;
- private provider/evidence references;
- private message/receipt bodies;
- medical/school/account records;
- full payment-card/account authentication data;
- private deployment configuration not deliberately intended for publication.

Portable features use placeholders and synthetic fixtures and pass the **public-source audit** before publication.

## Reliability rules

- Starter personal state is canonical in private Git; chat is never the database.
- The current reference deployment continues using its established Sheets/Drive authority contract.
- Scheduled prompts remain thin and do not mutate their own automation definitions.
- Use the fewest recurring dispatchers; no hidden retry/child/per-order/per-appointment task fan-out.
- Retry is optional/bounded. Repeated/no-progress/ambiguous failure trips the **Pants Filling With Shit Report** circuit breaker and stops only the affected module.
- One purchase is one Receipt ID/total; shopping intent, refund, and reimbursement remain distinct.
- People/assets/retained knowledge use immutable UUID identity.
- Email sending remains approval-gated.
- CI success never substitutes for live provider readback when provider behavior matters.

## Public distribution and releases

`main` is the stable public upstream only after repository validation, public-source audit, starter privacy audit, deterministic/runtime tests, portable feature/starter tests, and merge authority pass. Feature branches are development surfaces, not installation targets.