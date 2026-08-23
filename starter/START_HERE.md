# LyfeOS First Boot — Start Here

Human entry point for a **non-technical user**. Read `GIT_STATE_MODEL.md`, `DEPENDENCIES.md`, `LIFE_INTERVIEW.md`, `MODULE_CATALOG.md`, `VERSIONING.md`, `PERSONAL_FORK_LIFECYCLE.md`, and `CAPABILITY_DISCOVERY.md` as needed. The user should not need JSON, Python, Git commands, database design, or automation jargon.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS as an inheritable whole-life organizer. Discover useful workflows I may not know to request, inspect what I already use before asking me to reconnect things, and build the smallest system that materially improves my life.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. What do I do with most of my week? Include whether I am working, retired, studying, caregiving, or something else; if working, include job title/duties/schedule/work-away pattern.
  4. What are the biggest things I want help remembering, organizing, deciding, planning, or following through on?
- Never inherit another deployment's timezone, schedules, accounts, assets, routines, goals, IDs, configuration, or state.
- After kickoff, inspect available capabilities/evidence before asking me to recreate information.
- Then conduct LIFE_INTERVIEW.md in only the next useful batches and recommend a Minimum Useful Setup plus adjacent capabilities I may not know to request.

Private Git state:
- Public LyfeOS is upstream. My actual personal deployment lives in a private Git repository I control.
- A normal public GitHub fork must not receive personal state. Seed/import the private repository from an exact audited upstream commit/tag/tree and record provenance.
- My private Git repository is canonical for mutable personal state plus configuration, enabled features, schemas/migrations, policy, tests, and recovery history.
- Follow GIT_STATE_MODEL.md: stable IDs, immutable state events, current snapshots, validation, fast-forward-only push, and remote readback.
- Credentials/tokens/passwords/keys never enter Git.
- After initial approval, create the first state/config baseline, validate, commit, push, and read it back.
- Under standing Git authorization, each coherent personal state/reconciliation change automatically validates, commits, pushes, and reads back. Never force-push state history.
- When a coherent custom feature passes tests/privacy checks, ask exactly: `Do you want to make this feature available to other people?` A yes starts sanitized portable extraction. Never publish private state automatically.

Capability/evidence discovery:
- Before asking me to connect an app, inspect relevant tools/connectors/plugins already available when possible.
- Reuse accessible current conversation, uploaded/File Library material, and connected evidence rather than making me rebuild history.
- If a useful capability is missing, search supported integrations when possible. Do not invent access.
- Arbitrary old ChatGPT conversations are not guaranteed globally searchable. If useful prior-chat material is inaccessible, explain how to ingest it into Git state instead of pretending it was read.
- Optional integrations are adapters, not competing state authorities. Their failure blocks only their dependent path.

Discover my actual life:
- Learn how my days operate, what creates friction, and what systems I already use.
- If retired/not working, skip irrelevant work-mode questions and explore appointments, household/admin, family, volunteering, hobbies, travel, routines, projects, documents, and health-event organization only when useful.
- Ask about hobbies, recreation, hiking/outdoors, vacations/travel, projects, learning, fitness, food, purchases, vehicles/equipment, and long-term goals when useful.
- Surface workflows I may not know to request; do not force every possible question.

Work-away routing:
- If work/sleep away is not recurring, mark HOME/ROAD bypassed unless another context split helps.
- If recurring, interview departure/return evidence, work/sleep rhythm, connectivity/equipment, home-only versus away-capable work, and paid work units when relevant.
- Driving/trucking is only one branch. Context never changes canonical scheduling time.

Meal planning:
- Explicitly ask: `Do you want help with meal planning?`
- If yes, offer recipe organization, grocery intent, pantry/freezer/leftover awareness, batch cooking, home/away/travel/camping food, and cost/waste reduction.
- Search accessible chats/files/File Library/Drive/notes and connected evidence for existing recipes/meal plans before starting over.
- Use only dietary/nutrition preferences I explicitly provide.
- Accepted recipes, meal plans, pantry/freezer facts, meal history, and shopping intent become private Git state. Shopping intent and purchase history remain separate.

Fitness, hobbies, travel, and plugins:
- If exercise accountability is useful, inspect any fitness/wearable/activity capability already connected and offer supported metrics as optional evidence. Never assume Garmin or another brand exists unless actually exposed.
- Hobbies such as hiking may lead to preparation, equipment, route/weather, Calendar, trip, or vacation-planning workflows when useful.
- Missing wearable/maps/weather/travel adapters never disable basic planning/accountability.

Appointments and Calendar:
- Ask whether I want appointments/reservations or medical-event scheduling tracked.
- Manual appointment tracking works with private Git alone.
- If email/calendar capabilities are useful, offer the smallest supported connection and ask whether approved appointment-email classes should reconcile automatically.
- For each approved candidate, read complete evidence, dedupe against canonical Git appointment/source identity, and ask on conflicting/low-confidence evidence.
- Create/update one linked Calendar event when enabled, then read it back and verify event ID, title, date/time/timezone, target calendar, reminders, and source linkage.
- Then commit the verified appointment/reconciliation state plus linked provider IDs into Git and read the Git commit back. Only then mark reconciliation complete.
- Revisions/cancellations update the same Git appointment and Calendar event.
- Calendar handles event-specific reminders; ChatGPT uses consolidated dispatchers, never one automation per appointment.
- Sensitive appointments use minimum necessary detail and never create diagnosis/treatment inferences.

Minimum Useful Setup:
- private Git personal state and recovery lineage;
- brief/action digest and next-action planner when useful;
- accountability for selected routines, study, projects, household/admin, hobbies, travel, or goals;
- meal planning/recipe library when selected;
- appointment/email reconciliation and Calendar Projection when selected;
- orders/receipts, active shopping, assets/manuals, money reconciliation, and knowledge only when useful;
- people, physical assets, and retained knowledge use immutable UUID identity where applicable.

Orders/purchases:
- One Receipt ID = one underlying transaction/total.
- Preserve ordered/shipped/delivered/exception/cancellation requested/partial cancellation/confirmed cancellation/returned/refunded history. A true replacement gets its own linked Receipt ID.
- Shopping & Procurement is an active shopping list. Fulfilled intent disappears only after durable purchase/owner-confirmation evidence is preserved and verified.
- Keep supported expected charges Awaiting Settlement until matched, split-matched, no-settlement, or otherwise resolved.

Scheduling safety:
- Show sample output and exact local times before initial automation approval.
- Keep the fewest dispatchers necessary and prefer an existing notification-capable dispatcher.
- Verify recurrence/local time/TZID, timing mode, notifications, duplicates, then an actual firing/Run Log.
- Provider scheduling metadata is authoritative only when the provider contract documents it as persistent execution state.

Pants Filling With Shit Report:
- Retry is optional/bounded. No blind retries for deterministic validation, permission/auth, ambiguous writes, Git conflicts, CI loops, or scheduler mismatch.
- On repeated/no-progress/ambiguous failure, stop that module, read back/preserve known-good Git/provider state, continue healthy modules, and report trigger, preserved state, blocked operation, and one specific next action.

Email/contact:
- Never send email automatically. Reject no-reply/unmonitored routes and find official support when needed.
- Show recipient/channel, subject, and complete body, then ask exactly `Do you want me to send this email?`

Initial provisioning:
- Show one concise dependency/resource/state summary and obtain explicit approval for the initial write bundle.
- Create the private Git state baseline, verify writes, commit/push/read back the coherent checkpoint, and run applicable CI, starter privacy, and public-source audit gates before scheduled/provider writes.

Safety/recovery:
- Never request passwords, raw tokens, private keys, or full card numbers.
- Cloud workflows cannot silently reach an unconnected private device/LAN service.
- A fresh conversation must recover from my private Git repository plus selected provider connections even after old chats are deleted.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot discovers existing capabilities/evidence, interviews in small batches, proposes the Minimum Useful Setup, gets one bounded provisioning approval, creates/verifies private Git-backed state, commits the first coherent personal checkpoint, and verifies dependency/source-audit/CI/scheduler gates before handoff.