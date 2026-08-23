# LyfeOS Starter Versioning and New-User Forks

## Repository roles

- `Matthew-Beare/Daily-Ops-Brief` is the owner's private production/development repository. It is never the default clone source for another user.
- `Life-Ops-Starter` is the planned sanitized upstream containing only portable code, schemas, tests, examples, onboarding, and synthetic fixtures.
- Each new user's fork of `Life-Ops-Starter` becomes that user's private deployment repository.

## What a new user starts from

A new user starts from the **latest stable tagged release of `Life-Ops-Starter`**, not from an arbitrary development branch and not from the owner's production repository.

Release scheme:

- semantic versions: `vMAJOR.MINOR.PATCH`;
- `main` in the starter repository is release-candidate quality but a tag is the stable installation boundary;
- feature/integration branches are never first-boot sources;
- the first starter tag should be created only after the unified core is merged, sanitized, CI-green, privacy-audited, and first-boot tested. Until then, no release version should be advertised as stable.

Examples once releases exist:

- `v0.1.0` — first private beta starter;
- `v0.2.0` — backwards-compatible new modules/onboarding behavior;
- `v0.2.1` — bugfix-only release;
- `v1.0.0` — stable compatibility contract after migrations/upgrade paths are proven.

## Non-technical first boot

The normal user should not need Git CLI knowledge.

1. Open the stable `Life-Ops-Starter` release page.
2. Choose **Fork** and create a **private** fork under the user's own GitHub account.
3. Start ChatGPT with that fork/repository connected.
4. Run `starter/START_HERE.md`.
5. First boot asks the four kickoff questions, offers optional modules, performs harmless connector reads, shows proposed schedules/writes, and establishes one standing private-Git versioning authorization.
6. User-specific data and mutable state are created in that user's own authorities. No production owner's Sheet IDs, Gmail data, schedules, vehicle list, terminal history, receipt IDs, or personal configuration are inherited.

Developer/local-clone users may clone their own fork and check out the stable tag or the deployment branch derived from it, but CLI usage is optional rather than part of ordinary onboarding.

## Deployment version record

Every deployment should persist a small non-secret version record containing:

- `core_version`: starter semantic version;
- `upstream_commit`: exact sanitized upstream commit/tag;
- `schema_version`;
- selected portable feature IDs and exact versions in `features.lock.json`;
- migration version/checksum state;
- local deployment policy version.

Do not put mutable operational records or secrets in the version record.

## Updating a user's fork

Upgrades are deliberate, reviewable changes:

1. fetch/compare the next stable upstream tag;
2. read release notes and migration declarations;
3. run synthetic compatibility tests;
4. apply idempotent migrations to a backup/test copy where required;
5. open/update a deployment PR showing exactly what changes;
6. verify CI and data migrations;
7. merge only with that deployment owner's approval.

Do not silently reset a user's fork to upstream or overwrite private policy/configuration. Shared defaults never trump deployment-specific policy.

## Developing new portable features

Develop reusable features behind a branch/PR in the sanitized starter or copy a proven personal feature into a clean sanitized feature branch. A portable module must satisfy `SHARED_FEATURE_WORKFLOW.md`, the feature-manifest schema, privacy boundaries, and its own tests before a starter release can contain it.

## Production-owner flow

For the owner's current deployment:

1. develop on `integration/lyfeos-unified` or a short-lived feature branch;
2. keep the canonical integration PR to `main` open until tests and deployment parity pass;
3. merge to production `main` only with explicit approval;
4. tag production releases when useful for recovery;
5. extract only sanitized portable behavior into `Life-Ops-Starter` after it works in production;
6. never use another user's fork as the upstream authority for the owner's production system.
