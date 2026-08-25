# MIRA | MIRROR — Personal Google Beta

**MIRROR is the reality layer. MIRA is the intelligence layer.**

MIRROR holds the durable picture of reality: memory, integrations, evidence, the Reality Record, reconciliation, and provenance. MIRA is the default assistant that talks to the user, reasons over that evidence, plans, recommends, and executes approved actions.

The public relationship is simple:

- **MIRA is the assistant.**
- **MIRROR is the system.**
- Signature line: **MIRA, MIRROR on the wall...**

The current `Matthew-Beare/Daily-Ops-Brief` repository remains the observed public beta source and browser template while the branded release repositories are prepared. The former public label **Life Planner — Personal Google Beta** and the internal `life-planner` package name remain compatibility identifiers during bounded migration. The separate repositories are not live yet, so onboarding must not send a user to a dead repository.

## Start here

Non-technical users start with [`starter/QUICK_START.md`](starter/QUICK_START.md). It explains Git and GitHub in plain language and requires no command prompt, terminal, local Git client, token, SSH key, or code editor.

[`starter/INSTALL.md`](starter/INSTALL.md) is the detailed browser-only reference for capability gates and troubleshooting. [`starter/START_HERE.md`](starter/START_HERE.md) remains the detailed interview contract. New onboarding must apply the MIRA/MIRROR defaults before reading legacy questions: the system name is MIRROR, the assistant name is MIRA, and the user is not asked to invent either unless they explicitly want a private alias.

## Architecture

Git or another approved managed source stores versioned behavior: policy, schemas, migrations, tests, onboarding, non-secret configuration, and reusable feature code. Mutable operational state does not live only in chat or Git. It lives in the selected canonical state authority, with retained evidence in the selected evidence store when needed.

Personal Google currently uses Google Sheets and Google Drive plus optional Gmail/Calendar capabilities when verified. The reference deployment already follows this external-authority model; new users inherit portable behavior, not its private accounts, IDs, schedules, or state. Microsoft 365, Apple/manual portability, Claude, Gemini, and institutional runtimes have no assumed feature parity and must be capability-checked.

The repository contains no mutable operational state, credentials, live authority IDs, private receipt bodies, medical records, or personal exports in the portable source.

## Release channels

The intended branded topology is:

- **MIRROR Personal-Production**: private canonical source.
- **MIRROR Personal-Experimental**: public sanitised browser-first personal template.
- **MIRROR Institutional-Experimental**: private sanitised source/configuration for approved institutional pilots.

All three consume the **same portable application code from the same canonical source revision**. Channel differences are visibility, approved deployment policy, provider/runtime configuration, data classification, and external mutable state. There are no channel-specific feature forks.

Until the branded repositories are created and remotely verified, the legacy planned repository identifiers `Life-Planner-Public-Experimental` and `Life-Planner-Institutional-Experimental` remain compatibility metadata only. See [`distribution/README.md`](distribution/README.md).

## Reliability rules

- MIRA reasons from MIRROR's verified state; guesses never silently become reality.
- One canonical authority owns each mutable data class.
- Important provider writes require readback before success is reported.
- Email sending remains approval-gated.
- Optional connector failures degrade only the dependent module.
- Recurring work uses consolidated scheduling rather than one task per order, appointment, or chore.
- Green CI proves source integrity, not live provider behavior or an actual scheduled firing.

## Validate

```bash
python3 scripts/validate_repo.py .
python3 scripts/feature_catalog.py --check
python3 scripts/audit_public_source.py . --history
python3 scripts/audit_starter_privacy.py starter
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skill/ops-brief-policy/scripts -p 'test_*.py'
python3 starter/tools/validate_feature_manifest.py --check-files
python3 -m unittest discover -s starter/tests -p 'test_*.py'
```

The current `Daily-Ops-Brief` public beta source remains the canonical observed source for this beta until the branded repository migration is completed with remote readback and green CI.
