# Daily Ops Brief

Daily Ops Brief is a version-controlled control-room policy for two concise daily briefings, persistent task capture, shipment reconciliation, ROAD/HOME mode, route and mileage state, and the LyfeOS purchase lifecycle.

The current deployment uses **one exact-schedule Ops Brief task** at 2:45 AM/PM and **one exact-schedule consolidated receipt lifecycle task** at 1:45 AM/PM in `America/New_York`. No purchase gets its own scheduled task. Optional Calendar Projection may create or update a deduplicated delivery event without creating another automation. Mutable state stays in the live Google Sheets; the repository holds policy, deterministic code, tests, templates, and recovery instructions.

## Current deployment

- Policy skill: `skill/ops-brief-policy`
- Project bootstrap contract: `project/INSTRUCTIONS.md.tmpl`
- Ops state: live Ops Status Register Google Sheet
- Mileage state: live Mileage & Pay Tracker Google Sheet
- Receipt evidence: Gmail plus the Drive receipt archive
- Purchase state: normalized Purchase & Receipt Archive with an integrity gate
- Scheduled entry points: one brief dispatcher and one consolidated receipt lifecycle task
- Repository state: policy and templates only; no copied task, route, trip, shipment, or mileage database

Canonical task fields:

```text
Title: 2:45 AM/PM Eastern Ops Brief
Prompt: Use $ops-brief-policy to run the Daily Ops Brief for the current America/New_York slot. Use AM before noon and PM at or after noon; the PM brief is my morning brief. Return only the brief.
Schedule: RRULE:FREQ=DAILY;BYHOUR=2,14;BYMINUTE=45;BYSECOND=0
Timezone: America/New_York
```

The task definition is not sufficient proof that scheduling works. A scheduler incident clears only after task readback confirms title/enabled/cadence/TZID/timing/notification/duplicate state and a subsequent actual firing or canonical Run Log entry lands in the intended New York slot. Connector metadata such as `default_timezone` is authoritative only when the provider contract explicitly defines it as persistent execution state.

## Repository map

- `skill/ops-brief-policy/` — canonical installed policy, deterministic engine, references, and tests
- `project/INSTRUCTIONS.md.tmpl` — complete user-specific Project instructions replacement
- `starter/` — separate generic first-boot kit for a new user
- `scripts/` — policy fingerprinting, starter rendering, and repository validation
- `tests/` — starter and repository-contract tests
- `docs/` — architecture, automation, Drive, privacy/recovery, and receipt-pipeline notes
- `policy/ops-brief-policy.yaml` — retained legacy machine-readable compatibility snapshot
- `skills/ops-brief-policy/SKILL.md` — retained legacy path pointing to the canonical `skill/` tree
- `tests/ops-brief-regressions.md` — retained human regression index pointing to executable tests

The three legacy compatibility paths above preserve old links without creating a second policy authority. Canonical behavior lives under `skill/ops-brief-policy/` and wins on divergence.

## Validate

```bash
python3 scripts/validate_repo.py .
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skill/ops-brief-policy/scripts -p 'test_*.py'
```

Validation also verifies the Git-side policy fingerprint against the checked-in canonical skill.

## Generic first boot

The `starter/` directory is intentionally separate from the current user's deployment. Its human entry point is `starter/START_HERE.md`. First boot supports configurable briefs, consolidated order notifications/lifecycle, a searchable collapsible recipe library, a job-routed per-user HOME/ROAD layer for recurring travel roles, whole-life planning/accountability, and a mandatory private-Git recovery checkpoint. It asks the new user's authoritative timezone, exact local cadence, and notification mode instead of inheriting this deployment's schedule.

A new deployment must use its own private repository. Before provisioning, verify provider metadata shows the target deployment repository is actually private. A repository merely described as private in documentation is not sufficient. If the repository is public, stop provisioning until visibility is corrected.

Until a standalone sanitized `Life-Ops-Starter` release exists, do not fork this production repository for a new user. Use a pinned, privacy-audited sanitized starter snapshot to populate a brand-new private deployment repository, then verify the target repository and run starter CI/privacy checks there.

For a new user, start with the audited starter material only after the private-repository gate passes:

```text
Open starter/START_HERE.md and paste its first-boot prompt into a new ChatGPT Project or conversation.
```

The JSON/template path remains available as the deterministic developer and recovery layer after the human setup is settled:

```bash
cp starter/config.example.json starter/config.local.json
python3 scripts/bootstrap.py \
  --config starter/config.local.json \
  --template starter/INSTRUCTIONS.md.tmpl \
  --output starter/INSTRUCTIONS.rendered.md
```

Do not commit `config.local.json` or a rendered file containing private identifiers.

## Design rules

1. Keep mutable operational state in one authoritative live system.
2. Keep scheduled prompts tiny; route execution into the skill.
3. Read complete evidence before changing state.
4. Commit downstream records before archiving source email.
5. Update existing scheduled tasks in place when possible and preserve notification capability during scheduler surgery.
6. Treat private-device access as a separate integration problem; a cloud task cannot silently reach an unconnected local device.
7. After standing authorization, automatically validate, commit, push, and remotely verify every lasting policy/schema/workflow/onboarding change; never wait for another Git prompt.
8. Treat one purchase as one stable transaction with many tags/links, never duplicated spend.
9. Block Gmail archival when the cross-system Audit gate fails.
10. Keep user-facing Drive navigation native and readable; raw HTML/JSON/Markdown artifacts belong only in backups or developer sources.
11. Preserve true replacement orders as distinct, bidirectionally linked Receipt IDs; same-order revisions remain one Receipt ID.
12. Automatic push never means auto-merge, public publishing, or committing mutable data/secrets.
13. Repository privacy is a provider-state invariant, not a prose claim. Production and per-user deployment repositories must remain private unless a separate explicit publication decision is made after history/privacy review.

## Security

This repository **must be private** because deployment-specific policy may contain authority identifiers and other operational metadata. Before treating a deployment as healthy, verify repository provider metadata reports private visibility. Regardless of visibility, never commit passwords, access tokens, full card numbers, private keys, Gmail bodies, receipts, or mutable operational exports. Connected-app credentials remain with the connector platform. Receipt records should retain only transaction data needed for evidence and reconciliation.