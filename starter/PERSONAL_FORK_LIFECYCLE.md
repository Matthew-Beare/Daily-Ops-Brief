# Personal Fork Lifecycle

LyfeOS is designed to be inherited, personalized, stateful, versioned, and optionally improved upstream.

## Repository lineage

```text
public upstream main/tag
        ↓ pin + seed/import
private user-owned LyfeOS repository
        ↓ first-boot state/config checkpoint
personal state transactions + feature/fix branches
        ↓ tested integration
user stable branch
        ↓ optional sanitized feature extraction
public upstream PR
```

A user's **private deployment repository is the canonical source of truth for that deployment's personal state and behavior**: mutable state events/snapshots, policy, schemas, migrations, module selection, provider references, configuration, tests, feature code, and recovery instructions.

Read `GIT_STATE_MODEL.md` for the state transaction/layout contract.

The current Daily Ops reference deployment keeps its existing Sheets/Drive authorities because that deployment has an established policy. New-user starter deployments do not inherit that exception.

## Why the default is not a literal public GitHub fork

A standard GitHub fork of a public repository is public. That is fine for code-only experimentation but wrong for a deployment whose personal state lives in Git.

The default therefore preserves **fork lineage without requiring the GitHub fork visibility relationship**:

1. pin an exact public LyfeOS release/commit/tree;
2. seed/import that source into a new private repository owned by the user;
3. record the upstream provenance and update path;
4. keep the public upstream available for compare/update/share-back workflows.

If the platform later supports a genuinely private fork of the public upstream, that can satisfy the same contract. A public fork must not receive personal state.

## First boot must produce a Git state checkpoint

After capability discovery and bounded provisioning approval:

1. resolve the exact upstream tag/commit/tree used;
2. verify the private user-owned repository is writable;
3. verify provider metadata says the personal-state repository is private;
4. write non-secret deployment configuration and selected provider references;
5. create the initial `state/` event/snapshot structure;
6. write selected feature IDs/versions and schema/migration state;
7. write generated deployment policy/instructions;
8. import only approved accessible existing user information into normalized Git state with provenance;
9. run applicable validation/privacy/source tests;
10. commit and push one coherent first-boot checkpoint;
11. read back the remote commit/state before calling initialization complete.

Credentials, OAuth tokens, passwords, raw authentication material, and full payment credentials never enter Git. Bulky raw provider evidence is optional; the canonical personal state and supported provenance/reference live in Git.

## Continuous personal state

Under standing Git authorization, each coherent state-changing user action or reconciliation cycle follows the `GIT_STATE_MODEL.md` transaction:

- read current remote HEAD and affected state;
- append immutable state event(s);
- update derived/current snapshot(s);
- validate;
- commit;
- push fast-forward only;
- read back remote state;
- report success only after verification.

Examples:
- accept a meal plan;
- record a completed hike/workout;
- add or revise an appointment;
- mark a task complete;
- reconcile an email-derived appointment with Calendar;
- confirm a purchase or shopping-intent fulfillment;
- change an ongoing routine or project state.

If the remote branch moved, re-read/reconcile and create a new commit. Never force-push state history merely to make automation easier.

## Continuous personal development

Behavior/configuration changes use the same personal Git lineage. Several experiments may exist at once on separate feature branches. The stable personal branch stays known-good; incomplete work belongs on feature/experimental branches.

Examples:
- a new meal-planning rule;
- a new appointment reconciliation policy;
- a hiking/travel planning module;
- a custom work-mode transition;
- a dashboard/schema;
- a reusable fitness evidence adapter;
- a household workflow.

## Portable feature candidate gate

When a custom feature reaches a coherent tested checkpoint, LyfeOS explicitly asks:

`Do you want to make this feature available to other people?`

If no, keep it in the user's private repository.

If yes:
1. identify reusable behavior separately from private deployment state;
2. replace personal identifiers/provider references with configuration placeholders;
3. exclude `state/`, private deployment configuration, private evidence references, and secrets;
4. create synthetic fixtures;
5. declare dependencies and permissions;
6. add migrations/rollback behavior when needed;
7. run feature tests, starter privacy audit, and public-source audit;
8. generate a portable feature manifest/version;
9. show the exact public contribution diff;
10. publish/open the upstream PR only under configured publication authority.

A later user may improve that portable feature and contribute a new version back again. Git provenance preserves the full lifecycle without copying personal state upstream.

## Upstream synchronization

Private deployments pin known-good upstream versions. Updating is deliberate:
- compare the next upstream release with the recorded provenance;
- review migrations and feature conflicts;
- test against the user's current private state/configuration;
- apply compatible source/migrations without overwriting `state/`;
- merge under the user's policy;
- verify remote commit and migrations.

Never reset a user's deployment to upstream or discard local state/features merely because public upstream advanced.

## Failure isolation

A Git state/versioning failure blocks the affected state mutation because Git is canonical for new-user deployments. Preserve the last verified remote commit, read it back, and stop that mutation rather than falling back to chat memory or another shadow database. Optional connector failures remain module-scoped. Do not repeatedly retry deterministic Git/CI conflicts. Apply the Pants Filling With Shit Report boundary when the same materially corrected operation fails twice, a write is ambiguous, or no progress is made.