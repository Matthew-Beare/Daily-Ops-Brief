# LyfeOS First-Boot Module Catalog

After the four kickoff questions, present modules conversationally in small groups. Recommend a useful default bundle, then offer the remaining relevant groups so users of any technical ability can discover the system's capabilities. Do not silently enable optional modules. Explain outcomes, required apps/data, write behavior and approval boundaries in ordinary language. Missing dependencies route through `DEPENDENCIES.md` instead of being hand-waved.

## Core personal-ops modules

### Briefs and action digest
Ask: **Do you want a recurring brief combining tasks, appointments, important email, orders, finance/payment exceptions, and other enabled modules?**
Collect cadence, exact local times, authoritative timezone, length and anti-nag rules.

### Orders and shipment lifecycle
Ask: **Do you want orders tracked from ordered → shipped → delivered, including revisions, cancellations, replacements, returns, refunds and stalled shipments?**
Use one consolidated lifecycle pipeline. Delivered fulfillment leaves the active queue but remains in durable history.

Optional Gmail organization may group all correlated merchant/carrier messages under an order-history label. If the user deliberately selects a retention rule, explain exactly which mail may later be deleted and what canonical evidence must exist first.

### Receipt database
Ask: **Do you want a searchable purchase database from email, files, screenshots and receipt photos?**
Offer vendor/order/item/date/category/amount search; cross-source dedupe; UPC/GTIN/SKU/part/model extraction; readable evidence links; line-item categories/beneficiaries/assets; balanced allocations; and unresolved classification only after investigation.

### Shopping and procurement reconciliation
Ask: **Do you want a shopping/procurement list that automatically marks or updates items when LifeOS proves you bought them?**

If enabled, preserve one shopping intent per desired item/project. Confirmed purchases update the existing row with the actual product/model, vendor/order, status, Receipt ID and resolved date. Order revisions and replacement orders update the same shopping intent rather than creating duplicates. A cancelled item without a supported replacement remains open or becomes `Needs replacement`; a merely similar purchase never closes an item without evidence.

### Asset acquisition and inventory
Ask: **Do you want products/tools/equipment automatically added or enriched when receipts, product photos, model/serial plates or exact identifiers prove what they are?**
Offer tools/shop equipment, vehicles/parts, electronics/computers, appliances/home equipment, warranty/serial assets, hobby/technical equipment and user-defined domains.

Every canonical person/physical asset receives an immutable collision-resistant UUID that survives renames, ownership changes and database migrations. Friendly Asset IDs/names remain aliases. An asset may combine receipt + product photo + serial/model + manufacturer lookup into one identity. Search existing inventory first, preserve evidence, link the purchase line, enrich specs/warranty/compatibility and never invent an unreadable model/serial digit.

### Manuals and reference library
Ask: **Do you want product manuals, service manuals, datasheets and technical references saved so you can later ask for them by product, part number or asset?**

If enabled:
- accept an uploaded file, download/source URL, email attachment or existing Drive file;
- prefer/record authoritative manufacturer/OEM provenance where available;
- retain the original in the canonical Drive `Manuals & Reference` hierarchy;
- dedupe the same document across upload/email/link sources;
- give each knowledge object an immutable Knowledge UUID;
- index title, manufacturer, model, part/SKU, revision/date, tags and related asset UUID(s);
- answer later queries from the retained source and return the canonical Drive link plus page/section when supported.

This Drive/Sheet implementation is the interim file/index layer until a self-hosted database/object store is deployed; UUIDs and relationships must migrate unchanged.

### Receipt/account financial reconciliation
Ask: **Do you want LifeOS to reconcile expected purchase charges with connected financial accounts and surface unexplained differences?**
Keep supported merchant totals open until settlement/no-settlement resolution; reconcile same-order revisions first; detect possible over/under/duplicate/unmatched charges; distinguish reimbursement from merchant refund.

### Financial reports
Ask: **Do you want spending/household reports from verified receipts and, when separately connected, account-level finance data?**
Offer current/prior week, month, YTD, rolling 12 months, calendar years, merchant/category/asset/beneficiary, gross purchase, reimbursements and net household cost. Clearly distinguish receipt-detected coverage from complete account data.

### Subscriptions and trials
Ask: **Do you want subscriptions, price changes, renewal dates and trial-conversion risks detected?**
Never cancel/contact automatically.

### Important-mail triage
Ask: **Do you want important actionable email surfaced while routine mail stays quiet?**
Ask which domains/senders matter. External sends remain approval-gated.

### Calendar Projection
Ask: **Which verified LifeOS facts, if any, should also appear on Google Calendar?**
Offer independently: appointments/reservations; order delivery dates/windows; work trips/departures/arrival commitments; trial/subscription renewal/cancellation deadlines; bills/payment due dates; school/work deadlines; maintenance/warranty deadlines; selected tasks; user-defined event types.

For each enabled class collect target calendar, tentative-date behavior, automatic revision behavior, and completion/cancellation behavior. Use one projection/link row per source event so changes update rather than duplicate. Inviting other people is a separate permission/action boundary.

### Recipes
Ask: **Do you want a searchable recipe library from documents, links, images and notes?**
Store one canonical body with title, ingredients, directions, tags, provenance and optional nutrition/equipment.

### General knowledge capture
Ask: **Do you want verified facts, procedures, specifications, documents and source excerpts organized into a searchable knowledge store?**
Preserve source/provenance; retain relevant excerpts by default and full raw sources only when needed/pinned. Manuals/reference files use the dedicated manual-library workflow above.

## Work-pattern modules

### HOME / ROAD or equivalent
Only offer when actual work regularly takes the user away from home enough that brief behavior should differ. For non-travel roles bypass the subsystem entirely.

### Route, mileage and pay
Offer when work uses paid routes/miles/trips/commissions/per-diem or similar units. Track each actual current work leg separately; never assume the first destination returns directly home.

Ask whether company-paid terminal mileage is **symmetric by pair** or **directional**. Persist the user's actual rule. A historical employer/shared run sheet used as route knowledge imports only unique canonical terminal pairs by default, normalizes only proven aliases/typos, records mileage variants/provenance, and updates the existing Routes database. It does not create hundreds of duplicate historical Trips merely because the source repeats a route.

## Household, beneficiaries and reimbursements

Ask whether purchases may belong to another household member, friend/client or their asset, and whether reimbursements should be tracked. One merchant transaction remains one Receipt ID. Beneficiary/asset assignment and reimbursement are separate relationships; reimbursement does not erase gross spend or become a merchant refund.

## Default receipt taxonomy

Use a stable primary category plus flexible subcategories/tags. Starter primaries are user-editable:

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

Category changes never change Receipt ID/transaction identity.

## Lifecycle money semantics

A confirmed cancellation leaves active orders/shipments/current spend/inventory effects but remains auditable. Determine whether money settled before expecting a refund. Same-order revisions remain one transaction. A new merchant replacement order receives its own linked Receipt ID. Only an actually expected unresolved financial correction becomes an action after its configured deadline.

## First-boot recommendation behavior

Recommend a small default bundle based on the user's stated problems and verified dependencies, then walk through adjacent and remaining feature groups in small batches. Explain what each feature accomplishes and offer to guide any missing dependency setup. Users may enable/disable modules later without rebuilding unrelated state.