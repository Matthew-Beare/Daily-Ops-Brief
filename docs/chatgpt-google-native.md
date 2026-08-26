# MIRA in ChatGPT with Google Workspace only

## The normal-user promise

A stock MIRA user does **not** need Linux, Docker, a NAS, a VPS, a homelab, a database server, or an OpenAI API key.

The normal deployment is:

**ChatGPT + connected Google Workspace = MIRA**

Google Drive/Sheets/Gmail/Calendar hold the user's mutable reality. MIRA's workflow instructions enforce UUID identity, provenance, reconciliation and readback. The optional standalone MIRROR service exists for people who want native clients, local/offline authority, institutional controls, or self-hosting.

## What the user connects

1. ChatGPT.
2. Google Drive / Google Workspace permissions needed for the features they select.
3. Gmail only if they want email/order/receipt ingestion.
4. Google Calendar only if they want calendar-backed workflows.
5. GitHub only if they later create executable/custom source features.

Do not ask a stock user to set up GitHub during first boot unless they choose Feature Studio source customization.

## First boot

MIRA should present the user with a guided wizard rather than a configuration document.

1. **Welcome** — MIRA is the assistant; MIRROR is the reality record.
2. **Use MIRA in ChatGPT** — recommended, no server to manage.
3. **Connect Google** — explain which Google permissions are used and why.
4. **Choose features** — Inventory, receipts/orders, calendar/reminders, Home Assistant, NFC/RFID/BLE are independently selectable.
5. **Identity basics** — an item gets one immutable UUID; serials, UPCs, retailer SKUs and tags are aliases.
6. **Locations** — show Shop > Loft > Aisle > Shelf > Tote and explain container inheritance.
7. **Updates** — safe updates happen automatically; genuine custom-code conflicts pause and are explained in plain language.
8. **GitHub only if needed** — Feature Studio can guide account creation/connection at the first executable source change.

Every step must have a Back button. Every option must remain editable later.

## Google permissions

Request only the Google surfaces required by selected features. Do not present a giant consent wall on first launch.

The tutorial should say in plain English:
- Drive access is for the MIRROR authority files, photos, receipts, manuals and exports.
- Gmail access is for user-approved mail/order/receipt workflows.
- Calendar access is for appointments/reminders.
- MIRA does not need the user to give Google credentials to a Linux server in Google-native mode.

Use official provider authorization pages for the actual consent. MIRA's own tutorial graphics are explanatory diagrams, not fake screenshots of provider consent pages that will rot the next time Google moves a button six pixels.

## Settings

In Google-native mode, settings are rows in the MIRROR Settings table. ChatGPT writes them and reads them back. Any standalone MIRA client connected to that same authority must use the same settings rows.

In hosted MIRROR mode, `/v1/settings` is the corresponding authority. Do not merge the two authorities silently; a migration explicitly changes authority.

## Feature Studio and GitHub

All feature requests target web, Windows, Linux and Android by default.

A settings/workflow change that does not create executable code can remain in the Google authority. An executable feature or policy-as-code source change requires Git. If the user has no GitHub account, MIRA explains why it is now needed, opens GitHub signup, then resumes at GitHub App authorization.

## Receipt workflow

The intended interaction is one command such as **“Reconcile this receipt.”** MIRA then:

1. preserves the original receipt;
2. extracts merchant/date/totals/line items;
3. searches the retailer's official site first using SKU + description;
4. falls back to manufacturer/other web evidence when necessary;
5. records every candidate and provenance URL;
6. auto-applies only unique high-confidence matches;
7. asks the human only about ambiguous lines;
8. categorizes assets using the existing hierarchy;
9. binds retailer SKU/GTIN/model/MPN/serial aliases to immutable asset UUIDs;
10. balances receipt allocations and leaves mismatches open.

## Physical identity

NFC is a form of RFID. Android can read compatible NFC/HF tags directly. UHF EPC Gen2 tags require a compatible UHF reader; ordinary phones do not contain that radio. BLE tags can provide rough proximity, and UWB-capable tags/devices can provide precise ranging, but these are separate hardware classes and should not be represented as interchangeable “RFID.”

## Production boundary

ChatGPT/Google-native operation removes the Linux requirement. It does **not** remove provider permissions, account-plan limitations, or the need to publish/approve the MIRA plugin/skill for the target ChatGPT plan/workspace. Keep those product-distribution concerns separate from the user's runtime architecture.
