# Shared Life-Ops Feature Workflow

## Decision

Keep each person's production deployment private and independent. Do not refactor, simplify, or weaken one deployment merely to accommodate another user. Create and maintain a sanitized forkable upstream for portable core and feature modules; extract working personal features into that portable boundary only after privacy review.

| Repository | Contents | Access |
|---|---|---|
| Production deployment | One owner's complete policy, private configuration boundary, and deployment | Owner controls access |
| `Life-Ops-Starter` | Sanitized forkable base, portable feature modules, schemas, tests, examples and stable releases | Private first; broader sharing only after audit |
| New user's fork | Their independently customized policy, selected features, private configuration, and deployment | Fork owner controls access |

Start `Life-Ops-Starter` private. It may become public only after an explicit history and privacy audit. Forks and personal deployment repositories remain independent.

## Non-compromise invariant

- Production behaviour never changes merely to make a feature portable or easier for another user.
- Shared defaults never override a deployment owner's private policy, configuration, schemas, schedules, or live state.
- No shared feature is imported into another deployment automatically. Adoption requires an explicit reviewed change in that target repository.
- If extraction would destabilize production, copy and sanitize the useful behavior into the starter rather than refactoring production in place.
- A user may rewrite their fork freely. Those commits affect another person's deployment only if that owner deliberately imports or accepts the feature.

## Why branches are not user separation

A collaborator on a personal private repository receives write access and can see repository branches and history. Branches isolate development work; they do not conceal one user's configuration/history from another collaborator. A fork gives each user an independent repository, while feature branches inside that fork isolate each piece of development.

A new user should fork the sanitized starter, not another person's production deployment, unless that production owner explicitly decides that exposing its full repository and history is acceptable.

## Portable feature boundary

A shared feature must be self-contained under `features/<feature-id>/` and include:

```text
features/<feature-id>/
├── feature.json
├── FEATURE.md
├── references/
├── scripts/
├── schemas/
├── migrations/
└── tests/
```

Only directories the feature actually needs should exist. The manifest is validated against `schemas/feature-manifest.schema.json`.

A portable feature contains behaviour, schemas, placeholders, synthetic fixtures, and tests. It must not contain real personal data, mutable operational state, credentials/secrets, private work records, or user-specific assumptions that are not configuration.

Real values live in each deployment's ignored local configuration and operational databases. Committed example profiles contain placeholders only.

## Feature contract

Every `feature.json` declares manifest and feature version, stable feature ID/purpose, compatible core version, dependencies, scripts/references/schemas/migrations/tests, connector/network/write permissions, runtime data boundaries, forbidden source data, per-user configuration schema, portability, and whether source contains personal data.

Build tooling discovers manifests; do not maintain a conflict-prone handwritten central registry.

## Git workflow

1. Open an issue describing the user problem, not a predetermined implementation.
2. Create a feature/fix branch in the user's own repository.
3. Keep feature implementation in its own directory; identify core-interface changes clearly.
4. Use atomic Conventional Commit messages.
5. Add synthetic acceptance fixtures and failure cases.
6. Validate the feature inside the originating deployment without copying mutable personal data into source.
7. Extract/sanitize the portable module and open a draft pull request to the sanitized starter upstream, or publish a sanitized feature-only repository when independent distribution is more appropriate.
8. Merge upstream only after CI passes and no personal data appears in the diff or reachable feature history.
9. Tag portable releases using semantic versions.

## Bidirectional feature exchange

Features are allowed to originate in any user's private fork. The contribution graph is intentionally many-to-many, not “central owner writes everything.”

- An originating user commits a useful feature in their own Git repository with tests and a stable feature ID.
- Before anyone else imports it, portable behavior is separated from personal state and reviewed for secrets/private data.
- Another deployment owner may review and import that exact sanitized feature release/commit without importing the origin user's entire branch or repository history.
- If the receiving owner improves it, the improvement remains a normal Git commit in that owner's repository. The portable delta can then be contributed back to the starter/upstream feature or to the original feature repository through a pull request.
- The original user can subsequently upgrade to that improved release through the same reviewed import path. No deployment silently overwrites another deployment.
- Keep authorship/source provenance at the Git commit/release level and in `features.lock.json`: feature ID, version, source repository/release, source commit/checksum, installed commit, and migration version. Do not put personal runtime data into provenance.

This supports the intended loop: user creates feature → commits/tests it → another user deliberately imports it → improves it → contributes portable improvements upstream → original user can deliberately pull the improved version.

## Moving a feature between deployments

Version 1 uses module-only commits and deliberate imports:

1. Develop and validate the portable module in a private fork or sanitized feature branch.
2. Record feature ID, semantic version, source release/commit/checksum in `features.lock.json`.
3. Import only the module commit/release into a target deployment.
4. Supply private configuration locally and run synthetic tests before enabling writes.
5. Apply migrations transactionally and verify the target database.
6. Record the target's installed commit/migration so the next update can produce a deterministic diff.

Do not copy an entire personal branch into another person's repository. If a useful feature originates in a personal deployment, first extract/sanitize behavior, add tests, review diff/history, then import only the shared feature release where wanted.

Once several modules exist, replace manual import with a deterministic `sync_features` tool that reads `features.lock.json`, verifies repositories/source commits/checksums, installs only selected modules, shows the migration/permission delta, and refuses dirty, incompatible, or privacy-unsafe upgrades.

## Compatibility and ownership

- Use semantic versions for core and every feature.
- Breaking manifest/schema/state migrations increment the major version.
- Migrations are idempotent, versioned, and reversible when practical.
- Each deployment pins exact feature versions; upgrades are explicit pull requests.
- User-specific policy overrides shared defaults inside that user's private deployment.
- Shared defaults must be conservative: no destructive write, external message, email deletion, workplace-data access, or unbounded monitoring without explicit configuration and approval.
- A feature can depend on another feature, but its manifest must declare the dependency and compatible version range instead of relying on accidental files in one user's fork.

## New-user onboarding

1. New users get their own private deployment repository derived from a sanitized stable starter release, not access to somebody else's production history.
2. Run `START_HERE.md` in their deployment and store real configuration only there.
3. Pin the starter/core release and every selected feature version before enabling scheduled writes.
4. Extract genuinely portable improvements back through reviewed feature modules rather than sharing private deployment branches.

This gives users a common engineering surface without turning one person's life into another person's Git history.
