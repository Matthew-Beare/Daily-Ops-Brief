# LyfeOS Starter Versioning and New-User Deployments

## Repository roles

- This repository is the current **public LyfeOS upstream and reference implementation**.
- `starter/` is the sanitized portable onboarding/distribution boundary. New users start there, not from the current deployment's authority IDs or mutable state.
- A user's deployment source lives in a repository they control. It may be public or private by explicit choice, subject to the source-audit rules.
- Mutable operational records remain in that user's selected authorities and are never inherited from Git.

A future standalone starter repository may make packaging cleaner, but it is **not a prerequisite** for using the current public starter.

## Current public installation paths

### Simple fork path

1. Fork the public repository into an account/repository the user controls.
2. Connect that fork to ChatGPT and verify read/write capability.
3. Start with `starter/START_HERE.md`.
4. First boot records that user's repository visibility, canonical timezone, authorities, modules, schedules, approval boundaries, and state model.
5. Never copy current-deployment Google IDs, aliases, schedules, vehicle records, Gmail content, receipts, or mutable state into the new deployment.
6. Run public-source/starter privacy audit, repository validation, and all tests before enabling scheduled writes.

The fork contains public reference history, including the reference implementation. That is acceptable because the upstream is intentionally public. **Reference configuration is not deployment state.** First boot must build the new user's configuration from their interview and connected authorities.

### Clean portable-snapshot path

For users who do not want the reference implementation in their repository:

1. pin an exact audited upstream commit;
2. copy/export only the documented portable starter files and portable feature/schema/test tooling;
3. create a new repository owned by the user;
4. run starter privacy/public-source audits and CI in that repository;
5. record the upstream commit as provenance.

This path provides a clean deployment tree without depending on another user's configuration, while the fork path remains easier for ordinary users.

## Repository visibility

Public and private are both supported.

- **Public:** source must pass public-source audit and contain no secrets, credentials, mutable operational exports, private message/receipt bodies, account data, or other information the user did not intentionally publish.
- **Private:** the same no-secrets rule still applies. Private Git is not a substitute for proper secret storage.

Repository visibility must come from provider metadata, not prose. Changing visibility is a deliberate repository-owner action.

## Release model

Use semantic versions when tagging public releases:

- `v0.1.0-beta.1` — first public beta after forensic repository audit, full CI, starter privacy/public-source audit, and a synthetic first-boot pass;
- `v0.1.0` — first stable release after at least one clean real-user deployment from the public starter;
- `v0.2.0` — backwards-compatible modules/onboarding behavior;
- `v0.2.1` — bugfix-only release;
- `v1.0.0` — stable compatibility contract after migrations/upgrade paths are proven.

Feature branches are not installation targets. `main` is the public release-candidate/current release line only after CI and merge authority pass.

## Non-technical first boot

The normal user should not need Git CLI knowledge or database design.

1. Fork the public upstream or use a clean audited starter snapshot.
2. Connect the repository plus whichever Drive/Sheets/Docs/Gmail/Calendar/finance services they select.
3. Run `starter/START_HERE.md`.
4. First boot asks four kickoff questions, performs the adaptive whole-life interview, recommends a Minimum Useful Setup, verifies dependencies with harmless reads, and requests one bounded provisioning approval.
5. After approval, setup creates or validates that user's canonical resources, writes only durable source/configuration appropriate for that repository's visibility, and verifies remote/readback state.
6. Establish standing Git versioning authorization if wanted.
7. User-specific mutable data remains only in that user's selected live authorities.

## Deployment version record

Persist a small non-secret record containing:

- `core_version` or pre-release snapshot identifier;
- exact upstream commit/tag;
- schema version;
- selected portable feature IDs and versions in `features.lock.json`;
- migration version/checksum state;
- local deployment policy version;
- chosen repository visibility (`public` or `private`).

Never put mutable operational records or secrets in the version record.

## Updating a deployment

1. fetch/compare the next audited upstream tag/commit;
2. read release notes and migrations;
3. run synthetic compatibility tests;
4. apply idempotent migrations to a backup/test copy when required;
5. review the source/configuration delta;
6. verify CI and data migrations;
7. merge under that deployment owner's merge policy.

Do not silently reset a deployment to upstream or overwrite deployment-specific policy/configuration.

## Portable feature development

Portable modules follow `SHARED_FEATURE_WORKFLOW.md`: behavior, schemas, placeholders, synthetic fixtures, and tests may move between deployments; mutable personal data does not. Features can originate in any deployment, but the contribution exported upstream must pass privacy/public-source review before merge.

## Production flow

1. develop on a feature branch;
2. keep incomplete multi-file checkpoints isolated from release CI when practical;
3. run repository validation, public-source audit, starter privacy audit, root tests, runtime tests, and starter tests;
4. open/ready the integration PR only when coherent;
5. merge to `main` only under the repository owner's merge authority;
6. verify the merge commit and main CI before calling the release healthy;
7. never commit mutable state or secrets merely because the repository is public.