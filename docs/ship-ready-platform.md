# mirror ship-ready platform contract

## Goal

A feature is implemented once against the mirror API and shared client surface, then appears on web, Windows, Linux and Android without cloning business policy into four applications.

## Client parity

- Web/PWA owns the shared interactive UI.
- Windows and Linux wrap that same UI with Tauri and add native capabilities only where required.
- Android embeds the same UI and exposes native bridges for background reminders, Text-to-Speech, camera/barcode scanning, file selection and external label/provider flows.
- CLI remains an automation/admin surface against the same versioned API.
- `starter/clients/release.json` is the compatibility authority. Clients preflight `/v1/compatibility` and must refuse mutations across an unsupported API major.
- Official command clients send an `Idempotency-Key`; mirror reserves it before mutation and replays the committed response on retry.

A new product feature should normally require one API/domain implementation and one shared UI implementation. Platform-specific work is reserved for actual hardware/OS boundaries.

## mirror connection model

The mirror service is the stable connection point. Clients never connect directly to Sheets, PostgreSQL, Drive, OneDrive or another authority. The service validates mutations, writes canonical state through the selected authority adapter, verifies readback and returns a common read model.

The starter self-hosted service is Docker-ready and exposes inventory/category/location/identifier/evidence/label and provider-login surfaces. Its SQLite database is a portable single-node starter authority. A later PostgreSQL migration must preserve UUIDs, events and provider evidence bindings rather than changing domain semantics.

Production API mutations default to bearer-token authentication. Health, compatibility discovery and OAuth callback/start surfaces remain reachable without the mirror bearer token. OAuth provider tokens are encrypted separately from the mirror API access token.

## Provider policy

Google Workspace is the default onboarding profile, using incremental OAuth consent. Microsoft 365 is a first-class alternate profile. Apple/iCloud is a deliberate manual/portability lane unless a specific verified adapter exists; mirror does not pretend general iCloud Drive access exists.

Google Drive and OneDrive are implemented evidence adapters, not just login buttons. A successful cloud evidence upload records a provider object ID/locator and requires provider readback before mirror reports the replication as verified. The local evidence copy remains a service cache/recovery copy; the canonical evidence UUID and SHA-256 hash do not change when the storage provider changes.

OAuth client secrets and refresh tokens are deployment secrets, never source. Provider tokens require encrypted server-side storage. Refresh-token rotation preserves an existing refresh token when an incremental provider response omits a replacement. OAuth return targets are constrained to local paths or the configured mirror public origin.

Gmail, Calendar, Drive and Sheets permissions are requested incrementally according to enabled capabilities rather than bundled into one enormous consent screen. Provider health reports verify which granted Google/Microsoft capabilities are actually reachable with the current token.

## Inventory path

The common domain supports:

1. hierarchical categories such as `Tools > Sockets > Tekton`;
2. hierarchical locations such as `Shop > Loft > Aisle 3 > Shelf B > Bin 7`;
3. asset create/edit/read models with immutable UUID identity;
4. relocation as an audited mutation;
5. commercial or preprinted barcode/QR aliases bound to an existing asset;
6. unmatched scans routed to classification/assignment rather than inventing identity;
7. arbitrary evidence/file attachment plus image/photo roles;
8. printable QR or Code 128 SVG labels generated from the immutable asset UUID.

The printed code is an alias/reference. It never becomes the only canonical identity.

## Docker customer deployment

`starter/service/docker-compose.example.yml` is the reference single-node deployment. Copy `starter/service/.env.example` to an untracked local `.env` and configure at minimum:

- `MIRROR_ACCESS_TOKEN`: a long random bearer token for the mirror API;
- `MIRROR_TOKEN_KEY`: a Fernet key used only to encrypt OAuth tokens at rest;
- `MIRROR_PUBLIC_BASE_URL`: the HTTPS public/private-overlay origin clients will use outside localhost;
- the exact Google or Microsoft OAuth client ID/secret and callback URI for providers being enabled.

Google Workspace is selected by default. `MIRROR_EVIDENCE_PROVIDER=auto` uses Google Drive when the Google profile is connected, Microsoft/OneDrive when the Microsoft profile is selected/connected, and local evidence storage when no cloud evidence adapter is connected. `GOOGLE_DRIVE_FOLDER_ID` may constrain app-created evidence to an operator-selected Drive folder.

For a remote customer device, publish mirror behind TLS or an authenticated private overlay. Do not expose SQLite, an eventual PostgreSQL service, or object-store credentials directly to clients.

## Android release rule

The Android workflow always compiles debug and release variants. Production signing material is never committed. A stable release keystore must be stored in GitHub Actions secrets using:

- `MIRA_ANDROID_KEYSTORE_BASE64`;
- `MIRA_ANDROID_KEYSTORE_PASSWORD`;
- `MIRA_ANDROID_KEY_ALIAS`;
- `MIRA_ANDROID_KEY_PASSWORD`.

When those secrets are present, Gradle signs the release variant and CI verifies the APK with Android `apksigner`. The release artifact includes a machine-readable signing-status file. An unsigned release build or debug build is suitable for engineering/pilot validation only; it is not evidence of a production-upgradable Android release.

## Release evidence

A release may be described as repository/build-gate ready only when the exact candidate SHA has green canonical CI, Docker smoke, Android, desktop and distribution workflows. A customer-facing claim must separately identify any unverified external dependency such as production OAuth credentials, Android signing credentials, HTTPS deployment, or physical scanner/device behavior.

Automated builds prove compilation and contract behavior. They do not prove a particular camera, Bluetooth scanner, label printer, NFC reader, Android OEM power-management policy or provider tenant until that hardware/provider path has been exercised and read back.

## Docker rule

Docker is a deployment option, not a feature-development fork. Domain code, provider adapters and API contracts are identical inside or outside a container. A feature cannot require Docker-specific paths or container state. Persistent state is mounted externally and provider secrets arrive at runtime.
