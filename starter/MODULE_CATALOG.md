# LyfeOS First-Boot Module Catalog

After the four kickoff questions and adaptive `LIFE_INTERVIEW.md`, present modules conversationally in small groups. Recommend a useful default bundle from problems, existing evidence, and available capabilities, then expose adjacent options so a user can discover workflows they did not know to request. Do not silently enable optional modules.

For new-user starter deployments, **private Git is the canonical personal-state authority** under `GIT_STATE_MODEL.md`. Email, Calendar, Drive/files, finance, fitness/wearable, maps/weather, and similar integrations are optional evidence/projection/action adapters around that state. The current Daily Ops reference deployment has its own established external authorities and is not the starter default.

## Core whole-life modules

### Briefs and action digest
Ask: **Do you want a recurring brief combining the few things that changed, need action, or should happen next across enabled life domains?**
Collect cadence, exact local times, canonical timezone, length, priority rules, context differences and anti-nag rules.

### Next-action planner
Ask: **Do you want LyfeOS to keep a prioritized next-action queue so you can ask “what should I do next?” without rebuilding context?**
Support deadlines, prerequisites, context/location, available time, user-provided constraints, blocked work, and minimum viable actions. Never infer completion from silence. Accepted task state is committed to private Git.

### Personal accountability and routines
Ask: **Are there recurring habits or routines where useful accountability would help you stay consistent?**
Examples include exercise, mobility/yoga, hiking, household routines, maintenance, creative practice, reading, paperwork, or another commitment.

Capture frequency, preferred windows, time/components, equipment/resources, context variants, minimum viable version, completion definition, check-in behavior, miss/reschedule policy and progression/review rule. Fitness/activity integrations may be optional evidence sources when already connected and supported. Accepted completion/progression becomes Git state.

### Education and study coach
Ask: **Do you want help staying accountable for school, certifications, or other learning and deciding what to study next?**
Capture verified deadlines, current work, prerequisites, weekly target, session sizes, source materials, home/away options, offline constraints, accountability cadence and calendar preferences. LyfeOS may plan, explain, quiz and organize; it must not fabricate completed work, grades or attendance.

### Life pattern and retirement routing
Ask whether the user is working, retired, studying, caregiving, self-employed, mixed, or in another pattern. Do not make work questions the tax humans must pay for existing.

For retired/nonworking users, surface useful branches such as appointments, household/admin, volunteering, hobbies, travel, family responsibilities, routines, projects and documents. Medical-event scheduling is offered only when wanted and never implies diagnosis or medical advice.

### Context modes: HOME / ROAD / TRUCK / FIELD or equivalent
Work-pattern discovery is the routing gate. For recurring away/overnight/rotating-site work, offer context modes based on actual duties and environment. For non-travel roles mark HOME/ROAD bypassed unless another context split is deliberately useful. Driving/trucking is one branch, not the default human condition.

### Existing-system and capability discovery
Ask: **Before we build anything new, what useful information or connected apps do you already have?**
Follow `CAPABILITY_DISCOVERY.md`: inspect reachable existing evidence and tools before asking for duplicate setup. Normalize accepted operational state into private Git while retaining provider provenance/reference IDs. Missing optional integrations block only their dependent paths.

## Food, recreation and planning

### Meal planning and grocery workflow
Ask exactly: **Do you want help with meal planning?**

When enabled:
- ingest/reconcile accessible existing recipes and meal plans rather than starting over;
- preserve canonical recipe identity plus provenance/tags in private Git state;
- learn user-selected preferences, constraints, serving pattern, cooking time/equipment, repeat-versus-novelty preference, leftovers/batch/freezer strategy, grocery cadence and home/away/travel variants;
- produce proposed meal plans and active shopping intent;
- commit accepted recipes, plans, pantry/freezer facts, meal history and shopping intent as verified Git state transactions;
- keep meal planning, shopping intent and purchase history as separate concepts;
- never invent dietary/medical restrictions.

### Recipes
Ask: **Do you want a searchable recipe library from documents, links, images, notes, or existing accessible planning material?**
Store canonical recipe state with title, ingredients, directions, tags, provenance and optional user-selected nutrition/equipment fields. Bulky originals may remain with their provider while Git stores accepted structured state and references.

### Hobbies, recreation and outdoor planning
Ask: **What do you do for fun, and which parts of it are annoying to plan or easy to forget?**
For selected activities such as hiking/camping/travel/sports/photography/automotive/crafting, optionally support preparation checklists, equipment, reservations/permits, weather/routes, maintenance/consumables, progression goals and trip plans. Do not over-structure hobbies the user wants spontaneous.

### Vacation and trip planning
Ask: **Do you want help moving travel ideas from “someday” to an actual plan?**
Support destination research, date constraints, reservations, Calendar projection, packing/preparation, documents, budgets when selected, and context-aware tasks. Trips remain proposals until the user commits them; accepted plan/task state lives in private Git.

## Appointments, calendar and communication

### Verified appointment reconciliation
Ask: **Do you want appointment/reservation emails to update your LyfeOS appointment state and Calendar automatically after you approve the rule?**

Private Git is canonical. Email is evidence; Calendar is optional projection/reminders.

For each enabled appointment class:
- define allowed evidence/senders, target calendar when enabled, reminders, tentative/revision/cancellation behavior, confidence threshold and sensitive-detail policy;
- read current remote Git state and dedupe by canonical source/appointment identity;
- create/update one linked Calendar event when enabled;
- read every Calendar write back and verify event ID, title, date/time/timezone, target calendar, reminders and source linkage;
- append/update canonical Git appointment/reconciliation state with the verified provider references;
- validate, commit, push fast-forward only and read the Git state back before calling it reconciled;
- revision/cancellation evidence updates the existing Git appointment and linked event rather than duplicating it;
- ambiguity asks the user;
- event-specific reminders live in Calendar. Do not create one ChatGPT automation per appointment.

Medical appointment organization is allowed when selected, but use minimum necessary detail and never infer diagnosis/treatment or provide medical advice from scheduling evidence.

### Calendar Projection
Ask: **Which verified LyfeOS facts, if any, should also appear on Calendar?**
Offer independently: appointments/reservations; deliveries; work travel; trial/subscription deadlines; bills; school/work deadlines; routine/study sessions; maintenance/warranty deadlines; selected tasks; user-defined event types. Git remains canonical state; revisions update linked Calendar events rather than creating duplicates. Inviting attendees is separate authority.

### Important-mail triage
Ask: **Do you want important actionable email surfaced while routine mail stays quiet?**
Ask which domains/senders and event classes matter. Email is evidence; accepted action/reconciliation state is Git-backed. External sends remain approval-gated.

## Orders, purchases and assets

### Orders and shipment lifecycle
Ask: **Do you want orders tracked from ordered → shipped → delivered, including revisions, cancellations, replacements, returns, refunds and stalled shipments?**
Use one consolidated lifecycle pipeline. Accepted lifecycle state is Git-backed; delivered fulfillment leaves the active queue but remains in durable history.

### Receipt database
Ask: **Do you want a searchable purchase database from email, files, screenshots and receipt photos?**
Offer cross-source dedupe, identifiers, readable evidence references, line-item relationships, balanced allocations and unresolved classification only after investigation. Raw evidence may remain with its provider; canonical receipt/reconciliation state is private Git.

### Shopping and procurement reconciliation
Ask: **Do you want an active shopping/procurement list that removes fulfilled items automatically when LyfeOS proves they were bought?**

`Shopping & Procurement` is an active shopping list, not purchase history. Preserve one intent per desired item/project. When durable purchase evidence or explicit owner confirmation satisfies an intent, preserve transaction/reconciliation state and **remove the fulfilled shopping row** after verification. A cancellation with no supported replacement leaves the intent open. Missing exact product identity becomes a separate reconciliation task rather than a Purchased tombstone.

### Asset acquisition and inventory
Ask: **Do you want products/tools/equipment automatically added or enriched when receipts, product photos, model/serial plates or exact identifiers prove what they are?**
Canonical people/physical assets receive immutable UUIDs; friendly names/IDs remain aliases. Search before creating, link purchase evidence, enrich supported specs/warranty/compatibility and never invent unreadable identifiers.

### Manuals and reference library
Ask: **Do you want product manuals, service manuals, datasheets and technical references saved so you can later ask for them by product, part number or asset?**
Retain canonical Git indexes/state with immutable Knowledge UUID and related asset identities; bulky manual files may remain in optional file/Drive storage with stable references.

## Money and household

### Receipt/account financial reconciliation
Ask: **Do you want expected purchase charges reconciled with connected financial accounts and unexplained differences surfaced?**
Financial providers supply evidence. Keep accepted expected/reconciliation state in private Git until settlement/no-settlement resolution; distinguish reimbursement from merchant refund.

### Financial reports
Ask which receipt-derived or account-backed reports are useful and clearly state coverage limits. Provider credentials/raw authentication never enter Git.

### Household, beneficiaries and reimbursements
Support shared responsibility and purchases without duplicating merchant transactions. Reimbursement remains separate from merchant refund and gross spend.

### Subscriptions and trials
Ask whether price changes, renewals and trial-conversion risks should be tracked. Never cancel/contact automatically.

## Information, projects and administration

### General knowledge capture
Organize verified facts, procedures, specifications and documents with source/provenance. Preserve canonical Git indexes/state and avoid chat-only state.

### Projects and long-term goals
Separate active projects from someday/backlog ideas with outcomes, deadlines, dependencies, context, next milestone, review cadence and completion definition. Accepted state is Git-backed.

### Household and personal administration
Offer chores, errands, renewals, documents, appointment/admin workflows and shared-responsibility tracking. Avoid turning every household fact into a notification.

## Work-pattern modules

### Route, mileage and pay
Offer only when work uses paid routes/miles/trips/commissions/per diem or similar units. Persist that user's actual symmetric/directional rules and do not manufacture historical occurrence rows from repeated reference routes.

## Source lineage and feature exchange

### Personal Git lineage
Every new-user deployment establishes a private user-owned Git lineage during first boot. That Git repository is the canonical personal state and source authority for state events/snapshots, policy/config/schema/tests/features and upstream provenance. Provider connections remain adapters and credential holders.

### Share a personal feature
When a customization becomes coherent and passes tests/privacy/source checks, ask exactly: **Do you want to make this feature available to other people?**
If yes, follow `PERSONAL_FORK_LIFECYCLE.md` and `SHARED_FEATURE_WORKFLOW.md`: exclude `state/` and private deployment material, create synthetic fixtures, declare dependencies/permissions, version the feature, show the contribution diff, and send it upstream only under explicit publication/PR authority.

## First-boot recommendation behavior

Recommend a small bundle based on the user's stated problems, existing evidence and verified dependencies. Explain adjacent capabilities so users can discover useful features they did not know to request. Modules can be enabled/disabled later without rebuilding unrelated state.