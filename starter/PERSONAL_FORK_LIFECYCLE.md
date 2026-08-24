# Personal Fork Lifecycle

LyfeOS is designed to be inherited, personalized, versioned, and optionally improved upstream without treating Git as the user's live database.

## Repository lineage

```text
public upstream main/tag
        ↓ fork/clone/pin
user-owned LyfeOS source repository
        ↓ first-boot source/config checkpoint
feature/fix branches + optional experimental integration
        ↓ tested personal release
        ↓ optional sanitized feature extraction
public upstream PR
```

The user's Git repository is the durable source of truth for **behavior and structure**: policy, schemas, migrations, module selection, authority references, non-secret configuration, tests, feature code, onboarding, provenance, and recovery instructions.

Mutable personal operational state lives in canonical authorities described in `STATE_AUTHORITY_MODEL.md`, normally Google Sheets plus Google Drive evidence for the starter.

## First boot

After capability discovery and bounded provisioning approval:

1. resolve the exact upstream tag/commit/tree used;
2. verify the user-owned repository is writable and record visibility/provenance;
3. create/select the structured state authority and evidence root;
4. create and verify the `Authority Registry` and `Interview Ledger`;
5. write non-secret deployment configuration, selected feature IDs/versions, schemas/migrations, and policy;
6. import approved accessible existing information into the selected canonical state/evidence authorities with provenance;
7. run applicable validation/privacy/source tests;
8. commit and push one coherent Git source/config checkpoint;
9. read back the remote source commit;
10. read back canonical state/evidence writes before calling initialization complete.

Credentials, OAuth tokens, passwords, raw authentication material, full payment credentials, mutable Sheet exports, and private Drive evidence do not belong in portable Git source.

## Continuous state

Routine state changes happen in the canonical mutable authority, not Git. Each state-changing action follows the module contract:

- read canonical state/evidence;
- correlate/dedupe using stable IDs;
- write the smallest mutation;
- read back the canonical authority;
- verify material fields;
- retain required event/history rows;
- report success only after verification.

Examples include accepting a meal plan, recording a workout, adding/revising an appointment, marking a task complete, or reconciling an email-derived appointment with Calendar.

## Continuous personal development

After standing Git authorization, lasting behavior/configuration/schema/migration/onboarding changes automatically validate, commit, push, and receive remote readback. Several experiments may exist at once on separate feature branches. The stable personal branch stays known-good; incomplete work belongs on feature/experimental branches.

Examples:
- a new meal-planning rule;
- an appointment reconciliation policy;
- a hiking/travel module;
- a custom work-mode transition;
- a state-store schema migration;
- a reusable fitness evidence adapter;
- a household workflow.

## Portable feature candidate gate

When a custom feature reaches a coherent tested checkpoint, LyfeOS asks exactly:

`Do you want to make this feature available to other people?`

If no, keep it in the user's repository.

If yes:
1. identify reusable behavior separately from deployment state;
2. replace personal identifiers/authority references with configuration placeholders;
3. exclude live Sheet rows, Drive evidence, Calendar events, private provider IDs, local config, and secrets;
4. create synthetic fixtures;
5. declare dependencies and permissions;
6. add migrations/rollback behavior when needed;
7. run feature tests, starter privacy audit, and public-source audit;
8. generate a portable feature manifest/version;
9. show the exact public contribution diff;
10. publish/open the upstream PR only under configured publication authority.

## Upstream synchronization

User deployments pin known-good upstream versions. Updating is deliberate:
- compare the next release with recorded provenance;
- review migrations and feature conflicts;
- test against the user's configuration/state schemas;
- apply compatible source and bounded state-store migrations;
- preserve canonical state and local features;
- merge under the user's policy;
- verify remote source commit and state migration readback.

Never reset a user's deployment to upstream or discard local state/features merely because public upstream advanced.

## Failure isolation

A Git failure blocks only the durable source mutation that depends on it. A Sheets/Drive/selected-state failure blocks only the state-changing module that depends on that authority. Preserve and read back known-good state, continue unrelated healthy modules, and never fall back to chat memory or a shadow database.
