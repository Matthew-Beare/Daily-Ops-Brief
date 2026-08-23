# LyfeOS First-Boot Dependencies

First boot verifies every selected dependency before claiming a module is installed. Missing access blocks only the dependent module. Before asking the user to connect anything, read `CAPABILITY_DISCOVERY.md` and inspect already available tools/connectors/plugins when the platform permits it. Never ask a non-technical user for passwords, access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Dependency-minimization rule

Core onboarding, Git lineage, module selection, configuration, tests and recovery must not require Gmail, Calendar, finance, fitness, maps/weather, or another optional service. Optional modules declare the smallest connector set they need and fail independently.

Prefer one canonical authority per data class, one user-owned Git lineage, adapters around optional integrations, one consolidated scheduler per purpose/cadence, and Calendar events for event-specific reminders. A connector failure must not cascade into unrelated modules merely because somebody once thought a giant integration layer sounded elegant.

## Git repository — required durable source

LyfeOS stores durable policy, schemas, tests, migrations, onboarding, selected-module configuration, authority references and portable/personal feature code in Git. Mutable personal records remain in selected live authorities such as Sheets/Drive/database services.

A deployment repository may be **public or private by explicit user choice**. Public source requires the public-source audit and must not contain secrets, credentials, mutable operational exports, Gmail/receipt bodies, financial account data, medical records, school submissions, or other information the user did not deliberately choose to publish.

### Fork-first setup

1. Fork the public LyfeOS upstream into a repository the user controls, or use an audited clean snapshot.
2. Connect GitHub and verify a harmless repository/file read.
3. Separately verify write capability with one bounded approved branch/file mutation and remote readback.
4. Read provider repository metadata and record public/private visibility plus exact upstream commit/tag provenance.
5. First boot writes the user's non-secret deployment config, module/feature lock, authority references, schemas/migrations and generated policy.
6. Run validation/privacy/source checks, commit/push the coherent first-boot checkpoint, and read it back before calling source initialization complete.
7. Standing Git authorization may cover later durable commits/pushes. Merge/publication remains the user's configured policy.

A fork must never inherit another user's live Google IDs, schedules, aliases, records or state merely because reference code is present.

## Public-source gate

Before a public release, public fork handoff, public deployment-source push, or upstream portable-feature contribution:

1. run the public-source history/current-tree audit available in the source;
2. run starter privacy audit;
3. run repository validation and all tests;
4. verify local config, credentials, mutable exports, message/receipt bodies and account data are absent;
5. verify generated source contains only information the user intentionally allows in Git.

Public visibility is not itself a failure. **Unintended data exposure is.**

## Capability discovery before connection prompts

First boot should inspect relevant already-available capabilities before telling the user to connect another service. Reuse a verified existing connector when it satisfies the module contract. If a selected workflow needs an unavailable external capability, search supported plugins/apps when the product permits it, explain the benefit and permission boundary, and let the user choose. Never invent a Garmin, finance, calendar, email, or other connection merely because a workflow would be nicer with one.

## Google Drive / Docs / Sheets or selected state/evidence store

Needed only for modules that select these services as canonical state/evidence. Verify harmless read first; write verification occurs after provisioning approval. Read-only access is insufficient for automatic provisioning.

## Gmail

Required only for selected email-driven modules such as appointments, receipts/orders, actionable-mail triage, school/admin evidence or document intake. Verify bounded full-message read capability for the relevant class. Label/archive writes are separate. Sending remains approval-gated.

### Appointment reconciliation

For email-derived appointment automation, Gmail plus the selected Calendar/state authority are dependencies. Setup must define allowed appointment classes/senders, confidence/ambiguity behavior and sensitive-detail policy. A Gmail failure blocks appointment-email reconciliation, not Calendar/manual appointment management or unrelated LyfeOS modules.

## Google Calendar

Required only for calendar reads or selected Calendar Projection classes. Verify read access first. After approval, verify a bounded create/update and read it back.

For every projected appointment/event verify event ID, target calendar, title, date/time/timezone, reminder policy and canonical source linkage. Revisions update the linked event. Event-specific reminders should live in Calendar instead of generating one ChatGPT task per appointment.

## Fitness / wearable / activity integrations

Optional. If a relevant connector/plugin is already available, offer it as evidence for selected exercise/accountability workflows. Verify what fields it actually exposes before relying on it. Use only user-selected supported metrics. A wearable connection must never become a prerequisite for basic exercise planning, and activity data must not be treated as medical diagnosis or injury evidence.

## Maps, weather and travel capabilities

Optional for selected hiking, outdoor, route, vacation or trip-planning workflows. Keep planning usable without them; live weather/routes require the relevant current capability at execution time.

## Scheduled Tasks and timezone integrity

Scheduled Tasks are optional unless the user wants recurring briefs/digests/accountability/condition watches.

Treat scheduling as an evidence chain:
1. **Schedule definition:** canonical VEVENT/RRULE/TZID/local time.
2. **Dispatcher state:** exactly the intended job is enabled with correct timing mode and no active **duplicate**.
3. **Notification state:** expected **notification** delivery is enabled.
4. **Observed execution:** a subsequent **actual firing** or canonical Run Log lands in the intended local slot.

A field called `default_timezone` is authoritative only when the **provider contract** explicitly defines it as persistent task execution state. Travel/device timezone is context.

Keep the fewest dispatchers necessary. Do not create per-order, per-appointment or hidden retry tasks. Calendar events own event-specific reminders when Calendar is the selected projection surface.

## Financial accounts

Optional for account-level charge/refund/cash-flow reconciliation and separate from receipt-detected spending. Use the product's account-linking flow; never request banking credentials in chat. Inspect coverage/freshness before conclusions.

## Existing chats, files and File Library

Use current conversation and accessible uploaded/File Library material when relevant. Do not claim global search over arbitrary old ChatGPT conversations. If an existing meal plan, recipe collection, project or other useful system lives only in an inaccessible old chat, ask the user to open/share/export it or move durable information into an accessible canonical authority.

## Local/private devices

A NAS, home server, phone-local store, or LAN-only service requires an explicit supported bridge. Never imply cloud ChatGPT can silently reach an unconnected private network.

## Dependency gate output

Before provisioning, summarize each selected dependency as: required module(s); existing/available capability; read verified / write verified / missing / partial; exact next action; and whether unrelated onboarding can continue. Do not enable scheduled writes until their authorities and schedule/notification checks are verified; do not call scheduler repair complete until a real firing proves it.