# Shared LyfeOS Feature Workflow

## Decision

LyfeOS is an ecosystem of personal forks built from a stable public upstream. Each user's fork versions durable behavior/config/schema/tests/features. Live mutable records remain in that user's selected canonical authorities. Features may originate anywhere and flow upstream/downstream only through a portable, reviewed boundary.

| Surface | Contents | Rule |
|---|---|---|
| Public upstream | portable core/starter/features/tests/reference implementation | no secrets or mutable operational exports |
| User fork | user's durable policy/config/schema/tests/personal features | user-controlled; public/private source-audit rules apply |
| Live authorities | tasks, appointments, receipts, progress, finance, evidence | not distributed as portable Git source |

## Non-compromise invariants

- Shared defaults never override a deployment owner's timezone, accounts, authorities, schedules, goals, repository visibility, or local features.
- Adoption is explicit. Importing an upstream feature is a reviewed source/config/migration change.
- Public contributions contain no credentials, secrets, mutable exports, receipt/mail bodies, account/medical/school records, or unintended personal information.
- If portability extraction would destabilize a working deployment, preserve the working fork and extract the reusable behavior separately.
- Dependencies and permissions are declared, not assumed from whatever happens to be connected on the author's account.

## Personal feature lifecycle

1. User identifies a problem or LyfeOS discovers a useful workflow opportunity.
2. Create/modify the feature on the user's feature branch.
3. Add/update policy, config schema, migrations and tests as needed.
4. Test against synthetic fixtures plus the user's deployment interfaces without copying runtime data into portable source.
5. Commit/push a coherent personal checkpoint under standing authorization.
6. Integrate with other personal experiments on `experimental` when needed.
7. When coherent and useful, ask exactly: **Do you want to make this feature available to other people?**

If the answer is no, stop there. The feature remains a valid personal feature.

If yes, continue through the portability gate below.

## Portability gate

Before an upstream contribution:
1. state the reusable problem/behavior without personal assumptions;
2. replace user identifiers, authority IDs and deployment-specific constants with configuration;
3. remove real private/runtime evidence and create synthetic fixtures;
4. minimize dependencies and declare optional/required connectors;
5. define data boundaries and permission/write surfaces;
6. make migrations idempotent and reversible when practical;
7. add feature version/manifest and compatibility range;
8. run feature tests, repository validation, starter privacy audit and public-source history/current-tree audit;
9. show the user the portable contribution diff and what will become public;
10. open an upstream PR only under explicit repository publication authority.

Never interpret permission to auto-version a personal fork as permission to publish upstream.

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

## Feature contract

Every portable manifest declares feature version, stable ID/purpose, compatible core version, dependencies, entrypoints, permissions, runtime data boundary, forbidden source data, per-user configuration schema and tests.

Avoid a handwritten global feature registry when manifests can be discovered automatically.

## Bidirectional exchange

```text
public upstream release
        ↓ deliberate sync
personal fork
        ↓ personal customization
personal feature
        ↓ opt-in sanitization + PR
public upstream
        ↓ review/release
other personal forks
```

Another user may improve the feature and contribute a later portable version. Git commits/releases preserve provenance and authorship without making runtime data part of the exchange.

## Moving a feature between deployments

1. Pin a reviewed feature/core version.
2. Import only portable source plus declared dependencies.
3. Supply configuration from the receiving deployment.
4. Run synthetic tests and dependency checks before writes.
5. Apply migrations transactionally/idempotently and verify state.
6. Record installed version/commit/migration in `features.lock.json`.
7. Preserve local overrides and do not silently overwrite a personal feature with upstream defaults.

## Dependency minimization

Portable modules should depend on interfaces/capabilities, not specific accidental providers where practical. Example: exercise accountability can work manually and optionally consume a supported wearable/activity adapter. Appointment reconciliation can accept email evidence and project to a calendar interface, while manual appointments remain usable when Gmail is absent.

A missing optional dependency fails that adapter/module path only. Avoid central middleware whose failure disables unrelated life domains.

## New-user onboarding

1. Fork the public upstream or use an audited snapshot.
2. Run `START_HERE.md` and `CAPABILITY_DISCOVERY.md`.
3. Build the user's configuration from interview plus reachable existing evidence; never reuse reference deployment state.
4. Commit/push the first coherent personal deployment checkpoint after approval.
5. Pin core and selected feature versions before scheduled writes.
6. Let the user's fork evolve independently.
7. Offer reusable personal improvements upstream only through the opt-in portability gate.

This supports easy inherit → customize → improve → share → re-inherit cycles without turning Git into a database dump of people's lives.