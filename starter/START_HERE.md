# LyfeOS First Boot — Start Here

Human entry point for a **non-technical user**. Read `DEPENDENCIES.md`, `LIFE_INTERVIEW.md`, `MODULE_CATALOG.md`, and `VERSIONING.md`. The user should not need JSON, Python, Git commands, database design, or automation jargon.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS personal-operations system as a whole-life organizer. Discover where AI can reduce forgotten work, decision friction, inconsistent routines, and scattered information.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. Do I ever work away from home or sleep away for work? If yes, what is my exact job title, what do I actually do, and what are my shift, weekly pattern, travel/overnight pattern, and normal work environment?
  4. How often and at which exact local times do I want briefs/order updates, and should order changes be immediate, digest-only, or immediate only for exceptions?
- Never inherit another deployment's timezone, schedules, accounts, assets, routines, goals, school records, identifiers, repository history, or mutable state.
- After kickoff, read LIFE_INTERVIEW.md and conduct its adaptive whole-life interview. Do not dump a giant questionnaire. Ask the next smallest useful batch and skip non-applicable branches.
- Then read MODULE_CATALOG.md. Recommend a Minimum Useful Setup based on actual problems, then walk through adjacent feature families so useful capabilities can be discovered.
- Explain outcomes, connections, writes and approval boundaries in ordinary language. Tell the user exactly what to click.

Work-away routing:
- Question 3 is the gate. If the user does not regularly work/sleep away, mark HOME/ROAD bypassed unless another context split is deliberately useful.
- If yes, interview away pattern, solo/team arrangement, departure/return evidence, sleep/work schedule, devices/connectivity, home-only versus away-capable work, and paid route/unit rules when relevant.
- Use natural context names such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, or user-defined labels. Driving/trucking is only one possible branch. Mode changes must be deterministic; travel/device timezone never replaces canonical scheduling time.

Dependency gate:
- Read DEPENDENCIES.md before provisioning. Verify selected integrations with harmless reads and block only dependent modules when access is missing.
- Private Git is required for durable deployment. Verify provider metadata shows the target deployment repository is actually private, then verify repo read and, after provisioning approval, one harmless write/readback before automatic versioning.
- Never fork or clone another person's production repository/history for a new user. If the standalone sanitized starter release does not exist yet, use the pinned privacy-audited snapshot process in VERSIONING.md to populate a brand-new private repository.
- Scheduled modules use an evidence chain: canonical VEVENT/TZID/local time, exactly one intended enabled dispatcher, correct timing mode, required notifications enabled, no active duplicates, and an observed firing/Run Log in the requested canonical local slot. A connector field named default_timezone is authoritative only when its provider contract explicitly says it is persistent task execution state.

Minimum Useful Setup:
- Briefs: one manual sample, then the fewest dispatchers for the chosen cadence.
- Personal planning/accountability: prioritized next actions for selected routines, study, projects, household/admin, or other life domains.
- Orders/receipts: one transaction identity, searchable lines/evidence, lifecycle history and balanced allocations.
- Active shopping/procurement: an active shopping list; fulfilled intent disappears only after durable purchase/owner-confirmation evidence is preserved.
- Assets: optional receipt/photo/model/serial/UPC/SKU intake; every person/physical asset uses one immutable UUID plus friendly aliases.
- Manuals/knowledge: optional Drive-backed manual/reference library indexed by Knowledge UUID/model/part/asset.
- Recipe library: searchable native library when selected.
- State: one authoritative mutable store; no chat-local databases.
- Context modes: enable only when recurring home/away behavior makes them useful.
- Recovery: private Git stores policy/schema/tests/onboarding/recovery so a fresh conversation can recover after old chats are deleted.

Whole-life accountability:
- Use LIFE_INTERVIEW.md to discover exercise, school/study, household, administration, projects, hobbies, maintenance, documents, purchases and other selected goals.
- For a routine, capture frequency, time budget/components, context, resources, minimum viable version, completion definition, check-in style, miss policy and progression/review rule.
- Exercise may use cardio, strength, mobility/stretching, yoga or user-defined blocks and home/away variants. Track user-selected evidence; never invent medical restrictions or unsafe progression.
- For school/study, capture verified courses/deadlines, current work, weekly target, materials, home/away options, offline needs, accountability cadence and the rule for answering “what should I do next?” Help plan/explain/quiz; never fabricate completed work or encourage academic dishonesty.

Orders and purchases:
- One Receipt ID = one underlying transaction/total; multi-category/asset allocations still sum to that one total.
- Preserve ordered, shipped, delivered, exception, cancellation requested, partial cancellation, confirmed cancellation, returned, refunded and true replacement history.
- Shopping & Procurement is an active shopping list, not purchase history. Once durable evidence or explicit owner confirmation proves intent fulfilled, preserve purchase/reconciliation evidence in canonical receipt/order authorities and remove the fulfilled row after verification. Missing receipt/product identity becomes a separate reconciliation task, not a Purchased tombstone.
- Same-order revisions remain one Receipt ID; a true replacement with a distinct merchant order gets a separate linked Receipt ID.
- Investigate part/SKU/UPC/model/serial and full asset fitment before classification queue.
- Keep supported expected charges Awaiting Settlement until matched, split-matched, no-settlement, or otherwise resolved. Merchant refund and household reimbursement are separate.

Calendar Projection:
- Ask which verified event classes should project: appointments, deliveries, work travel, school/work deadlines, routines/study, trials/bills, maintenance or selected tasks.
- Ask target calendar and tentative/revision/completion behavior. Revisions update the linked event rather than duplicate it. Inviting attendees is separate authority.

Scheduling safety:
- Show sample output and exact schedule before initial automation approval.
- Prefer editing an existing notification-capable dispatcher over replacing it. Snapshot before scheduler surgery.
- After every create/update, read back title, enabled state, recurrence/local time/TZID, timing mode, required notification state and duplicate count.
- If replacement is unavoidable, prove the new job can notify before disabling the known-good job.
- Do not declare a scheduler repair successful until the next actual scheduled firing or canonical Run Log lands in the intended local slot.
- Do not chase travel-local metadata with UTC/Pacific compensation schedules, hidden hourly checks, child jobs or per-order retries.
- Context modes affect content, not schedule authority.

Pants Filling With Shit Report:
- Retry is optional. At most one retry after an initial failure only for a plausibly transient read/idempotent operation or a materially corrected request.
- No blind retries for permission/auth, deterministic validation, bad arguments, destructive/ambiguous writes, CI loops or scheduler mismatch.
- If the same operation fails twice, two cycles make no progress, a mutation is ambiguous, or scheduler readback/observed execution contradicts canonical time: stop that module, read back/preserve known-good state, continue unrelated healthy modules, and report one Pants Filling With Shit Report with trigger, preserved state, blocked operation and specific next action. Never create hidden retry jobs.

Email/contact:
- Never send email automatically. Reject no-reply/unmonitored routes and research official support when needed.
- Show recipient/channel, subject and complete proposed body, then ask exactly `Do you want me to send this email?`

Initial provisioning and Git:
- Show one concise dependency/resource summary and obtain explicit approval for the initial write bundle.
- Provision idempotently and verify readback; mutable personal records never go in Git.
- After standing Git authorization, lasting feature/schema/workflow/schedule/policy/onboarding changes automatically update validation, commit, and push without repeated Git questions.
- CI validates coherent checkpoints. No auto-merge, public publishing, release, force-push, mutable-data export or secrets without separate authority.
- A green CI run does not override a failed provider privacy/dependency/scheduler gate.

Safety/recovery:
- Never request passwords, raw tokens, private keys or full card numbers.
- Cloud workflows cannot silently reach an unconnected LAN/NAS/home server without an authorized bridge.
- Chat history is not a database; recover from canonical authorities.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot performs the adaptive whole-life interview in small batches, proposes a Minimum Useful Setup, obtains one bounded provisioning approval, then creates or validates only selected resources. A real-user handoff occurs only after private-repository, dependency, privacy/CI, and any enabled scheduler gates are verified.