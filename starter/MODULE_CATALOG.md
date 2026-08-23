# LyfeOS First-Boot Module Catalog

After the four kickoff questions, present modules conversationally in small groups. Do not silently enable optional modules. Explain the outcome, required apps/data, write behavior and approval boundaries. Missing dependencies route through `DEPENDENCIES.md` instead of being hand-waved.

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

### Asset acquisition and inventory
Ask: **Do you want products/tools/equipment automatically added or enriched when receipts, product photos, model/serial plates or exact identifiers prove what they are?**
Offer tools/shop equipment, vehicles/parts, electronics/computers, appliances/home equipment, warranty/serial assets, hobby/technical equipment and user-defined domains.

An asset may combine receipt + product photo + serial/model + manufacturer lookup into one stable Asset ID. Search existing inventory first, preserve original evidence, link the purchase line, enrich exact specs/warranty/compatibility and never invent an unreadable model/serial digit.

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
Offer independently:
- appointments/reservations;
- order delivery dates/windows;
- work trips/departures/arrival commitments;
- trial/subscription renewal or cancellation deadlines;
- bills/payment due dates;
- school/work deadlines;
- maintenance/warranty deadlines;
- selected tasks;
- user-defined event types.

For each enabled class collect target calendar, tentative-date behavior, automatic date-revision behavior, and whether completion/cancellation removes or marks the event. Use one canonical projection/link row per source event so changes update rather than duplicate. Inviting other people is a separate permission/action boundary.

### Recipes
Ask: **Do you want a searchable recipe library from documents, links, images and notes?**
Store one canonical body with title, ingredients, directions, tags, provenance and optional nutrition/equipment.

### Knowledge capture
Ask: **Do you want verified facts, procedures, specifications, documents and source excerpts organized into a searchable knowledge store?**
Preserve source/provenance; retain relevant excerpts by default and full raw sources only when needed/pinned.

## Work-pattern modules

### HOME / ROAD or equivalent
Only offer when actual work regularly takes the user away from home enough that brief behavior should differ. For non-travel roles bypass the subsystem entirely.

### Route, mileage and pay
Offer when work uses paid routes/miles/trips/commissions/per-diem or similar units. Track each actual leg separately; never assume first destination returns directly home.

Ask whether company-paid terminal mileage is **symmetric by pair** or **directional**. Persist the user's actual rule. Employer/shared run sheets are evidence imports into the existing Routes/Trips/Mileage model; dedupe by stable run/date/terminal/miles evidence and never create another route database.

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

Recommend a small default bundle based on the user's stated problems and verified dependencies, then offer adjacent modules. The user can enable/disable modules later without rebuilding unrelated state.
