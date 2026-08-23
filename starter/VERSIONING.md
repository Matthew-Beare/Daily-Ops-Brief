# LyfeOS Starter Versioning and New-User Deployments

## Repository roles

- A production deployment repository is one owner's private policy/development repository. It is never the default clone/fork source for another user.
- `Life-Ops-Starter` is the planned standalone sanitized upstream containing only portable code, schemas, tests, examples, onboarding, and synthetic fixtures.
- Each new user's deployment gets its own brand-new private policy/deployment repository.

## Current pre-release reality

The standalone `Life-Ops-Starter` repository does **not** yet exist. Until it exists and has a privacy-audited tagged release, no document may pretend a stable starter tag is available.

For the first private beta user:

1. choose one exact audited commit of the current development repository whose `starter/` tree has passed repository validation, starter privacy audit, starter tests and whole-repository tests;
2. export/copy only the sanitized starter/portable files intended for distribution, not the production repository's `.git` history, production policy tree, mutable-state snapshots, authority IDs, personal docs, issues, pull-request history or deployment-specific configuration;
3. create a **brand-new private** repository owned by the new user;
4. verify provider metadata reports the target repository is actually private before pushing anything;
5. populate that repository from the pinned privacy-audited sanitized snapshot;
6. run the starter privacy audit and complete CI again in the new private repository before first boot;
7. record the pinned source commit/snapshot identity as beta provenance.

Do not fork or clone another person's production repository/history for a new deployment. Sanitization of the working tree is not enough if private material remains reachable in Git history.

## Stable path once the standalone starter exists

After the standalone sanitized `Life-Ops-Starter` repository is provisioned and audited, a new user starts from its latest stable tagged release in a private repository, never from an arbitrary development branch or another person's production repository/history.

Release scheme:

- semantic versions: `vMAJOR.MINOR.PATCH`;
- `main` in the standalone starter is release-candidate quality; a tag is the stable installation boundary;
- feature/integration branches are never first-boot sources;
- the first stable tag is created only after the core is sanitized, CI-green, privacy-audited, and first-boot tested from an isolated/empty deployment.

Recommended milestones:

- `v0.1.0-beta.1` — first private standalone-starter onboarding beta after privacy audit and synthetic/isolated first-boot pass;
- `v0.1.0` — first stable private starter after at least one clean deployment from an empty account/workspace;
- `v0.2.0` — backwards-compatible new modules/onboarding behavior;
- `v0.2.1` — bugfix-only release;
- `v1.0.0` — stable compatibility contract after migrations/upgrade paths are proven.

## Non-technical first boot

The normal user should not need Git CLI knowledge or manually design databases.

1. Start from either the audited pinned-snapshot beta process above or, once available, a stable standalone `Life-Ops-Starter` release in a private Git repository owned by the user.
2. Verify the target repository is actually private from provider metadata.
3. Connect that repository and whichever Drive/Sheets/Docs/Gmail/Calendar/finance services the user wants LifeOS to use.
4. Run `starter/START_HERE.md`.
5. First boot asks the four kickoff questions, performs the adaptive whole-life interview, offers optional modules, performs harmless connector reads, shows a concise private-resource provisioning plan, and requests one bounded approval for initial creation.
6. After approval, setup creates or validates the user's canonical resources, writes sanitized policy/schema/tests/bootstrap to the private repository, and verifies remote/readback state.
7. Establish one standing private-Git versioning authorization for later durable source changes.
8. User-specific mutable data remains only in that user's selected live authorities. No other deployment's Sheet IDs, Gmail data, schedules, asset list, receipt IDs, aliases, financial data, or personal configuration are inherited.

The user may understand the result without understanding Git branches, schema migrations, table normalization, or formulas. Hidden implementation complexity is acceptable; hidden external permissions or unapproved destructive actions are not.

## Deployment version record

Every deployment should persist a small non-secret version record containing:

- `core_version`: starter semantic version, or an explicit pre-release beta/snapshot identifier before stable tags exist;
- `upstream_commit`: exact sanitized upstream commit/tag or pinned snapshot source commit;
- `schema_version`;
- selected portable feature IDs and exact versions in `features.lock.json`;
- migration version/checksum state;
- local deployment policy version.

Do not put mutable operational records or secrets in the version record.

## Updating a user's deployment

Upgrades are deliberate, reviewable changes:

1. fetch/compare the next audited snapshot or stable upstream tag;
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
2. keep the integration PR closed/draft or otherwise isolated while a multi-file checkpoint is incomplete so CI does not validate half-applied policy;
3. open/ready the integration PR only when the checkpoint is coherent;
4. merge to production only under that deployment's merge policy;
5. tag production releases when useful for recovery;
6. extract only sanitized portable behavior into the standalone `Life-Ops-Starter` after it works in production;
7. never use another user's private deployment as automatic upstream authority.