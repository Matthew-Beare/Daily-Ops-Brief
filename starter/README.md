# Generic LyfeOS First-Boot Starter

This reusable onboarding kit builds a new user's LyfeOS without copying the reference deployment's mutable state. The normal path is a **private personal Git lineage** seeded from the public upstream, followed by adaptive discovery, a bounded provisioning approval, and a verified first-boot Git state checkpoint. The human entry point is [`START_HERE.md`](START_HERE.md).

## Public upstream vs private personal deployment

`starter/` is the portable surface of the public upstream. The public upstream stays public so people can inherit, inspect, improve, and redistribute portable behavior.

A normal user deployment stores personal mutable state in Git, so its repository must be **private before personal-state writes are enabled**. A standard GitHub fork of a public repository is public, so the safe default is to seed a new private user-owned repository from a pinned audited upstream release/commit/tree and record upstream provenance.

The deployment elsewhere in this repository is a public **reference implementation** with its own established external state authorities. That is an exception, not new-user storage policy.

Read `GIT_STATE_MODEL.md` for the canonical starter state model.

## Built-in discovery and capabilities

First boot can discover/configure, when useful:

1. concise briefs and prioritized next actions;
2. personal accountability/routines, exercise progression, hiking/outdoor activity, and optional wearable evidence;
3. education/study planning and context variants;
4. working/retired/other life-pattern discovery plus conditional work-away modes;
5. **meal planning**, canonical recipes, grocery/shopping intent, and leftover/pantry/freezer workflows;
6. hobbies, recreation, vacations, hiking/trip planning, and travel logistics;
7. verified appointment/reservation email reconciliation with update-in-place Calendar projection plus Git state readback;
8. orders/receipts/shopping/payment reconciliation;
9. assets/manuals/knowledge, household/reimbursements, and optional finance evidence;
10. capability/plugin discovery so existing connected tools are reused before redundant setup is requested.

Accounts, exact schedules, taxonomy, provider IDs, and selected features are never inherited from another deployment.

## First-boot workflow

1. Pin an audited public upstream release/commit/tree.
2. Create/connect a private user-owned deployment repository and record upstream provenance.
3. Ask only the four kickoff questions in `START_HERE.md`.
4. Read `CAPABILITY_DISCOVERY.md` and inspect accessible existing evidence/capabilities before asking the user to recreate information.
5. Conduct `LIFE_INTERVIEW.md` in batches of at most four related questions and skip irrelevant branches.
6. Recommend a Minimum Useful Setup and adjacent capabilities the user may not know to request.
7. Verify only dependencies required by selected modules; optional connector failures are module-scoped.
8. Obtain one bounded provisioning approval and create the initial Git event/snapshot state, configuration, features, and policy.
9. Validate, commit, push, and remotely read back the first coherent deployment checkpoint.
10. After standing Git authorization, each coherent personal state or behavior change automatically validates, commits, pushes, and reads back.
11. When a coherent personal feature passes tests/privacy/source checks, ask exactly: `Do you want to make this feature available to other people?` A yes starts sanitized upstream contribution preparation; publication is never implicit.
12. Never treat green CI as proof of live scheduler/provider behavior without required readback/observed execution.

## Personal development model

Recommended branches:
- `main` for known-good personal state + behavior;
- optional `experimental` for integrating concurrent behavior experiments;
- `feature/*` and `fix/*` for bounded work.

Canonical state changes use small Git transactions on the configured state branch. Feature branches do not become shadow state stores.

## State and evidence boundary

Private Git is the canonical LyfeOS personal-state authority. Optional providers are adapters:

- email supplies evidence;
- Calendar supplies projection/reminders;
- fitness/wearables supply optional evidence;
- finance supplies optional transaction evidence;
- Drive/files may hold bulky originals;
- maps/weather/travel tools provide current planning inputs.

Accepted operational state and stable provider references commit into Git. Provider credentials never do.

## Boundaries

- Never inherit another user's timezone, schedule, accounts, assets, receipts, IDs, or mutable state.
- Never claim arbitrary old ChatGPT conversations are globally searchable. Use current/accessibly connected evidence or provide an ingestion path into Git state.
- Never create one automation per order, appointment, routine, or assignment when Calendar/consolidated dispatch can handle it.
- Same-order revisions remain one transaction; true replacements use linked Receipt IDs.
- Never request/commit passwords, tokens, keys, full card/bank authentication data, or information the user explicitly excludes from Git.
- Never include `state/` or private deployment material in an upstream feature contribution.
- Automatic Git push does not imply merge/release/publication/force-push authority.
- Completion comes from the user or reliable connected evidence, never silence.

## Developer/recovery layer

Developers may use `config.example.json`, `INSTRUCTIONS.md.tmpl`, `GIT_STATE_MODEL.md`, portable feature manifests under `features/`, and validation/test tooling. A fresh conversation should recover from the private personal repository plus selected provider connections, without needing old chats.

See `VERSIONING.md`, `PERSONAL_FORK_LIFECYCLE.md`, `GIT_STATE_MODEL.md`, `CAPABILITY_DISCOVERY.md`, and `DEPENDENCIES.md`.