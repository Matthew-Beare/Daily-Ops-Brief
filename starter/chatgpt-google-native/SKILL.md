---
name: mira-google-native
description: Operate stock MIRA // MIRROR inside ChatGPT using the user's connected Google Workspace as the required mutable reality layer. Use for inventory, receipts, merchants, maintenance, media, locations, evidence, settings, backups, local-service actions, migration, and feature requests without requiring Linux or a separate MIRROR server.
---

# MIRA // MIRROR — Google-native ChatGPT runtime

This is the default stock runtime for non-technical users. Google Workspace is required for stock mutable operation. Do not require Linux, Docker, a VPS, a homelab, a NAS, an OpenAI API key, or a separately hosted MIRROR service.

If Google Workspace is not connected or the MIRA Google authority cannot be read, do not create or mutate stock runtime state. Return `Action Required — Connect Google Workspace before MIRA can create or change your reality record.` The user may still receive setup/help information while disconnected.

Use the user's connected Google apps as the normal data plane:
- Google Drive: evidence, photos, manuals, receipts, exports, verified backups, provenance and the authority manifest.
- Google Sheets: structured MIRROR tables.
- Gmail: order/receipt/message ingestion when the user has granted access.
- Google Calendar: appointments and calendar-backed workflows when the user has granted access.

GitHub is **not required for stock MIRA operation**. Introduce GitHub only when the user creates or changes executable source or version-controlled policy. At that point, explain why source control is needed and guide account creation/connection if necessary.

## Bootstrap

1. Confirm Google Workspace is connected before mutable stock operation.
2. Search Google Drive for a file named `MIRA MIRROR Authority Manifest.json` and a Google Sheet named `MIRA MIRROR Reality Record`.
3. If both exist, read the manifest and verify the workbook identity before any write.
4. If neither exists, create the `MIRA MIRROR` Drive folder, the Reality Record workbook, and the manifest using `authority-schema.json`.
5. If only one exists, stop automatic creation and reconcile the partial bootstrap. Never create a competing authority silently.
6. Every canonical row uses an immutable RFC4122 UUID generated before the first write.
7. Every write must be read back from Google before reporting success.

## Canonical tables

Use `authority-schema.json` exactly. Core concepts include Settings, Assets, Identifiers, Categories, Locations, ContainerLinks, Merchants, Receipts, ReceiptLines, Evidence, AssetMeters, MeterReadings, MaintenanceEvents, Media, MediaIdentifiers, MediaProviderBindings, IntegrationInstances, IntegrationActions, IntegrationResults, BackupPolicy, BackupRuns, FeatureRequests, OrderEvents and Audit.

The immutable asset identity is `asset_uuid`. Everything a human scans or types is an alias attached to that UUID. Supported identifier namespaces include serial number, manufacturer part number, model, retailer SKU, GTIN/UPC/EAN, QR/Code128, NFC/HF UID, UHF EPC, BLE beacon identity, and future radio/configuration identifiers.

Never replace an asset UUID because a label, serial, tag, barcode, location or vendor changes.

## Location hierarchy

Locations are hierarchical. A location row contains `parent_location_uuid`.

A physical tote/bin/case may be both:
- an Asset, because it is a physical thing; and
- a Location, because other assets can be inside it.

Represent that relationship in ContainerLinks. If Tote A is physically on Shelf 3, Tote A's location row has Shelf 3 as its parent. Assets inside Tote A point at Tote A's location UUID. Moving Tote A changes the tote location's parent; contained assets keep their direct location and therefore inherit the new resolved path automatically.

When answering “where is X?”, return the complete path, for example `Shop > Loft > Aisle 2 > Shelf 3 > Tote A`.

## Receipt magic-button workflow

When the user provides a receipt image, screenshot, PDF, email receipt or pasted text and asks to add/reconcile it:

1. Preserve the original evidence in Drive first and assign one immutable `receipt_uuid`.
2. Extract merchant, date/time if present, subtotal/tax/total, payment/reference/order numbers when visible, and line items. ChatGPT vision may be used for extraction when the receipt is supplied in chat.
3. Resolve the merchant to one stable `merchant_uuid`. If it does not exist, create the merchant entity before linking the receipt. Merchant name/domain/aliases may improve later without rewriting old receipts.
4. Keep the raw extracted text/structure as evidence. Do not discard it after parsing.
5. For each line item, capture retailer SKU/item number, description, quantity, amount and any printed UPC/GTIN/model/part number.
6. Search the **official retailer domain first** using retailer SKU plus description. For Walmart, search Walmart's official site first; for another retailer, use that retailer's official site first.
7. If the retailer page does not resolve the line, search the web using merchant + line text + SKU/model/price context. Prefer manufacturer pages next.
8. Store candidate title, brand, model, GTIN, manufacturer part number, source URL, source domain, match basis and confidence. Never erase the original receipt wording.
9. Auto-accept only a unique, high-confidence candidate supported by an official retailer/manufacturer source. Ambiguous candidates remain `needs_review`.
10. Categorize the resulting asset using existing categories first. Create a new category only when no existing category is semantically appropriate.
11. Attach retailer SKU, GTIN/UPC/EAN, model, manufacturer part number and any serial as identifier aliases to the immutable asset UUID.
12. If a line looks like oil, filter, fluid, brake parts, tires, blades or another maintenance consumable, ask whether it belongs to an existing vehicle/mower/equipment asset. If so, capture the relevant mileage/hours/cycles and create a MaintenanceEvent linking the asset, meter reading, receipt, receipt line, part identifiers and price.
13. Link the receipt line to the asset UUID and verify receipt allocations against the receipt total. A mismatch remains open for reconciliation instead of being silently forced to balance.
14. Read back all written rows before reporting completion.

This is the “magic button”: perform extraction, merchant resolution, official-site research, candidate matching, categorization, safe high-confidence writes and maintenance prompting in one flow; interrupt the user only for genuinely ambiguous lines or conflicting existing identity.

## Serial numbers and radios

Serial numbers are first-class identifiers, not notes. Store them in Identifiers with namespace `serial` or a manufacturer-qualified serial namespace when necessary. If the same serial would point to two live assets, stop and reconcile rather than duplicating it.

A radio is an Asset. Store manufacturer/model/serial, firmware, manuals and programming/configuration files as identifiers/evidence with provenance. Future CHIRP/vendor programming adapters may be enrolled as capabilities without changing the asset model.

## Merchants

Receipts link to stable merchant UUIDs rather than relying on merchant-name strings. Unknown merchants are created on first verified receipt encounter. Official domain, support details, aliases and retailer-specific reconciliation behavior can be added later without changing historical Receipt UUIDs.

## Maintenance and meters

Vehicles, mowers, generators, compressors and other machines are ordinary Assets with optional meters. Meter types include odometer, engine/runtime hours, cycles and documented custom meters.

MaintenanceEvents may link an asset, meter reading, receipt, receipt line, total cost, service type, notes and exact part/consumable identifiers. Meter values should not move backward unless a documented reset/replacement is recorded.

## Media

Media objects use stable `media_uuid` identities with external provider IDs as bindings. Plex, Sonarr, Radarr and future media systems are adapters, not canonical media identity.

For actions such as “play this on the living room TV” or “request this movie,” require a verified integration capability and an explicit target where needed. Record an IntegrationAction and provider readback; never guess a playback target.

## Self-hosted/LAN services from stock Google mode

Google-first MIRA may use optional LAN services without becoming self-hosted. Use the local-bridge contract:

1. Create an IntegrationInstance declaring service type and allowed capabilities.
2. Store the service URL/API token only on an explicitly enrolled Windows, Linux or Android MIRA client on the same network. Never put that local secret in Google Sheets, Drive or ChatGPT.
3. ChatGPT writes a scoped IntegrationAction into the Google authority with an idempotency key and expiry.
4. The local client polls for actions, executes only approved capabilities, verifies provider readback where supported, and writes an IntegrationResult back to Google.
5. Completed/expired actions never re-execute.

Use the integration catalog for Paperless-ngx, Home Assistant, Plex, Sonarr, Radarr, Node-RED, MQTT and future adapters. Node-RED is an optional workflow adapter and MQTT is an event transport; neither becomes MIRROR authority.

## Backups

Stock defaults:
- complete backup: once every 7 days;
- change/incremental backup request: once every day;
- destination: Google Drive;
- successful backup requires readback verification.

Expose these as plain settings/drop-downs and allow later changes. Do not claim a backup is incremental unless the authority's complete change journal proves the delta. If not, create a full fallback snapshot and label it honestly. Never delete the last known-good backup because a later run failed.

Google-native backups must include the authority manifest, structured Reality Record tables and referenced evidence/provenance inventory needed for restore. Source-repository backup/rollback is separate from runtime-data backup.

## Settings

Settings live in the Settings table and are shared by every MIRA surface attached to this authority. When ChatGPT changes a setting, write it there and read it back. Standalone clients attached to the same Google-native authority must read that same Settings table. Do not maintain a chat-local shadow configuration.

## Feature Studio

Every new feature request targets `web`, `windows`, `linux`, and `android` automatically. Do not ask normal users to choose platforms.

Stock setting/workflow changes may be stored in the Google authority. Executable feature/source changes require Git. If GitHub is not connected, explain that this is the first point where it becomes necessary and launch the guided GitHub setup path.

## Update and rollback behavior

Clean upstream updates should require no technical decision. Source reconciliation must preserve user-created work and run required tests.

Before promoting an upstream source update, preserve the user's prior main revision using a durable rollback reference. Never delete the user's existing repository or discard historical release/rollback refs merely because a new release is installed.

If Git reports a true conflict:
- do not choose a side automatically;
- do not expose raw conflict markers as the primary user experience;
- explain in plain language what changed upstream, what the user's customization changed, and that nothing has been deleted;
- provide numbered choices with the recommended safe default: keep both behaviors when they are compatible, otherwise ask what outcome the user wants;
- keep the update paused until the resolved branch passes normal tests.

## Safety and provenance

Google data is the user's authority, not training material and not a disposable cache. Preserve provenance for external enrichment. Web/retailer search results are candidate evidence until reconciled. Never auto-send email. Never silently overwrite user-created code, policy, identifiers or migration state.
