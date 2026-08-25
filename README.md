# MIRA | M.I.R.R.O.R. — Personal Google Beta

**M.I.R.R.O.R.** stands for **Memory, Integration, Reality, Reconciliation, Observation, and Record**. **MIRA** is the **MIRROR Intelligence and Reasoning Assistant**. The deliberately forced acronym is a nod to Dennis E. Taylor's *Bobiverse* books and their fondness for a good forced acronym. M.I.R.R.O.R. is the reality layer and **holds the durable reflection of reality**: the verified state, evidence, relationships, history, and provenance that describe a user's world. MIRA is the intelligence layer that talks with the user, reasons over that reflection, plans, recommends, and carries out approved actions.

With the integrations and authorities a user chooses, M.I.R.R.O.R. can keep a connected record across assets and inventory, finances and reimbursements, calendars and appointments, email, orders, shipments, receipts and refunds, tasks and projects, medications and opt-in reminder schedules, documents and knowledge, travel and work, mileage, meals and groceries, and new domains the user creates. The point is not to dump everything into chat. The point is to maintain durable, queryable reality so MIRA can answer questions and coordinate work across those areas from evidence instead of guesswork.

> **Magic MIRA on the wall...**

## Start here

Non-technical users start with [`starter/QUICK_START.md`](starter/QUICK_START.md). It explains Git and GitHub in plain language and requires no command prompt, terminal, local Git client, token, SSH key, or code editor.

[`starter/INSTALL.md`](starter/INSTALL.md) is the detailed browser-only reference for capability gates and troubleshooting. [`starter/START_HERE.md`](starter/START_HERE.md) is the deeper first-boot interview contract. The default system name is **M.I.R.R.O.R.** and the default assistant is **MIRA**; a user does not have to invent either name.

## Build and share new skills

M.I.R.R.O.R. is designed to grow with the user. A non-technical user can describe a recurring problem to MIRA in ordinary language, for example: `Design a skill that tracks maintenance for my equipment and reminds me when service is due.`

MIRA should then:

1. inspect existing capabilities first so it does not build a duplicate;
2. define the behavior, required evidence, state authority, permissions, connectors, failure behavior, and success criteria;
3. create the work on a feature branch and keep reusable behavior separate from private user data;
4. add or update configuration, schemas or migrations, tests, and synthetic fixtures as needed;
5. test the skill against synthetic fixtures and the user's verified interfaces, then commit and push a coherent checkpoint;
6. keep the skill private by default; and
7. when it is coherent, ask exactly: **Do you want to make this feature available to other people?**

If the answer is **no**, the skill stays personal. If the answer is **yes**, MIRA must remove personal identifiers and provider-specific secrets, replace live data with synthetic fixtures, declare dependencies and permissions, run the privacy/source/feature tests, show the user the exact public diff, and only then create a sanitized contribution branch and upstream pull request under explicit publication approval.

The full contract is in [`starter/SHARED_FEATURE_WORKFLOW.md`](starter/SHARED_FEATURE_WORKFLOW.md).

## Architecture

Git or another approved managed source stores versioned behavior: policy, schemas, migrations, tests, onboarding, non-secret configuration, and reusable feature code. Mutable operational state does not live only in chat or Git. It lives in the selected canonical state authority, with retained evidence in the selected evidence store when needed.

Personal Google currently uses Google Sheets and Google Drive plus optional Gmail/Calendar capabilities when verified. Microsoft 365, Apple/manual portability, Claude, Gemini, and institutional runtimes are capability-checked rather than assumed to have identical integrations.

The portable source contains no credentials, live authority IDs, private receipt or email bodies, medical records, or mutable personal exports.

## Release channels

All three onboarding repositories are public and use one portable code line:

- **M.I.R.R.O.R. Personal-Production** — public canonical source;
- **M.I.R.R.O.R. Personal-Experimental** — public sanitised personal experimental distribution; and
- **M.I.R.R.O.R. Institutional-Experimental** — public sanitised institutional experimental distribution containing no live regulated or operational data.

All channels consume the **same portable application code from the same canonical source revision**. Channel differences are limited to approved deployment policy, provider/runtime configuration, data classification, and external mutable state. There are no channel-specific feature forks.

Repository identifiers use punctuation-safe names such as `MIRA-Personal-Production`; the human-facing system brand is **M.I.R.R.O.R.**

## Reliability rules

- MIRA reasons from M.I.R.R.O.R.'s verified state; guesses never silently become reality.
- One canonical authority owns each mutable data class.
- Important provider writes require readback before success is reported.
- Email sending remains approval-gated.
- Optional connector failures degrade only the dependent module.
- Recurring work uses consolidated scheduling rather than one task per order, appointment, or chore.
- A manual actual-brief smoke test can exercise the real brief pipeline at any time without claiming that the 2:45 scheduler fired.
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
