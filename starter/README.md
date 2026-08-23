# Generic LyfeOS First-Boot Starter

This reusable onboarding kit builds a new user's LyfeOS without copying the reference deployment's mutable state. The normal path is a **personal fork** of the public upstream, followed by adaptive discovery, a bounded provisioning approval, and a verified first-boot Git checkpoint. The human entry point is [`START_HERE.md`](START_HERE.md).

## Public distribution boundary

`starter/` is the portable surface of the public upstream. A user may fork the repository or use an audited snapshot. Public or private deployment source is supported. Secrets and mutable personal records never belong in portable Git source.

The deployment elsewhere in the repository is a public **reference implementation** and example, not new-user configuration.

## Built-in discovery and capabilities

First boot can discover/configure, when useful:

1. concise briefs and prioritized next actions;
2. personal accountability/routines, exercise progression and optional wearable/activity evidence;
3. education/study planning and home/away variants;
4. work/context modes for travel/overnight/field roles;
5. **meal planning**, canonical recipes, grocery/shopping intent and leftover/pantry/freezer workflows;
6. hobbies, recreation, hiking/outdoor preparation, vacations and trip planning;
7. verified appointment/reservation email reconciliation with update-in-place Calendar projection and write readback;
8. orders/receipts/shopping/payment reconciliation;
9. assets/manuals/knowledge, household/reimbursements and optional finance workflows;
10. capability/plugin discovery so existing connected tools are reused before redundant setup is requested.

Accounts, exact schedules, taxonomy, authority IDs, repository visibility and selected features are never inherited.

## First-boot workflow

1. Fork the public upstream or choose an audited snapshot; pin upstream provenance.
2. Ask only the four kickoff questions in `START_HERE.md`.
3. Read `CAPABILITY_DISCOVERY.md` and inspect accessible existing evidence/capabilities before asking the user to recreate information.
4. Conduct `LIFE_INTERVIEW.md` in batches of at most four related questions and skip irrelevant branches.
5. Recommend a Minimum Useful Setup and explain adjacent capabilities the user may not know to request.
6. Verify only dependencies required by selected modules; optional connector failures are module-scoped.
7. Obtain one bounded provisioning approval, create/verify canonical resources and source configuration, then run privacy/source/CI checks.
8. Commit/push and remotely verify the user's first coherent deployment checkpoint.
9. After standing Git authorization, durable personal feature/config/schema changes automatically validate, commit and push.
10. When a coherent personal feature passes tests/privacy/source checks, ask: `Do you want to make this feature available to other people?` A yes starts sanitized upstream contribution preparation; publication is never implicit.
11. Never treat green CI as proof of live scheduler/provider behavior without required readback/observed execution.

## Personal development model

See `PERSONAL_FORK_LIFECYCLE.md` and `SHARED_FEATURE_WORKFLOW.md`.

Recommended personal branches:
- `main` for known-good personal releases;
- optional `experimental` for integrating several concurrent experiments;
- `feature/*` and `fix/*` for bounded work.

This lets users inherit a working foundation, customize it independently, and optionally share portable improvements upstream without exporting their live personal data.

## Boundaries

- Never inherit another user's timezone, schedule, accounts, assets, receipts, authority IDs or mutable records.
- Never claim arbitrary old ChatGPT conversations are globally searchable. Use current/accessibly connected evidence or provide an ingestion path.
- Never create one automation per order, appointment, routine or assignment when Calendar/consolidated dispatch can handle it.
- Same-order revisions remain one transaction; true replacements use linked Receipt IDs.
- Never request/commit passwords, tokens, keys, full card data, private message/receipt bodies, account exports, medical records, school submissions or mutable operational exports.
- Automatic Git push does not imply merge/release/publication/force-push authority.
- Completion comes from the user or reliable connected evidence, never silence.

## Developer/recovery layer

Developers may use `config.example.json`, `INSTRUCTIONS.md.tmpl`, the portable feature manifests under `features/`, and the validation/test tooling. Durable behavior/configuration belongs in versioned source; mutable facts stay in canonical runtime authorities.

See `VERSIONING.md`, `PERSONAL_FORK_LIFECYCLE.md`, `CAPABILITY_DISCOVERY.md`, and `DEPENDENCIES.md`.