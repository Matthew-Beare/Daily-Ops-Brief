# LyfeOS First-Boot Module Catalog

After the four kickoff questions and the adaptive `LIFE_INTERVIEW.md`, present modules conversationally in small groups. Recommend a useful default bundle based on problems the user actually described, then offer adjacent and remaining groups so a non-technical user can discover capabilities they did not know to request. Do not silently enable optional modules. Explain outcomes, required apps/data, write behavior and approval boundaries in ordinary language. Missing dependencies route through `DEPENDENCIES.md` instead of being hand-waved.

## Core whole-life modules

### Briefs and action digest
Ask: **Do you want a recurring brief combining the few things that changed, need action, or should happen next across enabled life domains?**
Collect cadence, exact local times, canonical timezone, length, priority rules, context-mode differences and anti-nag rules.

### Next-action planner
Ask: **Do you want LifeOS to keep a prioritized next-action queue so you can ask “what should I do next?” without rebuilding context?**
Support deadlines, prerequisites, context/location, available time, energy constraints the user explicitly provides, blocked work, and minimum viable actions. Never infer completion from silence.

### Personal accountability and routines
Ask: **Are there recurring habits or routines where useful accountability would help you stay consistent?**
Examples include exercise, mobility/yoga, household routines, maintenance, creative practice, reading, paperwork, or another user-defined commitment.

For an enabled routine capture frequency, preferred windows, time budget, components, equipment/resources, home/away applicability, minimum viable version, completion definition, check-in behavior, miss/reschedule policy and progression/review rule. Record completion honestly and avoid punitive or repetitive nagging.

Exercise routines may contain cardio, strength, mobility/stretching, yoga, or user-defined blocks. Support evidence-based progression from the user's own logged sessions and constraints; do not invent diagnoses, injury restrictions or unsafe progression.

### Education and study coach
Ask: **Do you want help staying accountable for school, certifications, or other learning and deciding what to study next?**
Capture courses/programs, verified deadlines, current work, prerequisites, weekly target, study-session sizes, source materials, home/away study options, offline constraints, accountability cadence and calendar preferences. LifeOS may plan, explain, quiz and organize; it must not fabricate completed work, grades or attendance or encourage academic dishonesty.

### Context modes: HOME / ROAD / TRUCK / FIELD or equivalent
The kickoff work-away question is the routing gate. If the user regularly works away from home, sleeps away for work, rotates worksites or lives/works from a vehicle/field location, offer context modes and interview what changes between them. For non-travel roles mark HOME/ROAD bypassed unless another context split is deliberately useful.

Mode names should fit the user. Capture deterministic entry/exit triggers, tasks/routines available in each mode, device/connectivity limits, work/sleep pattern, route/weather/pay needs when relevant, and what must wait for home. Travel context never changes the canonical scheduling timezone.

## Orders, purchases and assets

### Orders and shipment lifecycle
Ask: **Do you want orders tracked from ordered → shipped → delivered, including revisions, cancellations, replacements, returns, refunds and stalled shipments?**
Use one consolidated lifecycle pipeline. Delivered fulfillment leaves the active queue but remains in durable history.

Optional Gmail organization may group correlated merchant/carrier messages under order-history labels. If the user deliberately selects a retention rule, explain exactly which mail may later be deleted and what canonical evidence must exist first.

### Receipt database
Ask: **Do you want a searchable purchase database from email, files, screenshots and receipt photos?**
Offer vendor/order/item/date/category/amount search; cross-source dedupe; UPC/GTIN/SKU/part/model extraction; readable evidence links; line-item categories/beneficiaries/assets; balanced allocations; and unresolved classification only after investigation.

### Shopping and procurement reconciliation
Ask: **Do you want an active shopping/procurement list that removes fulfilled items automatically when LifeOS proves they were bought?**

`Shopping & Procurement` is an active shopping list, not purchase history. Preserve one shopping intent per desired item/project. When durable purchase evidence or explicit owner confirmation satisfies an open intent, preserve the transaction and reconciliation evidence in the canonical receipt/order system, then remove the fulfilled shopping row after verification. Do not leave `Purchased` tombstones merely to retain history.

Order revisions and replacement orders satisfy the same intent rather than creating duplicates. A confirmed cancellation without a supported replacement leaves the intent open or needing replacement. If the owner confirms an item was bought but exact receipt/product identity remains unresolved, remove the fulfilled shopping intent and keep the missing identity as a separate reconciliation task.

### Asset acquisition and inventory
Ask: **Do you want products/tools/equipment automatically added or enriched when receipts, product photos, model/serial plates or exact identifiers prove what they are?**
Offer tools/shop equipment, vehicles/parts, electronics/computers, appliances/home equipment, warranty/serial assets, hobby/technical equipment and user-defined domains.

Every canonical person/physical asset receives an immutable collision-resistant UUID that survives renames, ownership changes and database migrations. Friendly IDs/names remain aliases. Search existing inventory first, preserve evidence, link the purchase line, enrich specs/warranty/compatibility and never invent an unreadable model/serial digit.

### Manuals and reference library
Ask: **Do you want product manuals, service manuals, datasheets and technical references saved so you can later ask for them by product, part number or asset?**

If enabled, retain the original in canonical Drive, dedupe across upload/email/link sources, assign an immutable Knowledge UUID, index manufacturer/model/part/revision/tags/related asset UUIDs, and later return the canonical Drive link plus page/section when supported.

## Money and household

### Receipt/account financial reconciliation
Ask: **Do you want LifeOS to reconcile expected purchase charges with connected financial accounts and surface unexplained differences?**
Keep supported merchant totals open until settlement/no-settlement resolution; reconcile same-order revisions first; detect possible over/under/duplicate/unmatched charges; distinguish reimbursement from merchant refund.

### Financial reports
Ask: **Do you want spending/household reports from verified receipts and, when separately connected, account-level finance data?**
Offer current/prior week, month, YTD, rolling 12 months, calendar years, merchant/category/asset/beneficiary, gross purchase, reimbursements and net household cost. Clearly distinguish receipt-detected coverage from complete account data.

### Household, beneficiaries and reimbursements
Ask whether purchases, tasks or calendar items may belong to another household member, friend/client or their asset, and whether reimbursements should be tracked. One merchant transaction remains one Receipt ID. Beneficiary/asset assignment and reimbursement are separate relationships; reimbursement does not erase gross spend or become a merchant refund.

### Subscriptions and trials
Ask: **Do you want subscriptions, price changes, renewal dates and trial-conversion risks detected?**
Never cancel/contact automatically.

## Information, communication and planning

### Important-mail triage
Ask: **Do you want important actionable email surfaced while routine mail stays quiet?**
Ask which domains/senders matter. External sends remain approval-gated.

### Calendar Projection
Ask: **Which verified LifeOS facts, if any, should also appear on Google Calendar?**
Offer independently: appointments/reservations; order delivery dates/windows; work travel; trial/subscription deadlines; bills; school/work deadlines; routine or study sessions; maintenance/warranty deadlines; selected tasks; user-defined event types.

For each enabled class collect target calendar, tentative-date behavior, automatic revision behavior and completion/cancellation behavior. Use one projection/link row per source event so changes update rather than duplicate. Inviting other people is a separate permission boundary.

### Recipes
Ask: **Do you want a searchable recipe library from documents, links, images and notes?**
Store one canonical body with title, ingredients, directions, tags, provenance and optional nutrition/equipment.

### General knowledge capture
Ask: **Do you want verified facts, procedures, specifications, documents and source excerpts organized into a searchable knowledge store?**
Preserve source/provenance; retain relevant excerpts by default and full raw sources only when needed/pinned. Manuals/reference files use the dedicated manual-library workflow above.

### Projects and long-term goals
Ask: **Do you want active projects separated from someday/backlog ideas, with milestones and next actions?**
Capture outcome, current state, real deadlines, dependencies, context restrictions, next milestone, review cadence and completion definition. Keep aspirational backlog out of daily briefs unless promoted.

### Household and personal administration
Offer recurring chores, errands, appointments, renewals, maintenance, paperwork, document organization and shared-responsibility tracking. Ask which items belong in briefs, Calendar Projection, task state or reference only. Avoid turning every household fact into a notification.

## Work-pattern modules

### Route, mileage and pay
Offer only when work uses paid routes/miles/trips/commissions/per diem or similar units. Track each actual current work leg separately; never assume the first destination returns directly home.

Ask whether company-paid terminal mileage is **symmetric by pair** or **directional**. Persist the user's actual rule. A historical employer/shared run sheet used as route knowledge imports only unique canonical terminal pairs by default, normalizes only proven aliases/typos, records mileage variants/provenance, and updates the existing Routes database. It does not create hundreds of duplicate historical Trips merely because the source repeats a route.

## Default receipt taxonomy

Use a stable primary category plus flexible subcategories/tags. Starter primaries are user-editable: Automotive & Transport; Tools & Shop; House & Home Improvement; Bills & Utilities; Electronics & Computing; Education & Professional; Health & Medical; Groceries & Household Consumables; Food & Dining; Clothing & Personal; Pets; Travel & Lodging; Subscriptions & Services; Insurance & Financial Fees; Taxes & Government; Entertainment & Hobbies; Gifts & Charity; Work & Business; General / Needs Classification.

Category changes never change Receipt ID/transaction identity.

## Lifecycle money semantics

A confirmed cancellation leaves active orders/shipments/current spend/inventory effects but remains auditable. Determine whether money settled before expecting a refund. Same-order revisions remain one transaction. A new merchant replacement order receives its own linked Receipt ID. Only an actually expected unresolved financial correction becomes an action after its configured deadline.

## First-boot recommendation behavior

Recommend a small default bundle based on the user's stated problems and verified dependencies, then walk through adjacent and remaining feature groups in small batches. Explain what each feature accomplishes and offer to guide missing dependency setup. Users may enable/disable modules later without rebuilding unrelated state.
