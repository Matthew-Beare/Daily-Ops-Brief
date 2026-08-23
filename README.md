# LyfeOS / Daily Ops Brief

LyfeOS is a version-controlled personal-operations framework for briefs, persistent state, receipts/orders, planning/accountability, work/context, meal planning, appointments/calendar reconciliation, assets/knowledge, travel/hobbies, and evidence-backed automation.

This repository is **intentionally public**. It is the stable upstream plus a public reference deployment. **Mutable operational state** remains in external canonical authorities such as Sheets/Drive/database services; Git versions behavior, schemas, configuration, migrations, features, tests and recovery rather than acting as a dump of the user's live life.

## Start here as a new user

Use [`starter/START_HERE.md`](starter/START_HERE.md). The normal lifecycle is:

1. fork this public upstream into a repository the user controls, or use a clean audited snapshot;
2. connect that repository and only the apps/services the user wants;
3. run the adaptive first boot;
4. inspect existing capabilities/evidence before asking the user to rebuild information manually;
5. create the user's timezone, authorities, modules, schedules and durable configuration;
6. commit/push and verify a coherent first-boot Git checkpoint;
7. run source/privacy/CI gates before scheduled writes;
8. evolve custom behavior in that user's own fork;
9. when a personal feature becomes reusable, ask whether the user wants to sanitize and contribute it upstream.

**Do not inherit the reference deployment's Google IDs, schedules, aliases, vehicles, tasks, receipts, or mutable state.** Those are reference configuration, not starter defaults.

A user's source repository may be public or private. Public source requires the public-source audit; private source follows the same no-secrets rule.

## Inherit → customize → improve → share

LyfeOS is designed for personal forks, not passive installations.

```text
public LyfeOS release
        ↓ fork
user-owned LyfeOS
        ↓ first-boot Git checkpoint
personal feature/fix branches
        ↓ optional experimental integration
user stable release
        ↓ opt-in sanitization
upstream pull request
        ↓ public review/release
other user forks
```

Custom features commit to the user's own Git lineage under their authorization. Sharing is separate. When a coherent personal feature passes tests/privacy/source checks, LyfeOS asks: `Do you want to make this feature available to other people?` A yes prepares a sanitized portable contribution; it never silently publishes personal configuration/state.

See `starter/PERSONAL_FORK_LIFECYCLE.md` and `starter/SHARED_FEATURE_WORKFLOW.md`.

## What LyfeOS can organize

The adaptive interview can surface domains the user did not know to request, including:

- concise manual/scheduled briefs and prioritized next actions;
- tasks, projects and recurring accountability;
- work-pattern discovery and conditional HOME/ROAD/TRUCK/FIELD-style contexts;
- exercise/fitness with optional supported wearable/activity evidence;
- school/study planning and context-aware next-action coaching;
- meal planning, grocery intent, recipes, leftovers/pantry/freezer workflows;
- hobbies, hiking/outdoor preparation, vacations/trip planning and travel logistics;
- appointments/reservations with verified email → Calendar update-in-place reconciliation;
- orders, receipts, cancellations, replacements, refunds and active shopping intent;
- assets, fitment, manuals/reference knowledge, warranties and maintenance;
- household/reimbursement and selected finance workflows;
- actionable email and durable reference material.

Before proposing new connections, first boot follows `starter/CAPABILITY_DISCOVERY.md`: use current context/files and inspect relevant already-connected capabilities when possible. Arbitrary old ChatGPT conversations are not assumed globally searchable; inaccessible prior-chat content gets an explicit ingestion path rather than fictional access.

Chat is the interface. Canonical connected stores are the live state/evidence plane. Each user's Git fork is the durable behavior/version/recovery plane.

## Dependency design

Core onboarding/Git/recovery stays usable without optional integrations. Gmail, Calendar, finance, fitness/activity, maps/weather and other apps are module-scoped adapters. A missing optional connector must not disable unrelated life domains.

Prefer one canonical authority per data class, one Git lineage per deployment, one consolidated scheduler per purpose/cadence, Calendar events for event-specific reminders, and readback verification at write boundaries. This deliberately minimizes layers that can fail together.

## Repository layout

- `starter/` — sanitized onboarding/distribution boundary
- `starter/features/` — portable feature contracts/manifests
- `skill/ops-brief-policy/` — public reference deployment policy/runtime
- `project/INSTRUCTIONS.md.tmpl` — reference deployment bootstrap
- `scripts/` — validation/source/privacy/bootstrap/fingerprint/import tools
- `tests/` and `starter/tests/` — regression/portable lifecycle tests
- `docs/` — architecture/data/automation/privacy/lifecycle notes

The reference deployment is intentionally public, but it is **not** copied as new-user state.

## Appointment verification example

When a user opts into appointment-email reconciliation, the feature reads complete relevant evidence, dedupes a canonical appointment/source identity, creates or updates one linked Calendar event, then reads it back to verify event ID, calendar, title, time/timezone, reminders and source linkage. Revision/cancellation evidence updates the same event. Ambiguity asks instead of guessing. Event-specific reminders live in Calendar rather than spawning one ChatGPT task per appointment.

## Validate

The release gate runs:

```bash
python3 scripts/validate_repo.py .
python3 scripts/audit_public_source.py .
python3 scripts/audit_starter_privacy.py starter
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skill/ops-brief-policy/scripts -p 'test_*.py'
python3 starter/tools/validate_feature_manifest.py
python3 -m unittest discover -s starter/tests -p 'test_*.py'
```

CI runs the coherent checkpoint on pull requests and `main`.

## Source and privacy policy

Public visibility is not an error. **Unintended source data is.** Never commit credentials/secrets, full payment-card/account numbers, mutable operational exports, private message/receipt bodies, medical records, school submissions, `.env`/local secret configuration, or personal information the owner did not deliberately choose to publish.

Non-secret reference identifiers may exist in the intentionally public reference deployment, but new deployments create/select their own authorities.

## Reliability rules

- Mutable state lives in canonical connected authorities, never only chat/Git.
- Scheduled prompts remain thin and do not mutate their own automation definitions.
- Use the fewest recurring dispatchers; no hidden retry/child/per-order/per-appointment job fan-out.
- Retry is optional/bounded. Repeated/no-progress/ambiguous failure trips the **Pants Filling With Shit Report** circuit breaker and stops only the affected module.
- One purchase is one Receipt ID/total; shopping intent, refund and reimbursement remain distinct.
- People/assets/retained knowledge use immutable UUID identity.
- Email sending remains approval-gated.
- CI success never substitutes for live provider readback when provider behavior matters.

## Public distribution and releases

`main` is the stable public release line only after repository validation, public-source audit, starter privacy audit, deterministic/runtime tests, portable feature/starter tests and merge authority pass. Feature branches are development surfaces, not installation targets.

See `starter/VERSIONING.md`, `starter/PERSONAL_FORK_LIFECYCLE.md`, `starter/CAPABILITY_DISCOVERY.md`, and `starter/DEPENDENCIES.md`.