# LyfeOS Starter Versioning and New-User Forks

## Repository roles

- A production deployment repository is one owner's private policy/development repository. It is never the default clone source for another user.
- `Life-Ops-Starter` is the sanitized upstream containing only portable code, schemas, tests, examples, onboarding, and synthetic fixtures.
- Each new user's private fork/deployment of `Life-Ops-Starter` becomes that user's independent policy/deployment repository.

## What a new user starts from

A new user starts from the **latest stable tagged release of `Life-Ops-Starter`**, not from an arbitrary development branch and never from another person's production repository/history.

Release scheme:

- semantic versions: `vMAJOR.MINOR.PATCH`;
- `main` in the starter repository is release-candidate quality but a tag is the stable installation boundary;
- feature/integration branches are never first-boot sources;
- the first starter tag should be created only after the core is merged, sanitized, CI-green, privacy-audited, and first-boot tested.

Recommended milestones:

- `v0.1.0-beta.1` — first private onboarding beta after privacy audit and synthetic first-boot pass;
- `v0.1.0` — first stable private starter after at least one clean deployment from an empty account/workspace;
- `v0.2.0` — backwards-compatible new modules/onboarding behavior;
- `v0.2.1` — bugfix-only release;
- `v1.0.0` — stable compatibility contract after migrations/upgrade paths are proven.

## Non-technical first boot

The normal user should not need Git CLI knowledge or manually design databases.

1. Start from a stable `Life-Ops-Starter` release in a private Git repository owned by the user.
2. Connect that repository and whichever Drive/Sheets/Docs/Gmail/Calendar/finance services the user wants LifeOS to use.
3. Run `starter/START_HERE.md`.
4. First boot asks the four kickoff questions, offers optional modules, performs harmless connector reads, shows a concise private-resource provisioning plan, and requests one bounded approval for initial creation.
5. After approval, setup creates or validates the user's canonical Sheets/Docs/folders/tables, writes sanitized policy/schema/tests/bootstrap to the private repository, and verifies remote/readback state.
6. Establish one standing private-Git versioning authorization for later durable source changes.
7. User-specific mutable data remains only in that user's selected live authorities. No other deployment's Sheet IDs, Gmail data, schedules, asset list, receipt IDs, aliases, financial data, or personal configuration are inherited.

The user may understand the result without understanding Git branches, schema migrations, table normalization, or formulas. Hidden implementation complexity is acceptable; hidden external permissions or unapproved destructive actions are not.

## Deployment version record

Every deployment should persist a small non-secret version record containing:

- `core_version`: starter semantic version;
- `upstream_commit`: exact sanitized upstream commit/tag;
- `schema_version`;
- selected portable feature IDs and exact versions in `features.lock.json`;
- migration version/checksum state;
- local deployment policy version.

Do not put mutable operational records or secrets in the version record.

## Updating a user's deployment

Upgrades are deliberate, reviewable changes:

1. fetch/compare the next stable upstream tag;
2. read release notes and migration declarations;
3. run synthetic compatibility tests;
4. apply idempotent migrations to a backup/test copy where required;
5. open/update a deployment PR showing exactly what changes;
6. verify CI and data migrations;
7. merge only with that deployment owner's approval or standing merge policy.

Do not silently reset a user's deployment to upstream or overwrite private policy/configuration. Shared defaults never trump deployment-specific policy.

## Developing new portable features

Develop reusable features behind a branch/PR in the sanitized starter or copy a proven personal feature into a clean sanitized feature branch. A portable module must satisfy `SHARED_FEATURE_WORKFLOW.md`, the feature-manifest schema, privacy boundaries, and its own tests before a starter release can contain it.

Features may originate in any private deployment. Portable behavior is sanitized and versioned; personal state is never used as the feature distribution mechanism.

## Production deployment flow

For any production deployment:

1. develop on a short-lived feature branch;
2. keep the integration PR open until tests and deployment parity pass;
3. merge to production only under that deployment's merge policy;
4. tag production releases when useful for recovery;
5. extract only sanitized portable behavior into `Life-Ops-Starter` after it works in production;
6. never use another user's private fork as automatic upstream authority.
