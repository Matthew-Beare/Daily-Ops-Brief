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

A collaborator on a personal private repository receives write access and can see the repository’s branches and history. Branches isolate development work; they do not conceal one user’s configuration or history from another collaborator. A fork gives her an independent repository for her changes, while feature branches inside that fork isolate each piece of development.

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

A portable feature contains behaviour, schemas, placeholders, synthetic fixtures, and tests. It must not contain:

- real names, email bodies, addresses, account or claim numbers;
- Sheet, Calendar, Gmail, or repository IDs tied to a person;
- API keys, tokens, credentials, or recovery material;
- mutable tasks, trips, meals, workouts, appointments, or health records;
- VA, Veteran, patient, employee, personnel, payment, or other nonpublic work data;
- assumptions that only make sense for one person unless expressed as configuration.

Real values live in each deployment’s ignored `config/profile.local.json` and operational databases. Committed `profile.example.json` files contain placeholders only.

## Feature contract

Every `feature.json` declares:

- manifest and feature version;
- stable feature ID and concise purpose;
- compatible core version;
- dependencies;
- scripts, references, schemas, migrations, and tests;
- connector, network, and write permissions;
- runtime data boundary and forbidden source data;
- a JSON Schema for per-user configuration;
- whether the feature is portable and whether source contains personal data.

Build tooling discovers manifests; do not maintain a conflict-prone handwritten central registry.

## Git workflow

1. Open an issue describing the user problem, not a predetermined implementation.
2. Create a branch such as `feat/hiking-conditions-watch` or `fix/meal-plan-leftovers`.
3. Keep the feature’s implementation in its own directory. Any core-interface change requires its own clearly identified commit.
4. Use atomic Conventional Commit messages, for example:
   - `feat(hiking): add armed conditions watch`
   - `fix(meals): preserve allergy exclusions`
   - `test(training): cover missed-session rollover`
5. Add synthetic acceptance fixtures and failure cases.
6. Push the branch to the developer’s fork and open a draft pull request to `Life-Ops-Starter`. Another collaborator reviews behaviour, permissions, portability, and tests.
7. Merge upstream only after CI passes and no personal data appears in the diff or history.
8. Tag portable releases using semantic versions.

GitHub’s normal branch-and-pull-request workflow is documented in [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow).

## Moving a feature between deployments

Version 1 uses module-only commits and deliberate imports:

1. Develop and merge the portable module in `Life-Ops-Starter` through a fork and pull request.
2. Record its feature ID, semantic version, and source commit in the target deployment’s `features.lock.json`.
3. Import only the module commit or release into the deployment.
4. Supply private configuration locally and run the feature’s tests against synthetic data before enabling writes.
5. Apply any declared migration transactionally and verify the target database.

Do not copy an entire personal branch into the other person’s repository. If a useful feature originates in a personal deployment, first copy the behaviour into a clean `Life-Ops-Starter` feature branch, remove personal policy and data, add tests, review the full diff and history, merge it upstream, and then import the shared release only where wanted.

Once several modules exist, replace manual import with a deterministic `sync_features` tool that reads `features.lock.json`, verifies source commits and checksums, installs only selected modules, and refuses dirty or incompatible upgrades.

## Compatibility and ownership

- Use semantic versions for the core and every feature.
- A breaking manifest, schema, or state migration increments the major version.
- Each migration is idempotent, versioned, and reversible when practical.
- Each deployment pins exact feature versions; upgrades are explicit pull requests.
- User-specific policy always overrides a shared feature default inside that user’s private deployment.
- Shared defaults must be conservative: no destructive write, external message, email deletion, workplace-data access, or unbounded monitoring without explicit configuration and approval.

## New-user onboarding

1. Create the new user’s GitHub account and enable a passkey or two-factor authentication; store recovery codes somewhere separate and durable. See [GitHub’s 2FA setup](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/configuring-two-factor-authentication).
2. Invite them to the sanitized `Life-Ops-Starter`, not the production repository. GitHub supports collaborators on private personal repositories, but personal-repository collaborators receive write access. See [repository permission levels](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/permission-levels-for-a-personal-account-repository).
3. Have them fork `Life-Ops-Starter` and treat that fork as their deployment repository.
4. Run `START_HERE.md` in their fork. Put their answers and real configuration only there; send upstream only sanitized, portable modules.
5. Build no more than three version-1 features, validate them privately, then extract only genuinely portable behaviour into `Life-Ops-Starter`.

This gives users a common engineering surface without turning one person’s life into another person’s Git history.
