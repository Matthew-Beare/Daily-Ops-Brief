# LyfeOS Starter Versioning and Personal Deployments

## Repository roles

- This repository is the public LyfeOS upstream and reference implementation.
- `starter/` is the portable onboarding/distribution boundary.
- The normal user path is a **personal fork** owned by that user. A clean audited snapshot is an alternate path.
- The user's repository is the durable source of truth for deployment behavior: policy, configuration, schemas, migrations, enabled features, tests, authority references and recovery instructions.
- Live mutable records remain in the user's selected canonical authorities and are not inherited from Git.

Read `PERSONAL_FORK_LIFECYCLE.md` for the complete lineage and contribution loop.

## Simple fork path

1. Fork the public upstream into an account/repository the user controls.
2. Connect the fork and verify read/write capability.
3. Record the exact upstream commit/tag as provenance.
4. Run `starter/START_HERE.md`.
5. Discover existing capabilities/evidence before creating duplicate systems.
6. First boot generates the user's non-secret deployment configuration, selected module/feature lock, schemas/migrations, authority references and policy.
7. Run validation/privacy/source audit.
8. Commit/push the coherent first-boot checkpoint and verify remote readback.
9. Only then enable scheduled writes whose own dependency/evidence gates pass.

The fork contains public reference history. Reference configuration is not the new user's live state.

## Clean portable-snapshot path

For users who do not want reference history:
1. pin an exact audited upstream commit;
2. copy/export only documented portable starter/features/schema/test tooling;
3. create a user-owned repository;
4. run the same first-boot/source/privacy/CI gates;
5. record upstream provenance.

## Branch model inside each personal fork

Recommended convention:

```text
main            known-good personal release
experimental    optional integration branch for several concurrent experiments
feature/*       bounded feature work
fix/*           bounded defect work
```

Five features may be in flight at once without becoming one undifferentiated branch. Merge each coherent feature into the user's `experimental` branch when needed for integrated testing; promote an audited checkpoint to the user's stable branch under their merge policy.

## Repository visibility

Public and private are both supported. Public source requires public-source audit and no secrets/credentials/mutable exports/private evidence. Private Git follows the same no-secrets rule. Visibility comes from provider metadata.

## Automatic personal versioning

After one-time standing authorization, durable behavior changes automatically update relevant validation/tests, commit, push and verify remote state. This covers policy/config/schema/migrations/feature code/onboarding and other source changes. It does not mean auto-merge, force-push, visibility change or public publication.

A user's new custom feature should be committed to their own Git lineage as it becomes a coherent checkpoint. Git therefore preserves how the user's LyfeOS evolved even when the feature is never shared upstream.

## Share-back gate

When a personal feature is coherent and tests pass, ask:

`Do you want to make this feature available to other people?`

If yes, follow `SHARED_FEATURE_WORKFLOW.md`: extract portable behavior, replace user-specific configuration with placeholders, remove private/runtime evidence, create synthetic fixtures, declare dependencies/permissions/migrations, run privacy/public-source/feature tests, show the contribution diff, then open an upstream PR only under publication authority.

If no, keep the feature local. The user can change that choice later.

## Deployment version record

Persist a small non-secret record containing:
- core version or snapshot identifier;
- exact upstream commit/tag;
- schema version;
- selected portable feature IDs/versions in `features.lock.json`;
- migration checksums/state;
- local policy version;
- repository visibility;
- enabled connector capability identifiers without credentials;
- last verified personal source commit.

Never put mutable operational records or secrets in the version record.

## Updating from upstream

1. fetch/compare the next audited upstream release;
2. read release notes/migrations;
3. test against the user's configuration/features;
4. apply idempotent migrations to a safe copy when required;
5. review source/config delta and local-feature conflicts;
6. merge under the user's policy;
7. verify remote commit and runtime migrations.

Never reset a personal fork to upstream or overwrite local features silently.

## Public release model

Use semantic versions for upstream releases. Feature branches are not installation targets. `main` remains the stable public line only after coherent forensic CI and merge authority. Personal forks may pin any known-good upstream tag and advance deliberately.

## Production flow for upstream

1. develop bounded features on feature branches;
2. integrate several concurrent features on an experimental/integration branch when useful;
3. run repository validation, public-source history audit, starter privacy audit, root/runtime/starter tests and feature tests;
4. open the release PR only when coherent;
5. merge under repository-owner authority;
6. verify the released tree is the tested tree;
7. never commit mutable state or secrets merely because portability matters.