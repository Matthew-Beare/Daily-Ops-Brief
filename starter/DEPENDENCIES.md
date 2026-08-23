# LyfeOS First-Boot Dependencies

First boot verifies every selected dependency before claiming a module is installed. Missing access blocks only the dependent module. Before asking the user to connect anything, read `CAPABILITY_DISCOVERY.md` and inspect already available tools/connectors/plugins when the platform permits it. Never ask a non-technical user for passwords, access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Dependency-minimization rule

The portable starter has one required durable dependency: a **private user-owned Git repository** that is both the canonical personal-state authority and the deployment source/version history.

Core onboarding, state, module selection, configuration, tests, and recovery must not require Gmail, Calendar, Drive, finance, fitness, maps/weather, or another optional service. Optional modules/adapters declare the smallest connector set they need and fail independently.

Prefer:
- one canonical personal-state authority: private Git;
- one user-owned Git lineage;
- provider adapters around that state;
- one consolidated scheduler per purpose/cadence;
- Calendar events for event-specific reminders;
- remote readback after every Git state transaction.

A connector failure must not cascade into unrelated modules merely because somebody once thought a giant integration layer sounded elegant.

## Private Git repository — required state and source

LyfeOS stores personal mutable state plus durable policy, schemas, tests, migrations, onboarding, selected-module configuration, provider references, and portable/personal feature code in the user's private deployment repository.

Read `GIT_STATE_MODEL.md` before provisioning.

### Safe upstream lineage

A normal GitHub fork of a public repository is public. Personal-state mode therefore must not write state into a normal public fork.

Default setup:
1. pin an exact audited public LyfeOS release/commit/tree;
2. create a private repository owned by the user;
3. seed/import the pinned upstream source into it;
4. record upstream provenance and update target;
5. connect GitHub and verify a harmless read;
6. separately verify write capability with one bounded approved mutation and remote readback;
7. read provider metadata and prove the personal-state repository is private;
8. after provisioning approval, create the initial `state/` model plus deployment config/features/policy;
9. run validation/privacy/source checks;
10. commit/push/read back the coherent first-boot checkpoint.

If a platform supports a genuinely private fork of the public upstream, it may satisfy the same contract. A public fork is code-only until personal state is moved into a private deployment repository.

### State mutation verification

Every coherent state mutation or reconciliation cycle:
1. reads the current remote HEAD and affected state;
2. appends stable immutable event(s);
3. updates derived/current snapshot(s);
4. validates;
5. commits;
6. pushes fast-forward only;
7. reads back remote commit/state.

If the branch moved, re-read and reconcile. Never force-push personal state history. If Git is unavailable, the state-changing operation stops rather than falling back to chat memory or an unversioned shadow database.

Standing Git authorization may cover later transactional commits/pushes. Merge/publication/visibility/destructive-history authority remains separate.

## Public-source gate

The public-source gate applies to the public upstream, public code-only forks, and sanitized portable feature contributions. Personal state must never be included in an upstream contribution.

Before a public release or contribution:
1. run the public-source history/current-tree audit;
2. run starter privacy audit;
3. run repository validation and all tests;
4. exclude `state/`, private deployment configuration, credentials, private provider/evidence references, message/receipt bodies, medical details, school records, and other private data;
5. use synthetic fixtures for portable examples;
6. show the exact public diff before publication.

Public visibility is not itself a failure for upstream source. **Unintended personal-state exposure is.**

## Capability discovery before connection prompts

First boot should inspect relevant already-available capabilities before telling the user to connect another service. Reuse a verified existing connector when it satisfies the module contract. If a selected workflow needs an unavailable external capability, search supported plugins/apps when the product permits it, explain the benefit and permission boundary, and let the user choose.

Never invent a Garmin, finance, calendar, email, or other connection merely because a workflow would be nicer with one.

## Gmail / email

Optional evidence adapter for selected appointment, receipt/order, actionable-mail, school/admin, or document workflows. Verify bounded full-message read capability for the relevant class. Label/archive writes are separate. Sending remains approval-gated.

Email is not the canonical state authority. Accepted/reconciled facts and source references commit into Git state.

### Appointment reconciliation

For approved appointment-email automation:
- Gmail/email supplies evidence when connected;
- private Git is canonical appointment/reconciliation state;
- Calendar is an optional projection/reminder adapter.

Setup defines allowed appointment classes/senders, confidence/ambiguity behavior, target calendar when enabled, and sensitive-detail policy. A Gmail failure blocks email-driven reconciliation, not manual Git-backed appointment management or unrelated LyfeOS modules.

## Google Calendar

Optional projection/reminder adapter. Verify read access first. After approval, verify a bounded create/update and read it back.

For every projected appointment/event verify event ID, target calendar, title, date/time/timezone, reminder policy, and source linkage. Then commit the verified linked event ID/status into Git state and read the Git commit back. Revisions update the same linked event.

Event-specific reminders should live in Calendar instead of generating one ChatGPT task per appointment.

## Drive / Docs / Sheets / file services

Optional evidence/import/export adapters, not required personal-state authorities for new-user deployments.

Use them when a selected workflow needs bulky original documents, collaboration, native office files, or existing evidence. Store stable provenance/reference IDs and accepted canonical facts in Git state. Large binaries do not need to be copied into Git merely to claim state ownership.

## Fitness / wearable / activity integrations

Optional evidence adapters. If a relevant connector/plugin is already available, offer it for selected exercise/accountability workflows. Verify what fields it actually exposes. Use only user-selected supported metrics.

Accepted routine/activity facts may be committed into Git state. A wearable connection must never become a prerequisite for basic exercise planning, and activity data must not be treated as diagnosis/injury evidence.

## Financial accounts

Optional evidence adapters for account-level charge/refund/cash-flow reconciliation. Use the product's account-linking flow; never request banking credentials in chat. Inspect coverage/freshness before conclusions.

Accepted reconciliation conclusions/state commit into private Git; provider credentials and raw authentication data do not.

## Maps, weather, and travel capabilities

Optional current-input adapters for hiking, outdoor, route, vacation, or trip planning. Keep planning usable without them. Accepted plans/tasks can be committed into Git state; live weather/routes remain provider-time inputs.

## Scheduled Tasks and timezone integrity

Scheduled Tasks are optional unless the user wants recurring briefs/digests/accountability/condition watches.

Treat scheduling as an evidence chain:
1. **Schedule definition:** canonical VEVENT/RRULE/TZID/local time.
2. **Dispatcher state:** exactly the intended job is enabled with correct timing mode and no active **duplicate**.
3. **Notification state:** expected **notification** delivery is enabled.
4. **Observed execution:** a subsequent **actual firing** or canonical Run Log lands in the intended local slot.

A field called `default_timezone` is authoritative only when the **provider contract** explicitly defines it as persistent task execution state. Travel/device timezone is context.

Keep the fewest dispatchers necessary. Do not create per-order, per-appointment, or hidden retry tasks. Calendar events own event-specific reminders when Calendar is enabled.

## Existing chats, files, and File Library

Use current conversation and accessible uploaded/File Library material when relevant. Do not claim global search over arbitrary old ChatGPT conversations.

If an existing meal plan, recipe collection, project, or other useful system lives only in an inaccessible old chat, ask the user to open/share/export it. Once approved and normalized, its durable state should be committed into the private Git deployment so the old chat is no longer required.

## Local/private devices

A NAS, home server, phone-local store, or LAN-only service requires an explicit supported bridge. Never imply cloud ChatGPT can silently reach an unconnected private network.

## Dependency gate output

Before provisioning, summarize each selected dependency as: required module(s); existing/available capability; read verified / write verified / missing / partial; exact next action; and whether unrelated onboarding can continue.

Do not enable scheduled/provider writes until their own authority/schedule/notification checks are verified. Do not call scheduler repair complete until a real firing proves it.