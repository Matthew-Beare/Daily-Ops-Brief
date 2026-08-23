# Receipt Line Classification, Fitment, and Financial Resolution

Load this reference together with `receipt-ingestion.md` for every purchase/receipt ingestion, cancellation/refund reconciliation, or inventory side effect.

## Line-item classification is authoritative

- One Receipt ID represents one underlying transaction, but its individual line items may belong to different categories, subcategories, cost owners, vehicles/assets, projects, and inventory destinations.
- Classify each identifiable line item independently. Never force every item on a mixed receipt into the receipt-level `Primary Category` or `Vehicle / Project` value.
- `Orders - Database.Primary Category` is a navigation summary only. Use the single dominant category when truly representative; use `Mixed / Multi-category` when no single category represents the receipt. `Search Categories` is the union of all line-item categories/tags.
- `Receipt Details - Expandable` holds the item-level category/asset identity. `Expense Ledger` holds the financial allocation. The included allocation rows for one Receipt ID must sum exactly to that transaction's one supported net total.
- One line item may itself serve multiple assets/projects. Split its cost through balanced allocations rather than duplicating the line or counting its full value more than once.
- A category or asset correction changes classification/allocation, never Receipt ID or source evidence.

## Part number and fitment evidence pass

When a purchased item has a manufacturer part number, vendor SKU, model, UPC, exact wheel/tire size, or another sufficiently specific identity, perform a fitment/identity evidence pass before final vehicle/asset assignment.

Evidence priority:

1. manufacturer or OEM catalog/specification;
2. vehicle/OEM parts catalog or manufacturer application guide;
3. merchant/vendor product page tied to the exact SKU;
4. reputable specialist catalog with an exact part-number match;
5. explicit user correction/assignment, which controls the user's intended asset relationship while preserving conflicting earlier evidence.

For automotive items, compare all material attributes that the evidence exposes rather than one convenient dimension:

- wheels: diameter, width, offset/inset, bolt pattern/PCD, center bore, load rating when available, brake/caliper clearance or application notes when available, and lug-seat/thread requirements when relevant;
- tires: exact size, load/speed specification, intended wheel setup, and proven vehicle/project context;
- OEM/replacement parts: exact part number and supersession chain, model year, trim, engine, transmission/drivetrain, axle/front-rear/left-right position, and other catalog qualifiers;
- studs/lugs/hubs: thread pitch, knurl/diameter, seat style, length, hub/application compatibility, and any known conversion already applied to the vehicle;
- electrical/electronic accessories: connector/interface, voltage/platform, model/application, and any required controller/ecosystem.

Assignment rules:

- If exact evidence plus the owned-asset registry uniquely resolves one asset and no material spec conflicts, auto-assign that asset and store a concise fitment note with the exact part/SKU and evidence source.
- If two or more owned assets remain plausible, evidence is incomplete, or any material fitment field conflicts, do not guess. Put the line in `Classification Queue` and ask the smallest useful question.
- Do not assign merely because a merchant page says `universal`, because one bolt pattern happens to match, or because a product title resembles a prior purchase.
- When no part/SKU is printed but exact manufacturer dimensions uniquely identify a catalog entry, enrich the receipt with that manufacturer part number and provenance.
- Preserve user-confirmed intended use even when the item is not a catalog-standard fitment, but record the distinction as `owner-assigned / custom fitment` rather than pretending the manufacturer application guide confirmed it.

Example: an Enkei GTC02 listed as `18x9.5 5x120 +45 Matte Black` resolves in Enkei's catalog to part `534-895-1245`. That evidence can enrich the line and be compared against the user's owned vehicles before asset assignment.

## Cancellation versus financial resolution

Cancellation state and money state are related but separate facts.

- A merchant-confirmed cancellation proves fulfillment/lifecycle cancellation. It does not by itself prove that a settled charge was refunded.
- Determine whether the cancelled amount ever settled. If the merchant revises the order before a charge settles and exact revised-order evidence shows the surviving amount, no fictional refund event is required; record the revised supported total and retain the cancelled line as excluded history.
- If the original/full amount settled, require credible reversal/refund evidence before marking the financial correction complete. Accept merchant refund confirmation, processor/card/bank posted credit/reversal, or another authoritative financial record.
- When connected account data is available, reconcile the cancellation against the likely payment account and amount/date window. Store only normalized proof needed for the audit: resolution state, confirmed amount, date, and source class/reference. Do not copy account balances, full account numbers, or unrelated transactions into the receipt archive.
- A pending authorization or pending credit is not a settled refund. Preserve the pending state and re-check through the normal lifecycle process.
- Absence of a matching financial transaction is not proof of refund/non-charge when account freshness/coverage is incomplete or unknown.

## Five-business-day unresolved-money rule

- Start the clock when merchant cancellation/refund eligibility is credibly confirmed or when a return is credibly accepted, whichever event creates the expected financial correction.
- If an expected refund/reversal or confirmed revised charge is still not proven after five business days, surface one compact `Action Required` in the next brief: vendor/order, unresolved amount if known, what evidence is missing, and the recommended bounded follow-up.
- Continue checking the existing receipt/order record; never create a separate reminder automation, duplicate receipt, or replacement financial transaction just to track the deadline.
- Clear the action once exact merchant or financial-account evidence resolves the money state. Append the resolution event; never erase the earlier exception.

## Audit requirements

A receipt cannot pass final Audit when any required item-level classification, fitment assignment, or expected financial correction remains falsely represented as verified.

The Audit gate must verify, where applicable:

- every line item has a verified or queued category and asset/cost-owner state;
- exact part/SKU evidence is retained when it was used to determine identity/fitment;
- no item or allocation is double-counted across categories/assets;
- included allocations equal the one supported transaction total;
- a cancelled line is absent from active fulfillment and spend while preserved as history;
- any settled cancelled/returned amount has a resolved refund/reversal state or a visible five-business-day exception;
- replacement relationships remain separate from refund accounting.
