# MIRA in ChatGPT with Google Workspace only

## The normal-user promise

A stock MIRA user does **not** need Linux, Docker, a NAS, a VPS, a homelab, a database server, an OpenAI API key, or the MIRA app.

The normal deployment is:

**ChatGPT + connected Google Workspace = MIRA**

Google Drive/Sheets/Gmail/Calendar hold the user's mutable reality. MIRA's workflow instructions enforce identity, provenance, reconciliation and readback. The optional MIRA app is a first-class display and data-ingestion companion. The optional self-hosted MIRROR service exists for people who want local/offline authority, institutional controls, or advanced self-hosting.

## What MIRA, MIRROR and the app mean

- **MIRA is the assistant.** The user talks to MIRA primarily in ChatGPT. MIRA reasons, plans, reconciles, recommends and performs approved actions.
- **MIRROR is the private reality record underneath MIRA.** It keeps durable settings, identities, evidence, relationships, history and structured state.
- **The MIRA app is optional.** It is one display/ingestion surface for MIRROR: dashboards, scanning, photos, receipts, inventory, NFC/BLE, kiosk displays, notifications and quick settings. It is not required to use MIRA and it is not a second assistant.

ChatGPT can answer in chat, write a structured result into MIRROR for the app to display later, or do both when the user's intent calls for both.

## What the user connects

1. ChatGPT.
2. Google Drive / Google Workspace permissions needed for the features they select.
3. Gmail only if they want email/order/receipt ingestion.
4. Google Calendar only if they want calendar-backed workflows.
5. The MIRA app only if they want a native display/ingestion companion.
6. GitHub only if they later create executable/custom source features.

Do not ask a stock user to install the MIRA app or set up GitHub as a prerequisite for ordinary MIRA use.

## First initialization in ChatGPT

The **primary life interview occurs when MIRA is initialized in ChatGPT**. It is conversational, Boomer-safe, and establishes the shared MIRROR profile and settings.

The interview should:

1. **Welcome** — explain MIRA and MIRROR in one sentence each.
2. **Connect Google** — establish the Google-backed MIRROR authority and explain permissions in plain English.
3. **Profile and priorities** — collect only the ordinary context needed for selected features.
4. **Choose life domains** — inventory, receipts/orders, calendar/reminders, meal planning, weather, health/nutrition, maintenance, home automation and other supported domains are opt-in or configurable as defined by their own feature contracts.
5. **Ask conditional follow-ups** — only ask detailed questions for features the user enabled.
6. **Explain optional app** — offer the MIRA app as an optional display/ingestion companion, not as a requirement.
7. **GitHub only if needed** — guide source-control setup when executable/custom source is first requested.
8. **Read back settings** — verify that the resulting profile was written to MIRROR before reporting setup complete.

## First boot of the MIRA app

The app **also keeps its guided wizard**. Do not remove it or replace it with a link to ChatGPT.

Its purpose is different from the ChatGPT interview:

1. explain that MIRA is the assistant and MIRROR is the private reality record;
2. connect the app/device to the user's MIRROR authority;
3. launch real Google authorization for stock Google-first users;
4. request device permissions such as camera, notifications, NFC/Bluetooth or always-on display only when relevant;
5. confirm or edit shared feature settings;
6. teach the app's capture/display workflows;
7. offer missing profile questions only if the primary ChatGPT interview was never completed; and
8. write every shared answer back to the same MIRROR settings authority.

A user who already completed the ChatGPT interview should not be forced through the entire life interview again in the app. A user who installs the app first should still be able to complete enough setup to use it and later continue the richer conversational interview in ChatGPT.

Every step must have a Back button. Every option must remain editable later. A primary button must never silently do nothing: it must perform the action, navigate to a prerequisite, or show a plain-English blocker.

## Google permissions

Request only the Google surfaces required by selected features. Do not present a giant consent wall on first launch.

The tutorial should say in plain English:
- Drive access is for MIRROR authority files, photos, receipts, manuals and exports.
- Gmail access is for user-approved mail/order/receipt workflows.
- Calendar access is for appointments/reminders.
- MIRA does not need the user to give Google credentials to a Linux server in Google-native mode.

Use official provider authorization pages for the actual consent. MIRA's own tutorial graphics are explanatory diagrams, not fake screenshots of provider consent pages that will rot the next time Google moves a button six pixels.

The stock app's **Continue with Google** action must launch a real supported Google authorization path. It must not depend solely on a separately configured hosted MIRROR API. If the required Google registration or transport is unavailable, the app must explain that clearly instead of presenting a dead button.

## Settings

In Google-native mode, settings are rows in the MIRROR Settings table. ChatGPT and any attached MIRA app read and write the same settings rows.

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
9. binds retailer SKU/GTIN/model/MPN/serial aliases to permanent asset identities;
10. balances receipt allocations and leaves mismatches open.

## Physical identity

NFC is a form of RFID. Android can read compatible NFC/HF tags directly. UHF EPC Gen2 tags require a compatible UHF reader; ordinary phones do not contain that radio. BLE tags can provide rough proximity, and UWB-capable tags/devices can provide precise ranging, but these are separate hardware classes and should not be represented as interchangeable “RFID.”

## Production boundary

ChatGPT/Google-native operation removes the Linux and MIRA-app requirements. It does **not** remove provider permissions, account-plan limitations, or the need to publish/approve the MIRA ChatGPT integration for the target plan/workspace. Keep those product-distribution concerns separate from the user's runtime architecture.
