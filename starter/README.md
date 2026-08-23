# Generic LyfeOS First-Boot Starter

This reusable onboarding kit builds a new user's LyfeOS without copying the reference deployment's data, schedules, accounts, assets, or mutable state. The human entry point is [`START_HERE.md`](START_HERE.md); JSON, templates, tests, and Git stay behind the interface.

## Public distribution boundary

`starter/` is the sanitized portable surface of the public upstream repository. A new user may fork the repository or copy an audited starter snapshot into a repository they control. Public or private deployment source is supported. In either case, secrets and mutable personal records never belong in Git.

The current deployment elsewhere in the repository is a public reference implementation, not default configuration for a new user.

## Stock capabilities

First boot can configure, when useful:

1. concise manual and scheduled briefs;
2. one consolidated order/receipt lifecycle with shipment, delivery, exception, cancellation, replacement, return, refund, shopping-intent, and payment-reconciliation behavior;
3. a searchable recipe/knowledge surface;
4. conditional HOME/ROAD-style context for driving/travel/overnight/field roles;
5. personal accountability/routines such as exercise and progression tracking;
6. education/study planning, next-action selection, and home/away study variants;
7. optional assets/manuals, Calendar Projection, household/reimbursement, and finance-related modules.

Accounts, exact schedules, notification mode, taxonomy, repository visibility, and selected features are never inherited.

## First-boot workflow

1. Ask only the four kickoff questions in `START_HERE.md`.
2. Conduct the adaptive whole-life interview in small batches from `LIFE_INTERVIEW.md` and `questions.json`.
3. Recommend a Minimum Useful Setup and show a manual sample before scheduled writes.
4. Verify selected email, calendar, Drive/Sheets, GitHub, financial, and task dependencies with harmless reads.
5. Record whether the user's Git repository is public or private. Public source must pass the public-source audit.
6. Agree on one mutable-state authority and the smallest useful evidence/document hierarchy.
7. Inspect existing scheduled tasks, show exact schedules/prompts, and obtain explicit approval for the initial automation mutations.
8. Provision idempotently, verify every write/readback, and keep scheduled prompts as thin dispatchers.
9. After standing Git authorization, automatically validate, commit, push, and remotely verify lasting source changes without repeated Git questions.
10. Never treat green CI as proof of a scheduler repair until the next actual canonical-time firing/Run Log is observed.

## Boundaries

- Never inherit another user's timezone, schedule, mode state, accounts, aliases, assets, receipt history, authority IDs, or mutable records.
- Never create one automation per order, routine, assignment, or calendar item when a dispatcher can resolve due state.
- Same-order revisions remain one transaction; true replacements use linked Receipt IDs.
- Never request or commit passwords, tokens, keys, full card data, Gmail bodies, receipts, account exports, or mutable operational data.
- Automatic Git push does not imply merge/release/force-push authority unless the repository owner explicitly grants it.
- A cloud task cannot reach an unconnected private device or LAN service without an authorized bridge.
- User-facing Drive navigation stays native/readable rather than raw developer artifacts.
- Completion of exercise, study, tasks, or orders must come from user confirmation or connected evidence, never silence.

## Developer/recovery layer

A developer may copy `config.example.json` to untracked `config.local.json` and render `INSTRUCTIONS.md.tmpl` with `scripts/bootstrap.py`. Durable facts belong in policy/schema/tests; mutable facts stay in the authoritative state store.

See `VERSIONING.md` for public fork/snapshot/release rules and `DEPENDENCIES.md` for provider setup and scheduler integrity.