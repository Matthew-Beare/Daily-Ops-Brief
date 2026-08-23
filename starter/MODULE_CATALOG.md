# LyfeOS First-Boot Module Catalog

After the four kickoff questions, present this catalog conversationally in small groups. Do not silently enable optional modules. Explain the useful outcome in plain language and let the user choose. Stock modules should be easy to enable without requiring technical vocabulary.

## Core personal-ops modules

### Briefs and action digest
Ask: **Do you want a recurring brief that combines tasks, appointments, important email, orders, and other enabled modules into one short update?**

Collect cadence, exact local times, authoritative timezone, preferred length, and what should never be repeated after acknowledgement.

### Orders and shipment lifecycle
Ask: **Do you want me to track orders from email from ordered → shipped → delivered, including cancellations, replacements, returns, refunds, and stalled shipments?**

Use one consolidated lifecycle pipeline, never one automation/task/calendar event per order. Delivered items leave the active queue but remain in lifecycle history.

### Receipt database
Ask: **Do you want me to build and maintain a searchable database of receipts and purchases that arrive by email?**

If enabled, offer:
- searchable vendor/order/item/date/category/amount fields;
- canonical readable receipt copies and evidence links;
- deduplication across confirmation, shipment, delivery, and forwarded-message variants;
- append-only lifecycle history;
- category and asset tagging without duplicate spend;
- unresolved classifications queued for a compact user question instead of guessed.

### Asset and inventory extraction
Ask: **When a receipt clearly identifies something you own, do you want me to add or update an inventory record automatically after the receipt passes validation?**

Offer inventory domains separately so the user can enable only useful ones: tools/shop equipment, vehicles/parts, electronics/computers, appliances/home equipment, warranties/serial-number assets, hobby/technical equipment, and user-defined domains. Never infer ownership, model, serial number, asset relationship, or disposal from weak evidence.

### Receipt-detected financial reports
Ask: **Do you want spending reports from the receipts and purchase email I can verify?**

Make the evidence boundary explicit: this is receipt/email-detected spending unless an account-level finance source is separately connected.

Offer these default views:
- current week and prior week;
- current month and prior month;
- year to date;
- rolling 12 months;
- prior calendar year and selectable calendar years;
- category, merchant, asset/project, and recurring/subscription breakdowns;
- refunds/cancellations netted exactly once while gross lifecycle evidence remains auditable.

Let the user choose which views belong in recurring briefs versus on-demand dashboards.

### Subscriptions and trials
Ask: **Do you want recurring subscriptions, price changes, renewal dates, and free-trial conversion risks detected from email?**

Never cancel or contact a vendor automatically. Surface exact evidence and requested action.

### Important-mail triage
Ask: **Do you want important actionable email surfaced in your brief while routine mail stays quiet?**

Ask which domains matter, such as employment, school, medical, financial, security, bills, purchases, or user-defined senders. Never send email automatically. Archive important actionable mail only after explicit approval when that workflow is enabled.

### Calendar and appointment reminders
Ask: **Do you want appointments folded into your brief, and when should they first appear?**

Collect day-before, morning-of, weekly preview, preparation, travel-time, or other user-selected rules. Never expose hidden anti-nag/confirmation state.

### Recipes
Ask: **Do you want a searchable recipe library built from your documents, links, images, and notes?**

Store one canonical recipe body with searchable title, ingredients, directions, tags, source/provenance, and optional nutrition/equipment fields.

### Knowledge capture
Ask: **Do you want verified facts, procedures, specifications, documents, and source excerpts organized into a searchable personal knowledge store?**

Default ingestion contract: preserve source URL/title/metadata and precise timestamp/page/section provenance; retain relevant excerpts by default rather than dumping entire transcripts; pin full raw sources only when requested or required.

## Work-pattern modules

### HOME / ROAD or equivalent travel mode
Do **not** ask this merely because the user has a job. Enable the branch only when exact job title, actual duties, or recurring schedule shows meaningful work travel, driving, trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away from home.

Ask: **Do you regularly work away from home enough that your brief should behave differently while you are away?**

If no, bypass the entire mode subsystem. If yes, collect deterministic enter/exit triggers, temporary overrides, per-mode task/weather/appointment visibility, and route/location evidence. Names may be HOME/ROAD or user-defined equivalents.

### Route, mileage, and pay tracking
Offer only when the work pattern uses paid routes, mileage, trips, commissions, per-diem, or similar measurable work units.

Ask: **Do you want each work leg recorded with origin, destination, company-paid miles, status, and pay estimate so weekly and longer-term totals are automatic?**

A multi-leg work week is modeled as separate consecutive trip legs. The system must never assume the user travels directly from the first destination back home. Close each arrived leg, open the next known leg, and aggregate all company/user-confirmed paid miles inside the configured pay week.

The pay week is independent of HOME/ROAD display mode. Returning home does not erase the week. A new configured pay week starts automatically at its boundary.

## Household and ownership modules

Ask whether household members share evidence but require separate ownership, budgets, calendars, mode state, or private records. One receipt may relate to multiple people/assets without being counted twice.

## Default receipt taxonomy

Use a two-level taxonomy: a stable primary category plus flexible subcategories/tags. The starter set is intentionally broad and user-editable:

- Automotive & Transport
- Tools & Shop
- House & Home Improvement
- Bills & Utilities
- Electronics & Computing
- Education & Professional
- Health & Medical
- Groceries & Household Consumables
- Food & Dining
- Clothing & Personal
- Pets
- Travel & Lodging
- Subscriptions & Services
- Insurance & Financial Fees
- Taxes & Government
- Entertainment & Hobbies
- Gifts & Charity
- Work & Business
- General / Needs Classification

Examples of subcategories include Tires, Vehicle Parts, Fuel & Charging, Hand Tools, Power Tools, Building Materials, HVAC, Internet, Mobile Phone, Software, Tuition, Certification, Pharmacy, Veterinary, Hotels, Streaming, Insurance Premiums, and Warranty/Service Plans. Users may rename/add categories without changing Receipt IDs or historical transaction identity.

## Cancellation semantics

A confirmed cancellation must disappear from **active orders, active shipments, current spend, dashboards, and inventory side effects**. It must not be physically deleted from audit history. Retain the Receipt ID, cancelled detail/event, and evidence with `Include in Spend = FALSE` so duplicate ingestion, refunds, disputes, replacements, and later corrections remain traceable.

If no replacement exists, the cancelled transaction simply ends in terminal `Cancelled` state with no replacement link. If a new merchant order replaces it, preserve both identities and link them reciprocally.

## First-boot recommendation behavior

Do not dump the entire catalog at once. After kickoff, recommend a small default bundle based on available connectors and the user's problems, then offer adjacent modules. Explain what each module buys them, what data it needs, and what actions still require approval. The user can change choices later without rebuilding unrelated modules.
