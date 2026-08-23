# Personal Fork Lifecycle

LyfeOS is designed to be inherited, personalized, versioned, and optionally improved upstream.

## Repository lineage

```text
public upstream main/tag
        ↓ fork or audited snapshot
user-owned LyfeOS repository
        ↓ first-boot configuration checkpoint
personal feature/fix branches
        ↓ tested integration
user stable branch
        ↓ optional sanitized contribution
public upstream PR
```

A user's repository is the durable source of truth for that deployment's **behavior**: policy, schemas, migrations, module selection, authority references, configuration, tests, feature code, and recovery instructions. Live mutable records remain in the selected canonical authorities for their data class. This separation keeps Git portable and reviewable without turning every appointment or completion into a merge conflict.

## First boot must produce a Git checkpoint

After dependency discovery and the user's bounded provisioning approval:

1. resolve the exact upstream tag/commit used;
2. verify the user-owned repository is writable;
3. record repository visibility and source-audit policy;
4. write non-secret deployment configuration and authority references;
5. write selected feature IDs/versions and schema/migration state;
6. write the generated deployment policy/instructions;
7. run applicable validation/privacy/source-audit tests;
8. commit and push one coherent first-boot checkpoint;
9. read back the remote commit before calling source initialization complete.

Do not commit credentials, raw private evidence, mutable exports, message bodies, receipt images, account transactions, medical records, school submissions, or secrets merely to make recovery convenient.

## Continuous personal development

After standing Git authorization, durable behavior changes automatically receive a branch/checkpoint, tests, commit, push, and remote verification. Several experiments may exist at once on separate feature branches. A user's stable branch should stay known-good; incomplete work belongs on feature/experimental branches.

Examples of durable behavior changes:
- a new meal-planning rule;
- a new appointment reconciliation policy;
- a hiking/travel planning module;
- a custom work-mode transition;
- a new dashboard/schema;
- a reusable fitness evidence adapter;
- a new household workflow.

Live facts produced by those workflows remain in canonical runtime state, not in portable source.

## Portable feature candidate gate

When a custom feature reaches a coherent tested checkpoint, LyfeOS should explicitly ask:

`Do you want to make this feature available to other people?`

If no, keep it in the user's repository.

If yes:
1. identify the reusable behavior separately from the user's configuration/state;
2. replace personal identifiers and authority IDs with configuration placeholders;
3. remove private examples/evidence and use synthetic fixtures;
4. declare dependencies and permissions;
5. add migrations and rollback behavior when needed;
6. run feature tests, starter privacy audit, and public-source audit;
7. generate a portable feature manifest/version;
8. show the contribution diff and upstream target;
9. require the repository owner's publication/PR authority;
10. submit for upstream review rather than silently publishing.

A portable feature can later be improved by another fork and contributed back again. Git provenance records authorship and version history without copying anyone's runtime data.

## Upstream synchronization

User forks should pin known-good upstream versions. Updating is deliberate:
- fetch/compare upstream release;
- review migrations and feature conflicts;
- test against the user's configuration;
- merge under the user's policy;
- verify remote/readback and runtime migrations.

Never reset a user's fork to upstream or overwrite local features merely because a newer public version exists.

## Failure isolation

A source/versioning failure blocks only the durable-source mutation that depends on it. Preserve current live canonical state and the last verified Git commit. Do not repeatedly retry a deterministic Git/CI failure. Apply the Pants Filling With Shit Report boundary when the same corrected operation fails twice or no progress is made.