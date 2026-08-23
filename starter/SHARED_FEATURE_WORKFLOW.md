# Shared LyfeOS Feature Workflow

## Decision

The public upstream distributes portable behavior, schemas, tests, examples, onboarding, and synthetic fixtures. Each deployment keeps its mutable operational state in that user's selected authorities. A deployment repository may be public or private by explicit choice; portable contributions must never depend on another user's mutable state.

| Surface | Contents | Rule |
|---|---|---|
| Public upstream | portable core/starter/features/tests/reference implementation | no secrets or mutable operational exports |
| User deployment source | that user's durable policy/config/schema/tests | public or private by owner choice; source-audit rules apply |
| Live authorities | tasks, receipts, messages, assets, progress, finance, evidence | never distributed through Git |

The current public upstream may include an intentionally public reference deployment. The **starter/portable boundary**, not that reference configuration, defines new-user defaults.

## Non-compromise invariants

- Shared defaults never override a deployment owner's selected timezone, accounts, authorities, schedules, goals, repository visibility, or mutable state.
- No feature is imported into another deployment automatically. Adoption is an explicit reviewed source change.
- Public source contains no credentials, secrets, mutable operational exports, receipt/mail bodies, account data, or unintended personal information.
- A feature may originate in any deployment. Before upstream publication, separate portable behavior from deployment state and run privacy/public-source tests.
- If portability work would destabilize a working deployment, extract/copy the reusable behavior into the portable boundary rather than weakening the working deployment.

## Why a branch is not a deployment boundary

Branches isolate code changes, not data ownership. A user should not treat another person's feature branch as their configuration. Forking the public upstream is supported because the upstream is intentionally public, but first boot must generate/select that user's own authorities and configuration rather than reusing reference values.

## Portable feature boundary

A portable feature lives under `features/<feature-id>/` when it needs an independent module boundary:

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

Only needed directories should exist. `feature.json` is validated against `schemas/feature-manifest.schema.json`.

Portable source may contain behavior, schemas, placeholders, synthetic fixtures, and tests. It must not contain real mutable personal data, credentials/secrets, private work records, account exports, or assumptions that should be configuration.

## Feature contract

Every manifest declares feature version, stable ID/purpose, compatible core version, dependencies, entrypoints, permissions, runtime data boundaries, forbidden source data, per-user configuration schema, portability, and tests.

Build tooling discovers manifests. Avoid a conflict-prone handwritten registry.

## Git workflow

1. Describe the user problem.
2. Create a feature/fix branch in an appropriate repository.
3. Keep implementation scoped and identify core-interface changes.
4. Add synthetic acceptance fixtures and failure cases.
5. Validate behavior without copying mutable user data into source.
6. Run public-source/privacy checks before any public push or upstream PR.
7. Open a PR to the public upstream for portable improvements.
8. Merge only after coherent CI passes and review shows no forbidden source data.
9. Tag public releases with semantic versions when release boundaries are established.

## Bidirectional feature exchange

Features may originate in any user's deployment:

- develop and test the useful behavior;
- extract portable code/policy/schema from mutable deployment state;
- run privacy/public-source review;
- contribute the portable delta upstream;
- other deployments deliberately import the reviewed upstream version;
- improvements can flow back through another reviewed contribution.

Authorship/source provenance belongs in Git commits/releases and `features.lock.json`, never in copied runtime data.

## Moving a feature between deployments

1. Pin a reviewed feature/core commit or release.
2. Import only the portable source delta and declared dependencies.
3. Supply deployment configuration from that deployment's own authorities.
4. Run synthetic tests and dependency checks before enabling writes.
5. Apply migrations transactionally/idempotently and verify state.
6. Record installed version/commit/migration in `features.lock.json`.

Do not use mutable user data as the distribution mechanism.

## Compatibility and ownership

- Use semantic versions for core/features once release tagging begins.
- Breaking schema/state migrations increment the major version.
- Migrations are idempotent, versioned, and reversible when practical.
- Deployments pin exact versions/commits; upgrades are deliberate.
- User-specific policy overrides shared defaults.
- Shared defaults are conservative: no destructive write, external message, email deletion, workplace-data access, or unbounded monitoring without configured authority.
- Feature dependencies must be declared rather than assumed from accidental files.

## New-user onboarding

1. Fork the public upstream or create a clean repository from an audited portable snapshot.
2. Run `START_HERE.md`.
3. Build the new user's configuration from their interview and connected authorities; never reuse reference deployment state.
4. Record repository visibility and run the required source-audit path.
5. Pin the core commit/release and selected feature versions before scheduled writes.
6. Contribute reusable improvements upstream only after sanitization and review.

This supports a public ecosystem without turning Git into a database of people's lives.