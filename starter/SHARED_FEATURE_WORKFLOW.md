# Shared Life-Ops Feature Workflow

## Decision

Keep the existing `Daily-Ops-Brief` as its owner’s canonical private deployment. Do not refactor, simplify, or weaken it to accommodate another user. Create a sanitized forkable upstream only when working features are extracted cleanly.

| Repository | Contents | Access |
|---|---|---|
| `Daily-Ops-Brief` | Owner’s complete production policy, private configuration boundary, and deployment | Owner only unless explicitly changed |
| `Life-Ops-Starter` | Sanitized forkable base, portable feature modules, schemas, tests, and examples | Invited collaborators; possibly public only after audit |
| New user’s fork | Their independently customized policy, selected features, private configuration, and deployment | Fork owner controls access |

Start `Life-Ops-Starter` private. It may become public only after an explicit history and privacy audit. Forks and personal deployment repositories remain independent.

## Non-compromise invariant

- Production behaviour never changes merely to make a feature portable or easier for another user.
- Shared defaults never override the production owner’s private policy, configuration, schemas, schedules, or live state.
- No shared feature is imported into `Daily-Ops-Brief` automatically. Adoption requires an explicit reviewed change in that repository.
- If extraction would destabilize production, copy and sanitize the useful idea into `Life-Ops-Starter` instead of refactoring production.
- A new user may rewrite their fork freely. Those commits affect production only if its owner deliberately accepts a pull request or imports a reviewed feature.

## Why branches are not user separation

A collaborator on a personal private repository receives write access and can see the repository’s branches and history. Branches isolate development work; they do not conceal one user’s configuration or history from another collaborator. A fork gives them an independent repository for their changes, while feature branches inside that fork isolate each piece of development.

A new user should fork `Life-Ops-Starter`, not `Daily-Ops-Brief`, unless the production owner explicitly decides that exposing the full repository and history is acceptable.

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

Real values live in each deployment’s ignored local configuration and operational databases. Committed example profiles contain placeholders only.

## Feature contract

Every `feature.json` declares manifest and feature version, stable feature ID/purpose, compatible core version, dependencies, scripts/references/schemas/migrations/tests, connector/network/write permissions, runtime data boundaries, forbidden source data, per-user configuration schema, portability, and whether source contains personal data.

Build tooling discovers manifests; do not maintain a conflict-prone handwritten central registry.

## Git workflow

1. Open an issue describing the user problem, not a predetermined implementation.
2. Create a feature/fix branch.
3. Keep feature implementation in its own directory; identify core-interface changes clearly.
4. Use atomic Conventional Commit messages.
5. Add synthetic acceptance fixtures and failure cases.
6. Push the branch and open a draft pull request to the sanitized starter upstream.
7. Merge upstream only after CI passes and no personal data appears in the diff or history.
8. Tag portable releases using semantic versions.

## Moving a feature between deployments

Version 1 uses module-only commits and deliberate imports:

1. Develop and merge the portable module in the sanitized starter through a pull request.
2. Record feature ID, semantic version, and source commit in `features.lock.json`.
3. Import only the module commit/release into a deployment.
4. Supply private configuration locally and run synthetic tests before enabling writes.
5. Apply migrations transactionally and verify the target database.

Do not copy an entire personal branch into another person’s repository. If a useful feature originates in a personal deployment, first extract/sanitize the behaviour, add tests, review diff/history, merge it upstream, then import only the shared release where wanted.

Once several modules exist, replace manual import with a deterministic `sync_features` tool that reads `features.lock.json`, verifies source commits/checksums, installs only selected modules, and refuses dirty or incompatible upgrades.

## Compatibility and ownership

- Use semantic versions for core and every feature.
- Breaking manifest/schema/state migrations increment the major version.
- Migrations are idempotent, versioned, and reversible when practical.
- Each deployment pins exact feature versions; upgrades are explicit pull requests.
- User-specific policy overrides shared defaults inside that user’s private deployment.
- Shared defaults must be conservative: no destructive write, external message, email deletion, workplace-data access, or unbounded monitoring without explicit configuration and approval.

## New-user onboarding

1. New users get their own private deployment repository derived from a sanitized starter, not access to the production owner’s repository/history.
2. Run `START_HERE.md` in their deployment and store real configuration only there.
3. Extract genuinely portable improvements back into the sanitized starter through reviewed feature modules.

This gives users a common engineering surface without turning one person’s life into another person’s Git history.
