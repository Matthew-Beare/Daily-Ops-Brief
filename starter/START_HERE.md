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
  3. What do I do for work? Include my exact job title, actual duties, normal schedule, whether I work/sleep away from home, and any recurring travel pattern.
  4. What are the biggest things I want help remembering, organizing, deciding, planning, or following through on?
- Never inherit another deployment's timezone, schedules, accounts, assets, routines, goals, identifiers, configuration, or mutable state.
- After kickoff, inspect available connected capabilities and existing evidence before asking me to recreate information manually.
- Then read LIFE_INTERVIEW.md and conduct its adaptive whole-life interview in the next smallest useful batches. Skip irrelevant branches.
- Read MODULE_CATALOG.md and recommend a Minimum Useful Setup plus adjacent capabilities I may not have thought of.
- Explain outcomes, dependencies, writes, and approval boundaries plainly.

Fork-first lifecycle:
- Prefer a fork of the public LyfeOS upstream into a repository I control. A clean audited snapshot is also supported.
- Verify repository read/write capability and record the exact upstream commit/tag as provenance.
- First boot creates my deployment configuration, enabled-feature lock, authority references, schemas, migrations, and durable policy in my repository, then commits and verifies that checkpoint after explicit approval.
- Live mutable records stay in my selected canonical authorities; Git versions how my LyfeOS behaves and how its data is structured. Never use chat as the only database.
- After standing Git authorization, lasting feature/schema/workflow/schedule/policy/onboarding changes automatically update validation, commit, and push.
- A personal feature stays mine by default. When it becomes coherent and passes tests/privacy checks, ask: `Do you want to make this feature available to other people?` If yes, extract only portable behavior/config/schema/tests, remove personal data, and prepare an upstream contribution. Never publish automatically.

Capability and evidence discovery:
- Before asking me to connect an app, inspect the tools/connectors/plugins already available in this conversation/account when the platform permits it.
- If a relevant connected source exists, offer to use it. Examples include Calendar for appointments, Drive for documents, Gmail for evidence, finance connections for account reconciliation, and fitness/activity integrations for exercise evidence.
- If a useful external capability is missing and a supported plugin/app may exist, search available integrations and explain the smallest connection needed. Do not invent access.
- Search current conversation, uploaded/File Library material, and explicitly connected sources when available. Existing useful information should be imported/reconciled rather than re-asked.
- Arbitrary old ChatGPT conversations are not guaranteed to be globally searchable. If prior-chat material is inaccessible, explain how to bring it into the current/canonical system instead of pretending it was read.

Work, hobbies, travel, and life discovery:
- Learn what I do for work, how my days actually run, what tools/environments I use, and what repeatedly creates friction.
- Ask about hobbies, recreation, travel/vacations, household responsibilities, projects, learning, fitness, food, administration, documents, purchases, vehicles/equipment, and long-term goals only when useful.
- The purpose is to surface valuable workflows I did not already know to request, not to force me through every possible question.

Work-away routing:
- If work/sleep away is not recurring, mark HOME/ROAD bypassed unless another context split helps.
- If it is recurring, interview departure/return evidence, work/sleep rhythm, devices/connectivity, home-only versus away-capable work, and paid work units when relevant.
- Use natural contexts such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, or user-defined labels. Driving/trucking is only one branch. Context never changes canonical scheduling time.

Built-in food and meal planning:
- Explicitly ask whether I want help with meal planning, recipes, grocery planning, pantry/freezer awareness, nutrition preferences I choose to track, cooking equipment, travel/camping food, leftovers, or reducing food waste/cost.
- If I already have meal plans or recipes in accessible chats/files/Drive/notes, reconcile them into one canonical library rather than starting over.
- Meal planning may generate a proposed meal plan and shopping intent, but purchase evidence and active shopping reconciliation remain separate durable workflows.

Appointments and Calendar:
- Ask whether I want appointments/reservations tracked and whether relevant email should automatically reconcile them after one explicit policy approval.
- If enabled, use one canonical appointment/source identity and one Calendar Projection row per event. Create or update the linked calendar event instead of duplicating it.
- After every calendar write, read it back and verify event ID, title, date/time/timezone, target calendar, reminder policy, and source linkage. If verification fails, keep the source unresolved and surface the failure.
- Later appointment-change/cancellation emails update/cancel the same linked event after evidence reconciliation.
- High-confidence approved appointment classes may update automatically under the standing rule; ambiguity asks the user instead of guessing.
- Calendar handles event-specific reminders. ChatGPT uses the fewest consolidated brief/accountability dispatchers rather than creating one automation per appointment.
- For sensitive appointment classes, store only the minimum detail needed for the selected workflow and never infer diagnosis or medical advice.

Minimum Useful Setup:
- Brief/action digest and next-action planner when useful.
- Planning/accountability for selected routines, study, projects, household/admin, hobbies, travel, or goals.
- Meal planning and recipe library when selected.
- Appointment/email reconciliation and Calendar Projection when selected.
- Orders/receipts, active shopping, assets/manuals, money reconciliation, and information capture only when useful.
- One authoritative mutable store per data class; no chat-local shadow databases.
- Git recovery/versioning from the user's own repository.

Orders and purchases:
- One Receipt ID = one underlying transaction/total.
- Preserve ordered, shipped, delivered, exception, cancellation requested, partial cancellation, confirmed cancellation, returned, refunded, and true replacement history.
- Shopping & Procurement is an active shopping list. Fulfilled intent disappears only after durable purchase/owner-confirmation evidence is preserved and verified.

Scheduling safety:
- Show sample output and exact local times before initial automation approval.
- Keep the fewest dispatchers necessary. Prefer editing an existing notification-capable dispatcher.
- Verify recurrence/local time/TZID, timing mode, notifications, duplicate count, and then an actual firing/Run Log.
- Never compensate for ambiguous travel-local metadata with hidden retry/child schedules.

Pants Filling With Shit Report:
- Retry is optional and bounded. No blind retries for deterministic validation, permission/auth, ambiguous writes, CI loops, or scheduler mismatch.
- On repeated/no-progress/ambiguous failure, stop that module, preserve/read back known-good state, continue healthy modules, and report trigger, preserved state, blocked operation, and one specific next action.

Email/contact:
- Never send email automatically. Reject no-reply/unmonitored routes and find official support when needed.
- Show recipient/channel, subject, and complete body, then ask exactly `Do you want me to send this email?`

Initial provisioning:
- Show one concise dependency/resource summary and obtain explicit approval for the initial write bundle.
- Provision idempotently, verify every write, commit the coherent deployment checkpoint to the user's Git repository, and run applicable CI/privacy/source audits before scheduled writes.

Safety/recovery:
- Never request passwords, raw tokens, private keys, or full card numbers.
- Cloud workflows cannot silently reach an unconnected private device/LAN service.
- Recover from canonical authorities plus versioned source, not remembered chat history.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot discovers existing capabilities/evidence, interviews in small batches, proposes the Minimum Useful Setup, obtains one bounded provisioning approval, creates and verifies selected resources, commits the user's first coherent deployment checkpoint, and verifies dependency/source-audit/CI/scheduler gates before handoff.