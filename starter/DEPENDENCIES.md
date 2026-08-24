# LyfeOS First-Boot Dependencies

First boot verifies every selected dependency before claiming a module is installed. Missing access blocks only the dependent module. Before asking the user to connect anything, read `CAPABILITY_DISCOVERY.md` and inspect already available tools/connectors/plugins when the platform permits it. Never ask a non-technical user for passwords, access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Dependency-minimization rule

Default new-user architecture:

- **Git:** required durable source/version lineage for code/policy/schema/config/features/tests.
- **Google Sheets:** default structured mutable state authority.
- **Google Drive:** default evidence/document authority when selected modules need retained files.
- **Google Calendar:** optional projection/reminder surface.
- Gmail, finance, fitness/wearable, maps/weather/travel, and other integrations are optional module adapters.

A supported database may replace Sheets when deliberately selected. Do not require both Sheets and another database for the same data class.

Prefer one canonical authority per data class, adapters around it, one consolidated scheduler per purpose/cadence, Calendar events for event-specific reminders, and write readback at module boundaries.

## Git repository — required source lineage

Git stores durable policy, schemas, tests, migrations, onboarding, selected-module configuration, authority references, and portable/personal feature code. Routine mutable operational records do **not** live in Git.

A deployment repository may be public or private by explicit owner choice. Public source requires the public-source audit and must not contain secrets, credentials, mutable operational exports, Gmail/receipt bodies, financial account data, medical records, school submissions, or unintended personal information.

### Upstream lifecycle

1. fork/clone or seed from an exact audited public LyfeOS release/commit/tree;
2. record upstream provenance;
3. verify Git read/write capability;
4. generate non-secret deployment config, schema/migrations, feature lock, authority references, and policy;
5. validate, commit/push, and read back the coherent first-boot source checkpoint;
6. after standing Git authorization, lasting behavior/config/schema/feature changes automatically validate, commit, push, and verify remote state.

Automatic Git versioning does not imply force-push, visibility change, release, merge, or public contribution authority.

## Structured state authority — required

Default: Google Sheets.

First boot creates/selects and verifies the structured state authority before state-changing automation begins. Read `STATE_AUTHORITY_MODEL.md`.

At minimum selected modules can provision:
- `Authority Registry`;
- `Interview Ledger`;
- their own canonical tables/schemas.

Every state mutation is read → dedupe/correlate → write → readback → verify. If the authority is unavailable, stop that module and report `Action Required — <authority> unavailable` rather than substituting chat or Git.

## Google Drive / evidence store

Default retained evidence/document store when selected modules need files. Use stable file IDs/links from canonical state rows. Do not create Drive merely because it exists if the deployment has no retained-file use case.

Typical classes include receipts, manuals/reference, recipe bodies/images, administrative documents, and other bulky originals.

## Shared authorities

First boot asks whether any domain should be shared with another person.

Support either:
- explicit provider sharing of an existing workbook/folder; or
- a separate scoped shared workbook/folder for household, meal planning, travel, projects, etc.

Record the scope/grant in the Authority Registry and verify provider read/write access after sharing. Never infer family access.

## Capability discovery before connection prompts

Inspect relevant already-available capabilities before telling the user to connect another service. Reuse a verified existing connector when it satisfies the module contract. If a selected workflow needs an unavailable capability, search supported plugins/apps when possible and explain the permission boundary.

Never invent a Garmin, finance, calendar, email, or other connection merely because a workflow would be nicer with one.

## Gmail / email

Optional evidence adapter for selected appointment, receipt/order, actionable-mail, school/admin, or document workflows. Verify bounded full-message read capability for the relevant class. Label/archive writes are separate. Sending remains approval-gated.

### Appointment reconciliation

For approved appointment-email automation:
- email supplies evidence;
- the structured state authority owns canonical appointment/reconciliation state;
- Calendar is an optional projection/reminder surface;
- public provider research may enrich provider specialty/type when evidence is unclear and research is allowed.

A Gmail failure blocks email-driven reconciliation, not manual appointment management or unrelated modules.

## Google Calendar

Optional projection/reminder adapter. Verify read access first. After approval, verify bounded create/update and read it back.

For each projected appointment verify event ID, target calendar, title/type, date/time/timezone, reminder policy, and canonical source linkage. Revisions update the same linked event.

Support multiple reminders, including day-before, a configured morning-of local clock time, and relative reminders such as one hour before. Fixed local-clock reminders must be converted using the event's IANA timezone, not a static offset.

Event-specific reminders live in Calendar rather than generating one ChatGPT task per appointment.

## Fitness / wearable / activity integrations

Optional evidence adapters. If a relevant connector/plugin is already available, offer it for selected exercise/accountability workflows. Verify what fields it exposes. Use only user-selected supported metrics.

A wearable connection must never become a prerequisite for basic exercise planning, and activity data must not be treated as diagnosis/injury evidence.

## Financial accounts

Optional evidence adapter for account-level charge/refund/cash-flow reconciliation. Use the product's account-linking flow; never request banking credentials in chat. Inspect coverage/freshness before conclusions.

## Maps, weather, and travel capabilities

Optional current-input adapters for hiking, outdoor, route, vacation, or trip planning. Keep planning usable without them.

## Scheduled Tasks and canonical timezone integrity

Scheduled Tasks are optional unless the user wants recurring briefs/digests/accountability/condition watches.

Treat scheduling as an evidence chain:
1. canonical VEVENT/RRULE/TZID/local time;
2. exactly the intended enabled dispatcher, correct timing mode, no duplicate;
3. expected notification state;
4. runtime canonical-clock gate;
5. subsequent actual firing/Run Log.

The runtime canonical-clock gate converts the current instant to the configured IANA timezone, e.g. `now.astimezone(ZoneInfo(canonical_timezone))`, then compares that local clock to the intended slot. Never compare against travel/device timezone or a manual UTC offset. This naturally handles DST.

A field called `default_timezone` is authoritative only when the provider contract explicitly defines it as persistent task execution state.

Keep the fewest dispatchers necessary. Do not create per-order, per-appointment, or hidden retry tasks.

## Existing chats, files, and File Library

Use current conversation and accessible uploaded/File Library material when relevant. Do not claim global search over arbitrary old ChatGPT conversations.

If useful prior-chat material is inaccessible, ask the user to open/share/export it or move durable content into the selected canonical authority. Once ingested, the old chat should not remain the sole authority.

## Dependency gate output

Before provisioning, summarize each selected dependency as required module(s), existing/available capability, read verified / write verified / missing / partial, exact next action, and whether unrelated onboarding can continue.
