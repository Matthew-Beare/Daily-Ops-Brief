# Asset Acquisition and Evidence Enrichment

Load this reference when the user supplies a tool/equipment/product photo, model number, serial number, UPC/SKU/part number, receipt/invoice, warranty card, packaging label, or other evidence that should create/enrich an owned or external asset.

## Intake sources

An asset may be established from one or several sources: receipt email, photographed receipt, product photo, barcode/label photo, model/serial plate, manual, invoice, merchant order, manufacturer lookup, explicit user statement, or an already verified inventory record. These are evidence sources for one asset, not separate assets.

Inspect images directly before OCR fallback. Preserve originals in canonical Drive evidence when normal ingestion is authorized.

## Identity resolution

1. Extract stable identifiers exactly when visible: manufacturer, product name, model, manufacturer part number, SKU, UPC/EAN/GTIN, serial number, IMEI/MAC or domain-specific identifiers.
2. Normalize formatting but preserve the source text/provenance.
3. Search manufacturer/OEM documentation first, then exact vendor SKU/product pages, then reputable specialist catalogs.
4. Enrich evidence-backed specifications useful for future matching: dimensions, platform/battery family, voltage, compatibility/application, capacities, warranty, included accessories, color/variant, etc.
5. Never invent a serial/model digit that is unreadable. Queue the missing value only when it is actually required.

## Dedupe and ownership

Before creating an asset, search existing canonical asset/tool/inventory records by serial, model+purchase, part/SKU, receipt/order, photo/evidence hash and descriptive identity. Enrich an existing asset when evidence describes the same physical item.

- One physical asset gets one stable Asset/Tool ID.
- Multiple receipts/evidence objects may link to the same asset.
- A multi-quantity purchase may create multiple physical asset records only when individual tracking is useful or unique serials exist; otherwise retain quantity at the line/inventory level.
- Owner/beneficiary and related vehicle/project are separate relationships. A tool used on a vehicle does not become a vehicle part.

## Automotive fitment

For automotive parts, load receipt-classification-fitment.md too. Resolve part identity/application against the complete owned/external vehicle registry and known modifications. Use exclusion evidence. Unique fitment may be auto-assigned; material ambiguity is queued only after reachable evidence is exhausted.

## Receipt and warranty linkage

When purchase evidence exists:

- link the asset to the existing Receipt ID and exact receipt line rather than duplicating spend;
- preserve merchant/order/date/price evidence;
- capture warranty period/registration/support documentation only when supported;
- keep replacement/returned/disposed status as lifecycle state rather than deleting the original asset identity.

## Completion gate

Asset acquisition is complete only when identity/dedupe, ownership/beneficiary, evidence links, receipt relationship when applicable, searchable identifiers and any required fitment are either verified or precisely queued. Never mark acquisition complete because a photo was merely saved.
