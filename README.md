# LyfeOS / Daily Ops Brief

LyfeOS is a version-controlled personal-operations framework for briefs, persistent state, receipts/orders, planning/accountability, work-away context, assets/knowledge, calendar projection, and evidence-backed automation.

This repository is **intentionally public**. The public source contains portable starter material plus a public reference deployment. Mutable operational state remains in external canonical authorities such as Sheets/Drive/database services; Git is source, not the user's live database.

## Start here as a new user

Use [`starter/START_HERE.md`](starter/START_HERE.md). It is designed for a non-technical first boot and performs an adaptive whole-life interview before provisioning.

A new user may:

1. fork this public repository into a repository they control, or use a clean audited starter snapshot;
2. connect that repository and only the apps/services they choose;
3. run the `starter/START_HERE.md` prompt;
4. build their own timezone, authorities, schedules, routines, goals, assets, and state from the interview and connected evidence;
5. run source/privacy validation and CI before enabling scheduled writes.

**Do not inherit the reference deployment's Google IDs, schedules, aliases, vehicles, tasks, receipts, or mutable state.** Those are not starter defaults.

Repository visibility for a user's own deployment may be public or private. Public source is supported only when the source audit passes and the owner understands what is intentionally published. Private source follows the same no-secrets rule.

## What LyfeOS can organize

The starter can configure only the domains a user wants, including:

- concise manual/scheduled briefs;
- tasks, projects, next actions, and recurring accountability;
- exercise/fitness routines with component tracking and progression;
- school/study planning, deadlines, road/home study variants, and “what should I do next?” coaching;
- conditional HOME/ROAD/HOME-TRUCK/HOME-FIELD context for people who work away from home;
- orders, shipments, receipts, cancellations, replacements, refunds, active shopping intent, and payment reconciliation;
- assets, fitment, manuals/reference knowledge, warranties, and maintenance evidence;
- Calendar Projection with update-in-place identity;
- household/reimbursement and selected finance workflows;
- searchable recipes and other durable reference material.

Chat is the interface. Canonical connected stores are the state/evidence plane. Git is the durable behavior/recovery plane.

## Repository layout

- `starter/` — sanitized public onboarding/distribution boundary for new users
- `skill/ops-brief-policy/` — current public reference deployment policy and deterministic runtime
- `project/INSTRUCTIONS.md.tmpl` — reference deployment bootstrap contract
- `scripts/` — repository validation, source/privacy audit, bootstrap, fingerprint, and importer tools
- `tests/` — repository and regression tests
- `docs/` — architecture, data model, automation, privacy/recovery, and lifecycle documentation
- `policy/` and `skills/` — legacy compatibility surfaces pointing back to canonical policy

The reference deployment is intentionally public, but it is **not** copied as new-user configuration.

## Reference deployment

The current reference deployment uses one exact-schedule Ops Brief task at 2:45 AM/PM and one consolidated receipt lifecycle task at 1:45 AM/PM in `America/New_York`. Optional Calendar Projection may create/update deduplicated events without creating per-record automations.

A task definition is not proof that scheduling works. Scheduler health requires:

- canonical VEVENT/TZID/local time;
- exactly one intended enabled dispatcher;
- correct timing mode;
- required notifications;
- no active duplicates;
- a subsequent actual firing/canonical Run Log in the intended local slot after creation or repair.

A connector field such as `default_timezone` is authoritative only when the provider contract explicitly defines it as persistent task execution state.

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

CI runs the same coherent checkpoint on pull requests and `main`.

## Source and privacy policy

Public visibility is not an error. **Unintended source data is.**

Never commit:

- passwords, access tokens, private keys, OAuth/client secrets, or credentials;
- full payment-card/account numbers or banking authentication material;
- mutable task/trip/receipt/shipment/account exports;
- Gmail/message bodies or receipt images/files;
- `.env` or local deployment configuration;
- personal information that the repository owner did not deliberately choose to publish.

Google resource IDs and other non-secret reference identifiers may exist in an intentionally public reference deployment, but a new deployment must generate/select its own authorities.

## Reliability rules

- Mutable state lives in canonical connected authorities, never only chat/Git.
- Scheduled prompts remain thin dispatchers and do not mutate their own task definitions.
- Exactly one consolidated task handles each recurring lifecycle; no hidden retry/child/per-order job fan-out.
- Retry is optional/bounded. Repeated/no-progress/ambiguous failure trips the **Pants Filling With Shit Report** circuit breaker, preserves verified state, and stops only the affected module.
- One purchase is one Receipt ID/total. Revisions, replacements, refunds, reimbursements, and shopping intent remain distinct concepts.
- Paid terminal mileage follows each deployment's explicit rule; the current reference deployment uses symmetric terminal-pair paid miles unless an exception is supplied.
- People/assets/retained knowledge use immutable UUID identity.
- Email sending remains approval-gated.
- CI success never substitutes for live provider readback when a feature depends on provider behavior.

## Public distribution and releases

`main` is the public release line only after repository validation, public-source audit, starter privacy audit, deterministic/runtime tests, starter tests, and merge authority pass. Feature branches are development surfaces, not installation targets.

See `starter/VERSIONING.md` for fork/snapshot/update rules and `starter/DEPENDENCIES.md` for provider setup and scheduler integrity.