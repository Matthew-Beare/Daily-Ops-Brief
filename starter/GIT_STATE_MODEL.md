# Git-Native Personal State Model

LyfeOS new-user deployments use **Git as the canonical personal state authority** as well as the durable behavior/versioning authority. The public LyfeOS repository remains upstream source. A person's private deployment repository contains their own state, configuration, enabled features, policy, schemas, migrations, and history.

The current Daily Ops reference deployment is an explicit exception because its existing production authorities remain Sheets/Drive under that deployment's policy. New users do not inherit that storage architecture.

## Privacy and repository topology

A repository that contains personal mutable state should be **private**. A normal GitHub fork of a public repository is public, so the safe default is a private personal-lineage repository seeded from a pinned public LyfeOS release/tree while retaining upstream provenance.

```text
public LyfeOS upstream
        ↓ pin release/commit
private user-owned deployment repository
        ├── deployment/       non-secret deployment configuration
        ├── state/            canonical personal mutable state
        ├── features.lock.json
        ├── personal features/policy/tests
        └── upstream provenance
                ↓ optional sanitized extraction
public upstream contribution
```

A literal public GitHub fork may be used for code-only experimentation, but **personal-state mode must not write private state into a public fork**. To use personal-state mode, move to a private user-owned repository first.

Credentials, OAuth tokens, passwords, private keys, authentication cookies, and full payment-card/bank credentials never belong in Git, even in a private repository. Providers retain their own credentials.

## State layout

Prefer an event-plus-snapshot model so state changes are auditable and merge conflicts stay small:

```text
state/
├── events/
│   ├── appointments/YYYY/<event-uuid>.json
│   ├── meals/YYYY/<event-uuid>.json
│   ├── routines/YYYY/<event-uuid>.json
│   ├── tasks/YYYY/<event-uuid>.json
│   ├── purchases/YYYY/<event-uuid>.json
│   └── <domain>/YYYY/<event-uuid>.json
├── snapshots/
│   ├── appointments.json
│   ├── meal-plans.json
│   ├── recipes.json
│   ├── routines.json
│   ├── tasks.json
│   └── <domain>.json
└── evidence-refs/
    └── <source-uuid>.json
```

- Event files are immutable after commit except for a deliberate correction event.
- Snapshot files are derived/current materialized state and may be rebuilt from events.
- Every state object uses stable IDs/UUIDs and provenance.
- Evidence references may store provider message/event/file IDs and supported extracted facts, but not credentials.
- Large binaries and raw provider bodies are not required for canonical state. They may remain in the originating provider or an optional evidence store, with a Git reference to them.

## Transaction contract

Every coherent state-changing action or reconciliation cycle is one Git transaction:

1. read the current remote deployment HEAD;
2. read the affected current snapshot/event history;
3. create immutable event file(s) with stable IDs and provenance;
4. update affected snapshot(s);
5. run schema/domain validation;
6. commit with a concise machine-readable subject;
7. push by fast-forward only;
8. read back the remote commit and affected state;
9. only then report the mutation complete.

If the remote branch moved, do not force-push. Re-read the new HEAD, reconcile the intended state change, and create a new transaction. Ambiguous writes get readback before any corrected retry.

Recommended commit examples:

```text
state(appointments): add verified dental appointment
state(meals): accept weekly meal plan
state(routines): record completed hike
state(tasks): mark passport renewal done
reconcile(appointments): update appointment from email evidence
```

Standing Git authorization may allow these transactional commits/pushes without repeated confirmation. It does not authorize destructive history rewriting, repository visibility changes, public publication, or external communication.

## Connectors are adapters, not competing authorities

For the portable starter, Git owns personal state. Optional integrations provide evidence, projections, or actions:

- Gmail/email: evidence source; extracted supported facts and source IDs reconcile into Git state.
- Google Calendar: projection/reminder surface; canonical appointment identity remains in Git and stores the linked Calendar event ID.
- Fitness/wearable: optional evidence for activity/routine events; Git retains the accepted state/progression history.
- Finance: optional evidence for reconciliation; accepted reconciliation results are recorded in Git state.
- Drive/files: optional source or bulky evidence store; canonical indexes/provenance remain in Git.
- Maps/weather/travel: current planning inputs; accepted plans/tasks may be recorded in Git.

A connector failure blocks only the dependent evidence/projection path. It must not make unrelated Git state unreadable or unwritable.

## Appointment reconciliation example

For an approved appointment-email class:

1. read the complete relevant email;
2. dedupe against Git appointment/source state;
3. extract only supported fields;
4. create/update the linked Calendar event when Calendar is enabled;
5. read the Calendar event back and verify event ID, target calendar, title, time/timezone, reminders, and source linkage;
6. commit the verified appointment event/snapshot plus Calendar event ID/source reference into Git;
7. read back the Git commit;
8. mark the source reconciled only after both projections and canonical Git state agree.

Later revisions/cancellations update the same canonical Git appointment and linked Calendar event. Ambiguity asks instead of guessing.

For sensitive appointments, store only the minimum detail the user chose for organization. Never infer diagnosis, treatment, prognosis, or other medical facts from scheduling evidence.

## Meal planning example

Recipes, accepted meal plans, pantry/freezer facts, shopping intent, and meal-history state live in the private deployment repository. Accessible prior chats/files/connected sources are ingestion evidence. New plans are proposed, then accepted state becomes a Git transaction. Shopping intent remains distinct from purchase history.

## Feature sharing boundary

Personal state never rides upstream with a reusable feature.

When the user answers yes to `Do you want to make this feature available to other people?`:

1. extract portable behavior/config/schema/migrations/tests from the personal repository;
2. replace user-specific state/config with placeholders and synthetic fixtures;
3. exclude `state/`, deployment-private configuration, private evidence references, and secrets;
4. run privacy/public-source/feature tests;
5. show the public diff;
6. publish only under the user's configured publication authority.

This preserves the full inherit → customize → improve → share → re-inherit lifecycle while each person's actual life remains in their own private Git history.

## Recovery

A fresh conversation should be able to reconstruct the deployment from:

1. the private personal Git repository;
2. provider connections needed for selected evidence/projection adapters;
3. optional external bulky evidence referenced by Git.

Chat history is not required for recovery.