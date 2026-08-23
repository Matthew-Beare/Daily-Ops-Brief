# LyfeOS Starter Versioning and Personal Deployments

## Repository roles

- This repository is the **public LyfeOS upstream** and reference implementation.
- `starter/` is the portable onboarding/distribution boundary.
- The normal user deployment is a **private personal-lineage repository** seeded from a pinned upstream release/commit/tree.
- That private repository is the durable source of truth for both personal mutable state and deployment behavior: `state/`, policy, configuration, schemas, migrations, enabled features, tests, provider references, and recovery history.
- Credentials remain with providers and never enter Git.
- The current Daily Ops reference deployment keeps its existing Sheets/Drive authorities as a deployment-specific exception; starter users do not inherit that storage model.

Read `GIT_STATE_MODEL.md` and `PERSONAL_FORK_LIFECYCLE.md` for the state/lineage contracts.

## Private personal-lineage path — default

A normal GitHub fork of a public repository is public. Because the starter stores personal state in Git, the safe default is:

1. pin an exact audited public LyfeOS release/commit/tree;
2. create a **private** repository owned by the user;
3. seed/import the pinned LyfeOS source into that repository and record upstream provenance;
4. connect the private repository and verify read/write capability;
5. run `starter/START_HERE.md`;
6. discover existing capabilities/evidence before creating duplicate systems;
7. generate the user's initial Git state, configuration, selected module/feature lock, schemas/migrations, provider references, and policy;
8. run validation/privacy/source checks;
9. commit/push the coherent first-boot checkpoint and verify remote readback;
10. only then enable scheduled/provider writes whose own gates pass.

This is a fork **lineage** even when GitHub cannot represent the relationship as a private fork of a public repository.

## Public GitHub fork path — code only

A literal public fork is useful for public development or contribution work, but it must not receive personal-state files. If a user begins with a public fork and wants normal LyfeOS personal-state mode, first create/migrate to a private deployment repository.

## Clean portable-snapshot path

For users who do not want reference history:
1. pin an exact audited upstream commit;
2. copy/export documented portable starter/features/schema/test tooling into a private user-owned repository;
3. record upstream provenance;
4. run the same first-boot/state/privacy/CI gates.

## Branch model inside each personal deployment

Recommended convention:

```text
main            known-good personal state + behavior
experimental    optional integration branch for concurrent experiments
feature/*       bounded feature work
fix/*           bounded defect work
```

Canonical state mutations normally commit to the configured stable state branch as small transactional commits. Feature development happens separately and must not silently fork or overwrite canonical state.

## Git state transaction model

Each coherent state-changing user action or reconciliation cycle:

1. reads current remote HEAD;
2. appends immutable state event(s);
3. updates derived/current snapshots;
4. validates;
5. commits;
6. pushes fast-forward only;
7. reads back the remote commit/state.

If remote HEAD moved, re-read and reconcile. Never force-push personal state history.

See `GIT_STATE_MODEL.md` for layout and failure semantics.

## Repository visibility

The public upstream is public by design. A deployment repository that stores personal state is **private by default and required to be private before personal-state writes are enabled**.

Private Git still is not a secret vault. Never commit credentials, tokens, keys, authentication cookies, full payment credentials, or data the user explicitly excludes from Git.

A public repository may contain only portable/public source and information intentionally published. Public contributions must pass public-source/privacy gates.

## Automatic personal versioning

After one-time standing authorization, coherent state/config/behavior changes automatically validate, commit, push, and verify remote state. This includes state events/snapshots, policy/config/schema/migrations/feature code/onboarding, and reconciliation results.

Automatic versioning does not mean force-push, repository-visibility change, destructive history rewriting, upstream publication, or external communication.

## Share-back gate

When a personal feature is coherent and tests pass, ask exactly:

`Do you want to make this feature available to other people?`

If yes, follow `SHARED_FEATURE_WORKFLOW.md`: extract only portable behavior, remove `state/` and private deployment material, replace personal examples with synthetic fixtures, declare dependencies/permissions/migrations, run privacy/public-source/feature tests, show the exact public diff, then publish/open an upstream PR only under publication authority.

If no, keep the feature in the private deployment. The choice can change later.

## Deployment version record

Persist non-secret version/config state containing:
- core version or snapshot identifier;
- exact upstream commit/tag/tree;
- schema version;
- selected feature IDs/versions in `features.lock.json`;
- migration checksums/state;
- local policy version;
- repository visibility;
- enabled connector capability identifiers without credentials;
- canonical state branch;
- last verified personal commit.

Mutable user state itself lives under `state/`, not in a separate mandatory database.

## Updating from upstream

1. compare the next audited upstream release with recorded provenance;
2. read release notes/migrations;
3. test against the user's private configuration and state schemas;
4. apply idempotent migrations to a safe copy when required;
5. review source/config delta and local-feature conflicts;
6. preserve `state/` and personal policy overrides;
7. merge under the user's policy;
8. verify remote commit, state integrity, and migrations.

Never reset a personal deployment to upstream or overwrite local state/features silently.

## Public release model

Use semantic versions for upstream releases. Feature branches are not installation targets. Public `main` remains the stable upstream only after coherent forensic CI and merge authority. Private personal deployments may pin any known-good upstream release and advance deliberately.

## Production flow for upstream

1. develop bounded portable features on feature branches;
2. integrate concurrent features when useful;
3. exclude personal `state/` and private deployment material from contribution diffs;
4. run repository validation, public-source history audit, starter privacy audit, root/runtime/starter tests, and feature tests;
5. open the release PR only when coherent;
6. merge under repository-owner authority;
7. verify the released tree is the tested tree.