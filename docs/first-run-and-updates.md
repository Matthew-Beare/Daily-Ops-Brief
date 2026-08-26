# MIRA // MIRROR 1.0 Pilot: first run and updates

This guide is written for a person who has never used Git, GitHub, Docker, OAuth, or a command line.

## What MIRA and MIRROR are

- **MIRA** is the application and assistant you interact with.
- **MIRROR** is the reality layer that stores identities, evidence, locations, settings, and operational state.
- The same MIRA experience is intended for Android, Windows, Linux, and web.
- A feature requested in Feature Studio is for **all supported platforms automatically**. You do not have to remember to select Android, Windows, Linux, or web.

## First run

When MIRA opens for the first time, it shows a guided setup. Nothing chosen here is permanent. Everything can be changed later under **Setup & Settings**.

1. Choose Personal, Family, or Institutional Pilot.
2. Turn optional capabilities on or off. Inventory, receipts, orders, and safe updates have sensible defaults. RFID/NFC, Home Assistant, BLE proximity, and UWB ranging remain optional.
3. Choose **Continue with Google** if you want Google identity or Workspace integrations. Google shows the permission screen; MIRA never asks for or stores your Google password.
4. If you want custom features, choose **Create GitHub account** if you do not already have one. GitHub requires you to complete its account creation and verification yourself.
5. Return to MIRA and choose **Connect GitHub**. The production design uses a GitHub App with narrowly scoped repository permissions and short-lived credentials.
6. Finish setup. You can reopen the walkthrough or change settings later.

## Adding a custom feature

Open **Feature Studio** and describe what you want in normal language. Examples:

- Add maintenance intervals to inventory assets.
- Add a tool checkout workflow.
- Add a family pantry view.

You do **not** select target platforms. Every supported client is a target by default.

The delivery path is:

1. MIRA stores the request and acceptance criteria in MIRROR.
2. ChatGPT can refine the specification through the companion integration.
3. Executable changes go to a Git branch in the user's Personal Production repository.
4. Automated tests and package builds run.
5. If the new feature and upstream MIRA changes reconcile cleanly, the verified change is promoted without requiring the user to understand Git.
6. If custom code or policy genuinely conflicts with the incoming release, the update stops and explains what needs review. MIRA must not silently overwrite either side.
7. A verified release is offered to installed clients through the release channel.

Feature Studio never runs arbitrary generated code directly inside the live customer application.

## Updates

MIRA checks the configured verified release channel. CI artifacts are not treated as customer releases.

- **Normal case:** a newer compatible release is detected and the update is automatic or one press, depending on the installed platform and release channel.
- **HTTP 426 Upgrade Required:** the MIRROR server has refused a modifying request because the client is too old. MIRA opens the update flow instead of allowing the old client to change data.
- **Custom-feature conflict:** MIRA pauses source reconciliation and requires a person to review the collision. User-created features are not discarded to make an update easier.

The current pilot has update detection and the 426 user experience. Fully self-installing signed updates require each platform's production signing/update channel before they are called customer-ready.

## Inventory: the normal physical workflow

Every real item has one immutable MIRROR UUID. Codes and tags are replaceable identifiers attached to that UUID.

A typical intake flow is:

1. Create or find the asset.
2. Take a picture or attach an existing picture, receipt, manual, or other evidence.
3. Scan its existing UPC/barcode/QR code, print a MIRROR QR/Code 128 label, or on Android tap an NFC tag to enroll it.
4. Choose a location or scan a MIRROR location QR code.
5. MIRROR records the relationship between item UUID, identifiers, evidence, and location.

A damaged QR label or replaced NFC tag does not change the asset's identity.

## Migrating Google Sheets

Migration is deliberately staged so a spreadsheet cannot silently overwrite MIRROR.

1. Choose the Google migration option.
2. Google asks for separate read-only Drive/Sheets permission.
3. MIRA discovers the spreadsheets the account can read.
4. Select a spreadsheet.
5. MIRROR stages a snapshot and records its SHA-256 provenance hash.
6. Review/map the staged data.
7. Apply only after the mapping passes validation and existing UUIDs are preserved.
8. Read back and reconcile the imported records.

The pilot currently supports discovery and safe staging. Full automatic mapping/apply for every legacy schema remains a release requirement before migration can be advertised as one-click.

## Settings

**Setup & Settings** is the canonical user-facing settings page. ChatGPT companion tools read and modify the same MIRROR settings authority, so changing a setting in chat and changing it in the application do not create two different truths.

## If something goes wrong

MIRA should tell you what action is required. Do not delete the data folder, reinstall the server, create a second Personal Production repository, or manually copy database files just to fix an update. Those actions can destroy provenance or create two authorities.
