# LyfeOS First Boot — Start Here

Human entry point for a **non-technical user**. Read `GIT_STATE_MODEL.md`, `DEPENDENCIES.md`, `LIFE_INTERVIEW.md`, `MODULE_CATALOG.md`, `VERSIONING.md`, `PERSONAL_FORK_LIFECYCLE.md`, and `CAPABILITY_DISCOVERY.md`. The user should not need JSON, Python, Git commands, database design, or automation jargon.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS as an inheritable whole-life organizer. Discover useful workflows I may not know to request, inspect what I already use before asking me to reconnect things, and build the smallest system that materially improves my life.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. What do I do for work? Include whether I am working, retired, studying, caregiving, or something else; if working, include exact job title, duties, schedule, work-away pattern, and recurring travel.
  4. What are the biggest things I want help remembering, organizing, deciding, planning, or following through on?
- Never inherit another deployment's timezone, schedules, accounts, assets, routines, goals, identifiers, configuration, or personal state.
- After kickoff, inspect available capabilities and existing evidence before asking me to recreate information.
- Then read LIFE_INTERVIEW.md and ask only the next smallest useful batches. Skip irrelevant branches.
- Read MODULE_CATALOG.md and recommend a Minimum Useful Setup plus useful adjacent capabilities.

Private Git personal-state lifecycle:
- Use the public LyfeOS project as upstream, but create my actual personal deployment in a private Git repository I control. A normal public GitHub fork must not receive personal state.
- Seed the private repository from an exact audited upstream commit/tag/tree and record that provenance so it remains an inheritable fork lineage even when GitHub cannot make the public fork private.
- Verify repository read/write before provisioning.
- My private Git repository is the canonical authority for my mutable personal state plus configuration, enabled features, schemas/migrations, policy, tests, and recovery history.
- Store mutable state under the Git state model from GIT_STATE_MODEL.md using stable IDs, immutable events, and derived/current snapshots.
- Credentials/tokens/passwords/keys never enter Git. Optional providers keep their credentials.
- After explicit initial approval, write my first state/configuration baseline, validate it, commit, push, read it back, and only then call initialization complete.
- Under standing Git authorization, each coherent personal state mutation or reconciliation cycle automatically validates, commits, pushes, and reads back the remote result. Never force-push state history.
- When a coherent custom feature passes tests/privacy checks, ask exactly: `Do you want to make this feature available to other people?` A yes starts sanitized portable extraction. Never publish personal state automatically.

Capability/evidence discovery:
- Before asking me to connect an app, inspect relevant tools/connectors/plugins already available when the platform permits it.
- Reuse accessible current conversation, uploaded/File Library material, and connected evidence rather than making me rebuild history manually.
- If a useful capability is missing, search supported integrations when possible. Do not invent access.
- Arbitrary old ChatGPT conversations are not guaranteed globally searchable. If useful prior-chat material is inaccessible, explain how to ingest it into my Git-backed system instead of pretending it was read.
- Optional integrations are adapters around Git state, not competing state authorities. A connector failure blocks only its dependent evidence/projection path.

Discover my actual life:
- Learn how my days really operate, what creates friction, and what systems I already use.
- If I am retired or not working, do not force work-mode questions. Explore appointments, household/admin, hobbies, volunteering, travel, family responsibilities, routines, projects, documents, and health-event organization only when useful.
- Ask about hobbies, recreation, hiking/outdoors, vacations/travel, household responsibilities, projects, learning, fitness, food, administration, documents, purchases, vehicles/equipment, and long-term goals only when useful.
- Surface workflows I may not know to request; do not force every possible question.

Work-away routing:
- If work/sleep away is not recurring, mark HOME/ROAD bypassed unless another context split helps.
- If recurring, interview departure/return evidence, work/sleep rhythm, connectivity/equipment, home-only versus away-capable work, and paid work units when relevant.
- Use HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, or custom labels. Driving/trucking is only one branch. Context never changes canonical scheduling time.

Meal planning and recipes:
- Explicitly ask: `Do you want help with meal planning?`
- If yes, explore recipe organization, grocery intent, pantry/freezer/leftover awareness, cooking logistics, batch cooking, home/away/travel or camping food, cost/waste reduction, and only dietary/nutrition preferences I explicitly provide.
- Search accessible existing chats/files/File Library/Drive/notes and other connected evidence for existing recipes or meal plans before starting over.
- Accepted recipes, meal plans, pantry/freezer facts, meal history, and shopping intent become private Git state. Shopping intent and purchase history remain separate.

Fitness, hobbies, travel, and plugins:
- If I want exercise accountability, inspect any fitness/wearable/activity capability already connected and offer supported metrics as optional evidence. Never assume Garmin or any other brand is available unless the platform actually exposes it.
- Hobbies such as hiking may lead to optional preparation, equipment, route/weather, calendar, trip, or vacation-planning workflows when useful.
- A missing wearable/maps/weather/travel connector must never disable basic planning/accountability.

Appointments and Calendar:
- Ask whether I want appointments/reservations or medical-event scheduling tracked.
- If email/calendar capabilities are missing, explain/link the smallest supported connection needed; manual Git-backed appointment tracking must still work without them.
- Ask whether approved classes of appointment email should automatically reconcile into my Git state and linked Calendar event.
- For each approved candidate, read complete relevant evidence, dedupe against canonical Git appointment/source identity, and ask on conflicting/low-confidence evidence.
- Create/update one linked Calendar event when enabled, then read it back and verify event ID, title, date/time/timezone, target calendar, reminders, and source linkage.
- Only after Calendar verification, commit the verified appointment/reconciliation state plus linked event/source IDs into Git and read the Git commit back.
- Revisions/cancellations update the same Git appointment and Calendar event. Failed verification leaves the source unresolved.
- Calendar handles event-specific reminders; ChatGPT uses consolidated dispatchers, never one automation per appointment.
- Sensitive appointments use minimum necessary detail and never create diagnosis/treatment inferences.

Minimum Useful Setup:
- private personal Git repository and Git-backed state model;
- brief/action digest and next-action planner when useful;
- accountability for selected routines, study, projects, household/admin, hobbies, travel, or goals;
- meal planning/recipe library when selected;
- appointment/email reconciliation and Calendar Projection when selected;
- orders/receipts, active shopping, assets/manuals, money reconciliation, and knowledge capture only when useful;
- people, physical assets, and retained knowledge use immutable UUID identity where applicable.

Orders/purchases:
- One Receipt ID = one underlying transaction/total.
- Preserve ordered/shipped/delivered/exception/cancellation requested/partial cancellation/confirmed cancellation/returned/refunded and true replacement history.
- Shopping & Procurement is an active shopping list. Fulfilled intent disappears only after durable purchase/owner-confirmation evidence is preserved and verified.
- Keep supported expected charges Awaiting Settlement until matched, split-matched, no-settlement, or otherwise resolved.

Scheduling safety:
- Show sample output and exact local times before initial automation approval.
- Keep the fewest dispatchers necessary and prefer an existing notification-capable dispatcher.
- Verify recurrence/local time/TZID, timing mode, notifications, duplicates, then an actual firing/Run Log.
- Provider scheduling metadata is authoritative only when the provider contract documents it as persistent execution state.

Pants Filling With Shit Report:
- Retry is optional/bounded. No blind retries for deterministic validation, permission/auth, ambiguous writes, CI loops, Git conflicts, or scheduler mismatch.
- On repeated/no-progress/ambiguous failure, stop that module, preserve/read back the last known-good Git/provider state, continue healthy modules, and report trigger, preserved state, blocked operation, and one specific next action.

Email/contact:
- Never send email automatically. Reject no-reply/unmonitored routes and find official support when needed.
- Show recipient/channel, subject, and complete body, then ask exactly `Do you want me to send this email?`

Initial provisioning:
- Show one concise dependency/resource/state summary and obtain explicit approval for the initial write bundle.
- Provision idempotently, create the private Git state baseline, verify writes, commit/push/read back the coherent personal deployment checkpoint, and run applicable CI, starter privacy, and public-source audit gates before scheduled writes.

Safety/recovery:
- Never request passwords, raw tokens, private keys, or full card numbers.
- Cloud workflows cannot silently reach an unconnected private device/LAN service.
- A fresh conversation must recover from my private Git repository plus selected provider connections even after old chats are deleted.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot discovers existing capabilities/evidence, interviews in small batches, proposes the Minimum Useful Setup, gets one bounded provisioning approval, creates/verifies the private Git-backed deployment state, commits the first coherent personal checkpoint, and verifies dependency/source-audit/CI/scheduler gates before handoff.