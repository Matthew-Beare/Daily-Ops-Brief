# Shared LyfeOS Feature Workflow

## Decision

LyfeOS is an ecosystem of private personal deployments built from a stable **public upstream**. Each user's private repository versions personal state, behavior, configuration, schemas, tests, and features. Portable improvements flow upstream/downstream only through a sanitized, reviewed boundary.

| Surface | Contents | Rule |
|---|---|---|
| Public upstream | portable core/starter/features/tests/reference implementation | no private deployment state or secrets |
| Private user deployment | `state/`, policy/config/schema/tests/personal features/provider refs | canonical personal source of truth |
| Optional providers | email/calendar/finance/wearable/files/maps/etc. | evidence/projection/action adapters; credentials stay provider-side |

The current public Daily Ops reference deployment has its own established external state authorities. That exception is not the generic starter model.

## Non-compromise invariants

- Personal state lives in the private deployment Git repository under `GIT_STATE_MODEL.md`.
- A normal public GitHub fork must not receive personal state.
- Shared defaults never override a deployment owner's timezone, provider choices, schedules, goals, or local features.
- Adoption is explicit. Importing an upstream feature is a reviewed source/config/migration change.
- Public contributions contain no `state/`, credentials, secrets, private provider/evidence references, receipt/mail bodies, account/medical/school records, or unintended personal information.
- If portability extraction would destabilize a working deployment, preserve the working private repository and extract the reusable behavior separately.
- Dependencies and permissions are declared, not assumed from whatever happens to be connected on the author's account.

## Personal feature lifecycle

1. User identifies a problem or LyfeOS discovers a useful workflow opportunity.
2. Create/modify the feature on the user's feature branch.
3. Add/update policy, config schema, migrations, and tests as needed.
4. Test against synthetic fixtures plus the private deployment interfaces without copying private state into portable source.
5. Commit/push a coherent personal feature checkpoint under standing authorization.
6. Integrate with other personal experiments on `experimental` when needed.
7. When coherent and useful, ask exactly: **Do you want to make this feature available to other people?**

If no, stop there. The feature remains a valid private personal feature.

If yes, continue through the portability gate.

## Portability gate

Before an upstream contribution:
1. state the reusable problem/behavior without personal assumptions;
2. replace user identifiers, provider IDs, and deployment-specific constants with configuration;
3. exclude the entire private `state/` surface and private deployment configuration;
4. remove real private evidence and create synthetic fixtures;
5. minimize dependencies and declare optional/required connectors;
6. define permissions, state/event schemas, and provider adapter boundaries;
7. make migrations idempotent and reversible when practical;
8. add feature version/manifest and compatibility range;
9. run feature tests, repository validation, starter privacy audit, and public-source history/current-tree audit;
10. show the user the exact public contribution diff and what will become public;
11. open an upstream PR only under explicit publication authority.

Never interpret permission to auto-version a private personal deployment as permission to publish upstream.

## Portable feature boundary

Portable modules live under `starter/features/<feature-id>/` when an independent module boundary is useful:

```text
starter/features/<feature-id>/
├── feature.json
├── FEATURE.md
├── references/
├── scripts/
├── schemas/
├── migrations/
└── tests/
```

Only needed directories should exist. `feature.json` follows the feature-manifest validator.

Portable source describes how a feature reads/writes deployment-local Git state and optional provider adapters. It never contains a real user's state.

## Feature contract

Every portable manifest declares feature version, stable ID/purpose, compatible core version, dependencies, entrypoints, permissions, runtime data boundary, forbidden public-source data, per-user configuration schema, and tests.

Avoid a handwritten global feature registry when manifests can be discovered automatically.

## Bidirectional exchange

```text
public upstream release
        ↓ seed private lineage
private personal deployment
        ↓ personal state + customization
personal feature
        ↓ opt-in sanitization + PR
public upstream
        ↓ review/release
other private personal deployments
```

Another user may improve the feature and contribute a later portable version. Git commits/releases preserve provenance/authorship without making anybody's private state part of the exchange.

## Moving a feature between deployments

1. Pin a reviewed feature/core version.
2. Import only portable source plus declared dependencies.
3. Supply private configuration from the receiving deployment.
4. Run synthetic tests and dependency checks before writes.
5. Apply migrations transactionally/idempotently to private Git state and verify state.
6. Record installed version/commit/migration in `features.lock.json`.
7. Preserve local overrides and never silently overwrite private state with upstream defaults.

## Dependency minimization

Portable modules should depend on Git state interfaces plus the smallest optional provider capabilities they need. Example: exercise accountability works manually with Git state and may optionally consume a wearable/activity adapter. Appointment reconciliation works with manual Git-backed appointments, while email evidence and Calendar projection are optional adapters.

A missing optional dependency fails that adapter path only. Avoid central middleware whose failure disables unrelated life domains.

## New-user onboarding

1. Pin the public upstream release/commit/tree.
2. Create a private user-owned deployment repository and record upstream provenance.
3. Run `START_HERE.md`, `GIT_STATE_MODEL.md`, and `CAPABILITY_DISCOVERY.md`.
4. Build private Git state/configuration from interview plus reachable existing evidence; never reuse reference deployment state.
5. Commit/push/read back the first coherent personal deployment checkpoint after approval.
6. Pin core and selected feature versions before scheduled/provider writes.
7. Let the private deployment evolve independently.
8. Offer reusable personal improvements upstream only through the opt-in portability gate.

This supports easy inherit → customize → improve → share → re-inherit cycles while keeping each person's actual life in their own private Git history.