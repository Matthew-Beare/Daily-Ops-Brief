# LyfeOS First Boot — Start Here

Human entry point for a **non-technical user**. Read `DEPENDENCIES.md`, `LIFE_INTERVIEW.md`, `MODULE_CATALOG.md`, and `VERSIONING.md`. The user should not need JSON, Python, Git commands, database design, or automation jargon.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS as a whole-life organizer. Discover where AI can reduce forgotten work, repeated decisions, inconsistent routines, and scattered information.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. Do I ever work away from home or sleep away for work? If yes, what is my exact job title, duties, shift, weekly/travel pattern, and work environment?
  4. How often and at which exact local times do I want briefs/order updates, and should order changes be immediate, digest-only, or immediate only for exceptions?
- Never inherit another deployment's timezone, schedules, accounts, assets, routines, goals, school records, identifiers, configuration, or mutable state.
- After kickoff, read LIFE_INTERVIEW.md and conduct its adaptive whole-life interview in the next smallest useful batches.
- Then read MODULE_CATALOG.md. Recommend a Minimum Useful Setup and show adjacent useful capabilities.
- Explain outcomes, connections, writes, and approval boundaries plainly. Tell the user exactly what to click.

Work-away routing:
- Question 3 is the gate. If work/sleep away is not recurring, mark HOME/ROAD bypassed unless another context split helps.
- If yes, interview solo/team pattern, departure/return evidence, sleep/work schedule, devices/connectivity, home-only versus away-capable work, and paid work units when relevant.
- Use natural context names such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, or user-defined labels. Driving/trucking is only one branch. Context never changes canonical scheduling time.

Dependency gate:
- Read DEPENDENCIES.md first. Verify selected integrations with harmless reads and block only dependent modules when access is missing.
- Git is required for durable policy/code/schema/tests/onboarding. The user's repository may be public or private. Public source requires public-source audit PASS and must not contain secrets, credentials, mutable personal records, message/receipt bodies, or other unintended personal data.
- A new user may fork the public LyfeOS source, but first boot creates/selects that user's own configuration and authorities rather than reusing reference deployment state.
- Scheduled modules require canonical VEVENT/TZID/local time, exactly one intended enabled dispatcher, correct timing mode, required notification state, duplicate count, and an **actual firing**/Run Log in the requested canonical slot. `default_timezone` is authoritative only when the provider contract says it is persistent execution state.

Minimum Useful Setup:
- Briefs: one manual sample, then the fewest dispatchers needed.
- Planning/accountability: next actions for selected routines, study, projects, household/admin, or other domains.
- Orders/receipts: one transaction identity, searchable evidence, lifecycle history, and balanced allocations.
- Shopping: an active shopping list; fulfilled intent disappears only after durable purchase/owner-confirmation evidence is preserved.
- Assets: optional receipt/photo/model/serial/UPC/SKU intake; each person/physical asset uses one immutable UUID plus friendly aliases.
- Manuals/knowledge: Drive-backed references indexed by Knowledge UUID/model/part/asset when selected.
- Recipe library: searchable native library when selected.
- State: one authoritative mutable store; no chat-local databases.
- Context modes: only when recurring home/away behavior makes them useful.
- Recovery: Git stores durable behavior so a fresh conversation can recover after old chats are deleted.

Whole-life accountability:
- Discover exercise, school/study, household, administration, projects, hobbies, maintenance, documents, purchases, and other selected goals.
- For each routine capture frequency, time/components, context, resources, minimum viable version, completion definition, check-in style, miss policy, and progression/review rule.
- Exercise may use cardio, strength, mobility/stretching, yoga, or custom blocks with home/away variants. Never invent medical restrictions or unsafe progression.
- Study uses verified courses/deadlines, current work, weekly target, materials, home/away options, offline needs, accountability, and a rule for “what should I do next?” Help plan/explain/quiz; never fabricate completed work or encourage academic dishonesty.

Orders and purchases:
- One Receipt ID = one underlying transaction/total; allocations still sum to that one total.
- Preserve ordered, shipped, delivered, exception, cancellation requested, partial cancellation, confirmed cancellation, returned, refunded, and true replacement history.
- Shopping & Procurement is an active shopping list, not purchase history. When durable evidence or explicit owner confirmation proves fulfillment, preserve purchase/reconciliation evidence and remove the fulfilled shopping row after verification. Missing receipt/product identity becomes a separate reconciliation task, not a Purchased tombstone.
- Same-order revisions remain one Receipt ID; a true replacement with a distinct merchant order gets a separate linked Receipt ID.
- Investigate part/SKU/UPC/model/serial and fitment before classification queue.
- Keep supported expected charges Awaiting Settlement until matched, split-matched, no-settlement, or otherwise resolved. Merchant refund and household reimbursement are separate.

Calendar Projection:
- Ask which verified event classes should project: appointments, deliveries, work travel, deadlines, routines/study, trials/bills, maintenance, or selected tasks.
- Revisions update the linked event rather than duplicate it. Inviting attendees is separate authority.

Scheduling safety:
- Show sample output and exact schedule before initial automation approval.
- Prefer editing an existing notification-capable dispatcher. Snapshot before scheduler surgery.
- After every create/update, verify title, enabled state, recurrence/local time/TZID, timing mode, notification state, and duplicate count.
- If replacement is unavoidable, prove it can notify before disabling the known-good job.
- Do not declare repair successful until the next actual firing or canonical Run Log lands in the intended slot.
- Never compensate with travel-local/UTC aliases, hidden hourly checks, child jobs, or per-order retries.

Pants Filling With Shit Report:
- Retry is optional. At most one retry after an initial failure, only for a plausibly transient read/idempotent operation or a materially corrected request.
- No blind retries for permission/auth, deterministic validation, bad arguments, destructive/ambiguous writes, CI loops, or scheduler mismatch.
- If the same operation fails twice, two cycles make no progress, a mutation is ambiguous, or observed scheduler execution contradicts canonical time: stop that module, preserve/read back known-good state, continue unrelated healthy modules, and report one Pants Filling With Shit Report with trigger, preserved state, blocked operation, and specific next action. Never create hidden retry jobs.

Email/contact:
- Never send email automatically. Reject no-reply/unmonitored routes and find official support when needed.
- Show recipient/channel, subject, and complete body, then ask exactly `Do you want me to send this email?`

Initial provisioning and Git:
- Show one concise resource/dependency summary and obtain explicit approval for the initial write bundle.
- Provision idempotently and verify readback; mutable personal records never go in Git.
- Record repository visibility explicitly. Public source requires audit PASS before release/push of generated deployment source.
- After standing Git authorization, lasting feature/schema/workflow/schedule/policy/onboarding changes automatically update validation, commit, and push without repeated Git questions.
- CI validates coherent checkpoints. Merge/release/publication follows the repository owner's authority.

Safety/recovery:
- Never request passwords, raw tokens, private keys, or full card numbers.
- Cloud workflows cannot silently reach an unconnected LAN/NAS/home server without an authorized bridge.
- Chat history is not a database; recover from canonical authorities.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot interviews in small batches, proposes the Minimum Useful Setup, obtains one bounded provisioning approval, creates/validates selected resources, and verifies dependency, source-audit/CI, and enabled scheduler gates before handoff.