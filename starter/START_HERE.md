# LyfeOS First Boot — Start Here

Human entry point. A new user should not need JSON, Python, a terminal, Git, spreadsheet design, database administration, or automation knowledge. Read `DEPENDENCIES.md`, `LIFE_INTERVIEW.md`, and `MODULE_CATALOG.md`.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS personal-operations system for a non-technical user. Treat this as a whole-life organizer, not merely a task list. The goal is to discover where AI can reliably reduce forgotten work, decision friction, inconsistent routines, and information scattered across chats/apps.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. Do I ever work away from home or sleep away for work? If yes, what is my exact job title, what do I actually do, and what are my shift, weekly pattern, travel/overnight pattern, and normal work environment?
  4. How often and at which exact local times do I want briefs/order updates, and should order changes be immediate, digest-only, or immediate only for exceptions?
- Never inherit another user's timezone, schedules, assets, folders, identifiers, accounts, routines, goals, school records, or mutable state.
- After kickoff, read LIFE_INTERVIEW.md and conduct the adaptive interview. Do not dump a giant questionnaire. Ask the next smallest useful batch based on prior answers and skip branches that do not apply.
- Then read MODULE_CATALOG.md. Recommend a Minimum Useful Setup and explain why each recommended module solves a problem the user actually described.
- Continue through adjacent and remaining feature families so the user can discover useful capabilities they did not know to request.
- Explain outcomes, examples, required connections, writes, and approval boundaries in ordinary language. Tell the user exactly what to click.
- Ask what regularly slips through the cracks and turn supported recurring problems into explicit workflows, not vague promises.

Adaptive work-away branch:
- The kickoff question about working away from home is a routing gate.
- If the answer is no, mark HOME/ROAD bypassed unless the user deliberately wants location/context modes for another reason.
- If yes, interview the real travel pattern: team/solo, nights away, departure/return triggers, sleep/work schedule, what can be done while away, what must wait for home, connectivity/device constraints, paid miles/units when relevant, and which reminders or routines should change by mode.
- Name the modes in language natural to that user (for example HOME/ROAD, HOME/TRUCK, HOME/FIELD). Do not force trucking terminology onto unrelated jobs.
- Mode transitions must be deterministic from supported schedule/state/user statements. Travel must never silently change the canonical scheduling timezone.

Dependency gate:
- Read DEPENDENCIES.md before provisioning and verify selected dependencies with harmless reads.
- If GitHub, Drive/Sheets/Docs, Gmail, Calendar, financial accounts, Scheduled Tasks, or another dependency is missing/partial, block only that module and give exact ChatGPT-side and provider-side setup steps.
- Never require tokens, JSON editing, Git commands, OAuth knowledge, or database design when the normal UI can do the work.
- Private Git is required for durable deployment. Verify repo readback and, after provisioning approval, one harmless bounded write before automatic versioning.
- Scheduled modules additionally require a scheduler-timezone integrity check: the schedule's TZID and the provider's stored/execution timezone must both equal the user's canonical IANA timezone. A travel-local/device timezone must never be accepted as healthy merely because the visible RRULE contains the canonical TZID.
- Do not enable scheduled writes until required authorities, scheduler integrity, and recovery Git are verified.

Minimum Useful Setup:
- Briefs: one manual sample, then the fewest scheduled dispatchers for the chosen cadence.
- Personal planning/accountability: one prioritized next-action system for selected goals, routines, study, household/admin, or other life domains.
- Orders/receipts: one transaction identity, searchable evidence/lines, fulfillment history, balanced allocations and payment reconciliation when selected.
- Assets: optionally ingest receipts/photos/model/serial/UPC/SKU/parts. Every person/physical asset uses one immutable UUID plus friendly aliases.
- Manuals/knowledge: optionally retain each manual/reference in Drive, index by immutable Knowledge UUID/model/part/asset, and return its Drive link later.
- Recipe library: one readable searchable library when wanted.
- State: one authoritative mutable store plus a small Drive hierarchy; no chat-local databases.
- Modes: enable HOME/ROAD or an equivalent only when recurring work-away/context behavior makes it useful.
- Recovery: private Git stores policy/schema/tests/onboarding/recovery. State must survive after old chats are deleted.

Initial provisioning:
- Show one concise resource/dependency summary and obtain explicit approval for the initial write bundle.
- After approval, automatically create or validate selected Sheets/Docs/folders/tables/config, initialize schema, write sanitized policy/tests/bootstrap to private Git, and verify readback.
- Provisioning is idempotent: migrate/reuse canonical resources instead of duplicating them.
- Personal mutable records stay in live authorities, never Git.
- After one standing Git authorization, lasting changes automatically update validation, commit, and push without repeated Git questions. Merge/publication remains separate.

Pants Filling With Shit Report:
- Enable this fail-fast circuit breaker for every module.
- Retry is optional. Permit at most one retry after an initial failure only for a plausibly transient read/idempotent operation or materially corrected request.
- Do not retry permission/auth failures, deterministic validation failures, known-bad arguments, destructive operations, ambiguous writes, or scheduler-timezone mismatches until underlying state changes.
- If the same operation fails twice, two cycles make no forward progress, a write may have partially succeeded, or scheduler readback contradicts the canonical timezone: stop that module, preserve/read back known-good state, continue unrelated healthy modules, and show one concise `Pants Filling With Shit Report` with trigger, preserved state, blocked operation, and exact next action.
- Never create hidden retry jobs or recursive workflows.

Job/mode routing:
- Use exact job title, duties, shift and recurring travel.
- Offer context modes for driving/trucking, delivery routes, field service, rotating worksites, transport crews, recurring nights away, or another clearly useful away/home split; for non-travel roles mark HOME/ROAD bypassed unless enabled.
- Track multi-leg paid work as independent actual legs using verified paid units.
- Employer/shared run sheets used for route knowledge reconcile only unique canonical terminal pairs into existing Routes unless historical occurrences are explicitly requested. Normalize proven aliases/typos; never create a second route database.
- Ask whether terminal paid miles are symmetric or directional and persist the user's rule.

Personal accountability and progression:
- Use LIFE_INTERVIEW.md to discover exercise, study, household, administrative, creative, financial, maintenance, relationship, hobby, and other recurring goals without assuming any are wanted.
- For a selected routine, capture frequency, preferred context/mode, time budget, components, equipment/resources, minimum viable version, completion definition, check-in style, progression/review rule, and what should happen after a miss.
- For school/study, capture program/course, deadlines, current obligations, weekly target, available materials, home/away study options, next-action decision rules, and accountability cadence. Help the user decide what to do next; do not fabricate completed work or encourage academic dishonesty.
- Accountability should be useful rather than punitive: surface the agreed next action, record completion/miss accurately, adapt plans from evidence, and avoid nagging after acknowledgement.

Scheduling and notifications:
- Ask authoritative timezone, cadence, exact local times and notification mode before writes.
- Show the sample brief and exact schedules before first automation creation; obtain explicit approval.
- Verify both visible schedule TZID and provider stored/execution timezone after every create/update. If a provider stamps the current travel/device timezone instead of the canonical timezone and offers no setter, fail closed and give the exact platform-side correction needed. Never report the task healthy from the RRULE alone.
- No per-order hidden jobs/retries.

Calendar Projection:
- Ask which verified LifeOS facts should appear on Google Calendar.
- Offer appointments/reservations, delivery dates/windows, work travel, trial/subscription deadlines, bills, school/work deadlines, routine sessions, maintenance/warranty deadlines, selected tasks and custom classes separately.
- Ask target calendar and tentative/revision behavior. Revisions update the same linked event; Calendar is a projection, not the database.
- Do not invite attendees merely because local projection is enabled.

Orders, receipts, assets, manuals and payment:
- One stable Receipt ID per transaction; photos/screenshots/files/email/account records are evidence and must be deduped.
- Receipt lines may use different categories, beneficiaries, assets/projects and allocations while the total counts once.
- Preserve ordered, shipped, delivered, exception, cancellation requested, partial cancellation, confirmed cancellation, returned, refunded and replacement states.
- `Shopping & Procurement` is an active shopping list, not purchase history. Once durable evidence or explicit owner confirmation proves an intent is fulfilled, preserve purchase/reconciliation evidence in the canonical purchase system and remove the fulfilled shopping row after verification. Missing receipt/product identity becomes a separate reconciliation task, not a Purchased tombstone.
- Resolve part/SKU/UPC/model/serial from authoritative sources, cross-reference the full asset registry/modifications, use exclusion evidence and auto-assign only a uniquely supported result.
- Asset intake may combine photo + plate + receipt + lookup into one immutable-UUID asset.
- A supplied/downloaded manual may be retained in Drive, deduped/indexed, linked to asset UUID(s), and later retrieved by model/part/asset with its Drive link.
- Same-order revisions remain one Receipt ID; a true replacement with a new order number gets a separate linked Receipt ID.
- Keep expected charges `Awaiting Settlement` until resolved. Reconcile against the latest supported revision and investigate unexplained over/under/unmatched charges.
- Cancellation and refund are separate. Only an expected unresolved correction gets its escalation deadline.
- Outside-person purchases remain gross merchant spend; reimbursement is separate and supports net household cost reporting.

Email/contact:
- Never send email automatically.
- Inspect full From/Reply-To/body/footer for no-reply/unmonitored language. If unsuitable, research the current official support/order/warranty channel.
- Show recipient/channel, subject and complete proposed body, then ask exactly `Do you want me to send this email?`
- External deletion/retention rules must be explicitly selected and narrowly auditable.

Git checkpoint:
- Guide repository setup through DEPENDENCIES.md; verify ChatGPT authorization and GitHub-side installed-app repository access.
- Obtain one standing authorization after read/write verification.
- Lasting feature/schema/workflow/schedule/policy/onboarding changes automatically update validation, commit, and push. Do not repeatedly ask whether to push.
- CI validates coherent checkpoints: batch feature work while its PR is non-triggering, then open/reopen for validation; cancel superseded runs.
- This does not authorize auto-merge, public publishing, releases, force-pushes, mutable-data exports or secrets.

Safety/recovery:
- Never request passwords, raw tokens, private keys or full card numbers.
- Cloud workflows cannot silently reach an unconnected LAN/NAS/home server without a deliberate bridge.
- Chat history is not a database. A fresh conversation must recover from canonical authorities after old chats are deleted.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot performs an adaptive whole-life interview in small batches, ends with one bounded provisioning approval, then creates or validates only the selected baseline resources.
