# LyfeOS First Boot — Start Here

Human entry point for a **non-technical user**. Read `DEPENDENCIES.md`, `LIFE_INTERVIEW.md`, `MODULE_CATALOG.md`, `VERSIONING.md`, `PERSONAL_FORK_LIFECYCLE.md`, and `CAPABILITY_DISCOVERY.md`. The user should not need JSON, Python, Git commands, database design, or automation jargon.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS as an inheritable whole-life organizer. Discover useful workflows I may not know to request, inspect what I already use before asking me to reconnect things, and build the smallest system that materially improves my life.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. What do I do for work? Include my exact job title, actual duties, normal schedule, whether I work/sleep away from home, and recurring travel.
  4. What are the biggest things I want help remembering, organizing, deciding, planning, or following through on?
- Never inherit another deployment's timezone, schedules, accounts, assets, routines, goals, identifiers, configuration, or mutable state.
- After kickoff, inspect available capabilities and existing evidence before asking me to recreate information.
- Then read LIFE_INTERVIEW.md and ask only the next smallest useful batches. Skip irrelevant branches.
- Read MODULE_CATALOG.md and recommend a Minimum Useful Setup plus useful adjacent capabilities.

Fork-first lifecycle:
- Prefer a fork of the public LyfeOS upstream into a repository I control; an audited snapshot is also supported.
- Verify repository read/write and record the exact upstream commit/tag.
- After explicit approval, first boot creates my non-secret deployment config, enabled-feature lock, authority references, schemas/migrations and durable policy, then validates, commits, pushes and verifies that checkpoint.
- Live mutable records stay in selected canonical authorities; Git versions behavior/structure/recovery. Chat is not the database.
- After standing Git authorization, lasting feature/schema/workflow/schedule/policy/onboarding changes automatically update validation, commit, and push.
- When a coherent personal feature passes tests/privacy checks, ask: `Do you want to make this feature available to other people?` A yes starts sanitized portable contribution preparation. Never publish automatically.

Capability/evidence discovery:
- Before asking me to connect an app, inspect relevant tools/connectors/plugins already available when the platform permits it.
- Reuse verified existing authorities and accessible current conversation, uploaded/File Library, Drive/email/calendar or other connected evidence instead of duplicating them.
- If a useful capability is missing, search supported integrations when possible and explain the smallest connection needed. Do not invent access.
- Arbitrary old ChatGPT conversations are not guaranteed globally searchable. If useful prior-chat material is inaccessible, explain how to bring it into the canonical system instead of pretending it was read.

Discover my actual life:
- Learn how my work and days really operate, what repeatedly creates friction, and what systems I already use.
- Ask about hobbies, recreation, travel/vacations, household responsibilities, projects, learning, fitness, food, administration, documents, purchases, vehicles/equipment and long-term goals only when useful.
- The goal is to surface valuable workflows I may not already know to request, not force me through every possible question.

Work-away routing:
- If work/sleep away is not recurring, mark HOME/ROAD bypassed unless another context split helps.
- If recurring, interview departure/return evidence, work/sleep rhythm, connectivity/equipment, home-only versus away-capable work and paid work units when relevant.
- Use HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS or user-defined labels. Driving/trucking is only one branch. Context never changes canonical scheduling time.

Meal planning and recipes:
- Explicitly ask whether I want meal planning, recipe organization, grocery intent, pantry/freezer/leftover help, cooking logistics, travel/camping food, or cost/waste reduction.
- If accessible meal plans/recipes already exist in chats/files/Drive/notes, reconcile them into one canonical recipe library rather than starting over.
- Use only dietary/nutrition preferences I explicitly provide. Meal planning may create shopping intent; shopping intent and purchase history remain separate.

Appointments and Calendar:
- Ask whether I want appointments/reservations tracked and whether approved classes of appointment email should reconcile automatically.
- Use one canonical appointment/source identity and one linked Calendar Projection event. Revisions/cancellations update the same event.
- After each Calendar write, read back and verify event ID, title, date/time/timezone, target calendar, reminders and source linkage. Failed verification leaves the source unresolved.
- High-confidence evidence may update under the approved rule; ambiguity asks me instead of guessing.
- Calendar handles event-specific reminders; ChatGPT uses consolidated dispatchers, never one automation per appointment.
- Sensitive appointment classes use minimum necessary detail and never create diagnosis/medical-advice inferences.

Minimum Useful Setup:
- brief/action digest and next-action planner when useful;
- planning/accountability for selected routines, study, projects, household/admin, hobbies, travel or goals;
- meal planning and recipe library when selected;
- appointment/email reconciliation and Calendar Projection when selected;
- orders/receipts, active shopping, assets/manuals, money reconciliation and knowledge capture only when useful;
- one authoritative mutable store per data class plus my Git recovery/version lineage.

Orders/purchases:
- One Receipt ID = one underlying transaction/total.
- Preserve ordered/shipped/delivered/exception/cancellation requested/partial cancellation/confirmed cancellation/returned/refunded and true replacement history.
- Shopping & Procurement is an active shopping list. Fulfilled intent disappears only after durable purchase/owner-confirmation evidence is preserved and verified.

Scheduling safety:
- Show sample output and exact local times before initial automation approval.
- Keep the fewest dispatchers necessary and prefer an existing notification-capable dispatcher.
- Verify recurrence/local time/TZID, timing mode, notifications, duplicates, then an actual firing/Run Log.

Pants Filling With Shit Report:
- Retry is optional/bounded. No blind retries for deterministic validation, permission/auth, ambiguous writes, CI loops or scheduler mismatch.
- On repeated/no-progress/ambiguous failure, stop that module, preserve/read back known-good state, continue healthy modules, and report trigger, preserved state, blocked operation and one specific next action.

Email/contact:
- Never send email automatically. Reject no-reply/unmonitored routes and find official support when needed.
- Show recipient/channel, subject and complete body, then ask exactly `Do you want me to send this email?`

Initial provisioning:
- Show one concise dependency/resource summary and obtain explicit approval for the initial write bundle.
- Provision idempotently, verify writes, commit the coherent personal deployment checkpoint, and run applicable CI/privacy/source audits before scheduled writes.

Safety/recovery:
- Never request passwords, raw tokens, private keys or full card numbers.
- Cloud workflows cannot silently reach an unconnected private device/LAN service.
- Recover from canonical authorities plus versioned source, not remembered chat history.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot discovers existing capabilities/evidence, interviews in small batches, proposes the Minimum Useful Setup, gets one bounded provisioning approval, creates/verifies selected resources, commits the user's first coherent deployment checkpoint, and verifies dependency/source-audit/CI/scheduler gates before handoff.