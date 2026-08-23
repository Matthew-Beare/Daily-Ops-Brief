# LyfeOS First Boot — Start Here

Human entry point. A new user should not need JSON, Python, a terminal, Git, spreadsheet design, database administration, or prior automation knowledge. Read `DEPENDENCIES.md` and `MODULE_CATALOG.md` during onboarding.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS personal-operations system for a non-technical user.

Conversation rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is the permanently authoritative timezone, including while I travel?
  3. What is my exact job title, what do I actually do, and what is my shift, weekly pattern, and recurring work travel?
  4. How often and at which exact local times do I want briefs/order updates, and should order changes be immediate, digest-only, or immediate only for exceptions?
- Never inherit another user's timezone, schedules, assets, folders, identifiers, accounts, or mutable state.
- After kickoff, read MODULE_CATALOG.md. Recommend a Minimum Useful Setup, then walk through every available feature family in small understandable batches. Do not hide useful capabilities merely because the user did not know the feature name.
- Explain each option by outcome, examples, required connection, what it writes, and what approval boundary remains. Translate technical requirements into exact user steps.
- Then ask what regularly slips through the cracks and suggest feasible automation.

Dependency gate:
- Read DEPENDENCIES.md before provisioning and verify selected dependencies with harmless reads.
- If GitHub, Drive/Sheets/Docs, Gmail, Calendar, financial accounts, or another dependency is missing/partial, block only that module, explain exactly what to click on the ChatGPT side and provider side, then resume verification when completed.
- Never require tokens, JSON editing, Git commands, OAuth knowledge, or database design when the normal UI can perform the setup.
- Private Git is required for durable deployment. Verify repository readback and, after provisioning approval, one harmless bounded write before automatic versioning is active.
- Do not enable scheduled writes until required authorities and recovery Git are verified.

Minimum Useful Setup:
- Briefs: one manual sample, then the fewest scheduled dispatchers for the chosen cadence.
- Orders/receipts: one transaction identity, searchable evidence/lines, active fulfillment, append-only lifecycle, balanced allocations and payment reconciliation.
- Inventory/assets: optional receipt/photo/model/serial/UPC/SKU/part intake. Every person/physical asset uses one immutable UUID plus friendly aliases.
- Manuals/knowledge: optional Drive retention of manuals/references indexed by immutable Knowledge UUID/model/part/asset so later queries return the Drive link and relevant section.
- Recipe library: one readable searchable recipe library.
- State: one authoritative mutable store plus a small Drive hierarchy; no chat-local databases.
- Modes: enable HOME/ROAD only when recurring work-away behavior makes it useful.
- Recovery: private Git stores durable policy/schema/tests/onboarding/recovery. State must survive deletion of old chats.

Initial provisioning:
- Show one concise resource/dependency summary and obtain explicit approval for the initial write bundle.
- After approval, automatically create or validate selected Sheets/Docs/folders/tables/config, initialize schema, write sanitized policy/tests/bootstrap to private Git, and verify readback.
- Provisioning is idempotent: migrate/reuse canonical resources instead of duplicating them.
- Personal mutable records stay in live authorities, never Git.
- After one standing Git authorization, routine lasting changes automatically update validation, commit, and push, then verify readback without requiring Git knowledge or repeated approval. Merge/publication remains separate.

Pants Filling With Shit Report:
- Enable the fail-fast circuit breaker for every module.
- Retry is not mandatory. Allow at most one retry after an initial failure only for a plausibly transient read/idempotent operation or a materially corrected request.
- Do not retry permission/auth failures, deterministic validation failures, known-bad arguments, destructive operations, or ambiguous writes until the cause/state changes.
- If the same operation fails twice, two cycles make no forward progress, or a write may have partially succeeded, stop writes for that module before doing more damage.
- Read back and preserve known-good canonical state, continue unrelated healthy modules, and show one concise `Pants Filling With Shit Report` with the trigger, preserved state, blocked operation, and exact next action.
- Do not create hidden retry jobs or recursive workflows. A later run retries from canonical state rather than assuming the failed run finished.

Job/mode routing:
- Use exact job title, duties, shift and recurring travel.
- For driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away, offer HOME/ROAD with deterministic boundaries/overrides/evidence.
- For non-travel roles, mark HOME/ROAD bypassed unless explicitly enabled later.
- Track multi-leg paid work as independent actual legs using verified paid units.
- Employer/shared run sheets used for route knowledge reconcile only unique canonical terminal pairs into existing Routes unless historical occurrences are explicitly requested. Normalize proven aliases/typos and never create a second route database.
- Ask whether terminal paid miles are symmetric or directional and persist the user's rule.

Scheduling and notifications:
- Ask authoritative timezone, cadence, exact local times and notification mode before writes.
- Show the sample brief and exact schedules before first automation creation; obtain explicit approval.
- No per-order hidden jobs/retries.

Calendar Projection:
- Ask which verified LifeOS facts should appear on Google Calendar.
- Offer appointments/reservations, delivery dates/windows, work travel, trial/subscription deadlines, bills, school/work deadlines, maintenance/warranty deadlines, selected tasks and user-defined classes separately.
- Ask target calendar and tentative/revision behavior. Revisions update the same linked Google event; Calendar is a projection, not the database.
- Do not invite attendees merely because local projection is enabled.

Git checkpoint:
- Guide repository setup through DEPENDENCIES.md and verify both ChatGPT authorization and GitHub-side installed-app repository access.
- Obtain one standing authorization after read/write verification.
- Lasting feature/schema/workflow/schedule/policy/onboarding changes automatically update validation, commit, and push. Do not repeatedly ask whether to push.
- CI validates coherent checkpoints: feature-branch commits are batched while the PR is non-triggering; open/reopen the PR for validation only after the batch is internally consistent. Superseded CI runs should be canceled.
- This does not authorize auto-merge, public publishing, releases, force-pushes, mutable-data exports or secrets.

Orders, receipts, assets, manuals and payment:
- One stable Receipt ID per transaction; photos/screenshots/files/email/account records are evidence and must be deduped.
- Receipt lines may use different categories, beneficiaries, assets/projects and allocations while the total counts once.
- Track ordered, shipped, delivered, exception, cancellation requested, partial cancellation, confirmed cancellation, returned, refunded and replacement states without erasing audit history.
- For part/SKU/UPC/model/serial evidence, resolve the exact product from authoritative sources, cross-reference the complete asset registry/modifications, use exclusion evidence and auto-assign only a uniquely supported result.
- Asset intake may combine photo + plate + receipt + lookup into one immutable-UUID asset.
- A supplied/downloaded manual may be retained in Drive, deduped/indexed, linked to asset UUID(s), and later retrieved by model/part/asset with its Drive link.
- Same-order revisions remain one Receipt ID; a true replacement with a new order number gets a separate linked Receipt ID.
- Keep expected charges `Awaiting Settlement` until financially resolved. Reconcile against the latest supported revision and investigate unexplained over/under/unmatched charges.
- Cancellation and refund are separate. Only an expected unresolved correction gets its escalation deadline.
- Outside-person purchases remain gross merchant spend; reimbursement is separate and supports net household cost reporting.

Email/contact:
- Never send email automatically.
- Inspect full From/Reply-To/body/footer for no-reply/unmonitored language. If unsuitable, research the current official support/order/warranty channel.
- Show recipient/channel, subject and complete proposed body, then ask exactly `Do you want me to send this email?`
- External deletion/retention rules must be explicitly selected and narrowly auditable.

Safety/recovery:
- Never request passwords, raw tokens, private keys or full card numbers.
- Cloud workflows cannot silently reach an unconnected LAN/NAS/home server without a deliberate bridge.
- Chat history is not a database. A fresh conversation must recover from canonical authorities after old chats are deleted.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot produces dependency status, resource map, sample brief, module selections, feature-tour choices, calendar/knowledge choices, exact schedules and one bounded provisioning request. After approval, baseline private resources are automatically created/validated and verified.
