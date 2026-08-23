# LyfeOS First Boot — Start Here

Human entry point. A new user should not need JSON, Python, a terminal, Git, spreadsheet design, or database administration. Read `DEPENDENCIES.md` and `MODULE_CATALOG.md` during onboarding.

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
- After kickoff, read MODULE_CATALOG.md, recommend a small Minimum Useful Setup, and ask which optional modules I want.
- Then ask what regularly slips through the cracks and suggest feasible automation.

Dependency gate:
- Read DEPENDENCIES.md before provisioning.
- Verify every selected dependency with harmless reads. A displayed connector is not proof that it works.
- If GitHub, Drive/Sheets/Docs, Gmail, Calendar, financial accounts, or another selected dependency is missing/partial, explain the exact ChatGPT-side connection steps and provider-side authorization steps. Block only the dependent module and continue what can work.
- Private Git is required for a durable deployment. Verify the chosen private repository by readback; when writes are needed, verify a bounded branch/file write only after initial provisioning approval.
- Do not enable scheduled writes until required authorities and recovery Git are verified.

Minimum Useful Setup:
- Briefs: show one manual sample, then use the fewest scheduled dispatchers for the chosen cadence.
- Orders/receipts: one canonical transaction identity, searchable evidence/line items, active fulfillment, append-only lifecycle, balanced allocations, payment reconciliation and compact active-order views.
- Inventory/assets: optionally create/enrich assets from receipts, photos, model/serial plates, UPC/SKU/part numbers and manufacturer evidence.
- Recipes: one readable recipe library with searchable title/ingredient/tag/source metadata.
- State: one authoritative mutable store plus a small Drive hierarchy; no chat-local databases.
- Modes: enable HOME/ROAD only when recurring work-away behavior makes it useful.
- Recovery: private Git stores durable policy/schema/tests/onboarding/recovery. Operational state must still work after old chats are deleted.

Initial provisioning:
- Show one concise resource/dependency summary and obtain explicit approval for the initial write bundle.
- After approval, automatically create or validate selected native Sheets/Docs/folders/tables/config, initialize schema/validation, write sanitized policy/tests/bootstrap to private Git, and verify readback.
- Provisioning must be idempotent: validate/migrate an existing canonical resource instead of creating a duplicate.
- Commit only sanitized code/policy/schema/tests/examples; personal mutable records remain in live authorities.

Job/mode routing:
- Use exact job title, actual duties, shift, and recurring travel.
- For driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away, offer HOME/ROAD (or equivalent) with deterministic boundaries, temporary overrides, route/location evidence and per-mode visibility.
- For non-travel roles, mark HOME/ROAD bypassed and ask no mode questions unless explicitly enabled later.
- For multi-leg paid work, track each actual leg independently and aggregate only verified paid units.
- Employer/shared run sheets reconcile into the existing route/trip/mileage database using stable source/date/terminal/miles evidence. Never create a second route database.
- Ask whether a terminal-pair paid-mile rule is symmetric or directional; persist that rule rather than assuming one globally for every user.

Scheduling and notifications:
- Ask authoritative timezone, cadence, exact local times and notification mode before writes.
- Show the sample brief and exact proposed schedules before first automation creation; obtain explicit approval.
- No per-order hidden jobs/retries. A consolidated lifecycle can notify for exceptions and approval-needed actions.

Calendar Projection:
- Ask whether the user wants canonical LifeOS facts pushed to Google Calendar.
- Offer event classes separately: appointments/reservations, order delivery dates/windows, work travel, trial/subscription deadlines, bills, school/work deadlines, maintenance/warranty deadlines, selected tasks, and user-defined classes.
- Ask target calendar and whether tentative dates should appear or move automatically when source dates change.
- Use one projection/link table so revisions update the same Google event instead of creating duplicates. Calendar is a projection; the Sheet/database remains authoritative.
- Do not invite attendees or send calendar invitations merely because local projection is enabled.

Git checkpoint:
- Ask the user to select/create a private deployment repository and obtain one standing authorization for durable versioning.
- After standing authorization, every lasting feature/schema/workflow/schedule/policy/onboarding change must automatically update validation, commit, and push. Do not repeatedly ask whether to push.
- This does not authorize auto-merge, public publishing, releases, force-pushes, mutable-data exports or secrets.

Orders, receipts, assets and payment:
- One stable Receipt ID per underlying transaction; photos/screenshots/files/email/account records are evidence sources and must be deduped.
- Items on one receipt may use different categories, beneficiaries, assets/projects and allocations while the receipt total counts once.
- For part/SKU/UPC/model/serial evidence, identify the exact product from manufacturer/OEM/vendor evidence, cross-reference the complete asset registry/known modifications and use exclusion evidence. Auto-assign only a uniquely supported result; queue only after reachable evidence is exhausted.
- Asset intake may combine a product photo, serial/model plate, receipt and later manufacturer lookup into one stable asset record linked to the purchase line.
- Ordered, shipped, delivered, exception, cancellation requested/confirmed, partial cancellation, returned, refunded and replaced are lifecycle states, not reasons to erase audit history.
- A same-order revision remains one Receipt ID. A true replacement with a new merchant order number gets a separate linked Receipt ID.
- Keep expected merchant charges `Awaiting Settlement` until matched, split-matched or resolved as no-settlement. Reconcile against the latest supported same-order revision and investigate unexplained overcharges/undercharges/unmatched charges.
- Cancellation and refund are separate. Only an actually expected unresolved correction gets the configured escalation deadline.
- A purchase for another person remains gross merchant spend; reimbursement is separate from merchant refund and allows both gross purchase and net household cost reporting.

Email/contact:
- Never send email automatically.
- Inspect full From/Reply-To/body/footer for no-reply or unmonitored language before proposing a reply. If unsuitable, research the current official support/order/warranty channel.
- Show actual recipient/channel, subject and complete proposed body, then ask exactly `Do you want me to send this email?`
- External deletion/retention rules must be explicitly selected and narrowly auditable.

Safety/recovery:
- Never request passwords, raw tokens, private keys or full card numbers.
- A cloud workflow cannot silently reach an unconnected LAN/NAS/home server without a deliberate bridge.
- Chat history is not a database. A fresh conversation must recover from canonical authorities after old chats are deleted.

Start now by asking only the four kickoff questions.
```

## What happens next

First boot produces a dependency status, proposed state/resource map, sample brief, module selections, calendar-projection choices, exact schedules and one bounded provisioning request. After approval, baseline private resources are automatically created/validated and verified.
