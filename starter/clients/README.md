# M.I.R.R.O.R. client surfaces

The baseline client is one installable **Progressive Web App (PWA)** shared by Android, Windows, Linux and ordinary web browsers. Native helpers are deliberately small and exist only where the operating system exposes capabilities a browser cannot reliably provide.

## Baseline PWA

`clients/pwa/` is the first usable client surface. It provides:

- camera barcode/QR capture through the browser `BarcodeDetector` API when the browser/device supports it;
- manual identifier entry;
- keyboard-wedge USB/Bluetooth barcode scanner entry, because those scanners normally type the decoded code followed by Enter;
- idempotent scan-command envelopes for the M.I.R.R.O.R. service API;
- local pending-sync queue when the API is unavailable;
- installable PWA metadata and static offline shell;
- foreground Text-to-Speech preview for testing speech wording.

Camera access and service workers require a secure browser context, normally HTTPS or localhost. The PWA never receives database credentials and never treats a locally decoded barcode as canonical product identity. The service/core validates and resolves the scan.

## Android

Use the PWA for normal UI and camera barcode/QR scanning. A thin native Android companion is the target for capabilities that require native/background privileges:

- reliable background appointment notifications;
- Android Text-to-Speech generation after a due spoken-reminder intent arrives;
- audio routing through whatever output Android has selected, including supported Bluetooth hearing aids/headsets;
- NFC tag observations;
- future local hardware bridges when useful.

M.I.R.R.O.R. sends reminder text, timing, reminder UUID and privacy/detail policy. **Android's selected Text-to-Speech engine generates the actual voice locally.** The server does not generate an audio file and does not force a Bluetooth route.

The PWA `speechSynthesis` control is only a foreground preview/test. It is not evidence of reliable background spoken delivery.

## Windows and Linux

Use the same PWA as the normal user interface. It can be installed from a supporting Chromium-family browser and opened like an application.

USB/Bluetooth scanners that operate as keyboard-wedge/HID devices work with the scan input without a special driver inside M.I.R.R.O.R. Camera scanning works where the browser exposes camera + `BarcodeDetector` support.

A future optional desktop/local agent is for OS/hardware duties, not a second business application. Examples:

- serial/USB reader SDK bridge;
- UHF RFID reader bridge;
- local file-watch/evidence import when explicitly enabled;
- native tray/background notifications;
- local model runtime adapter;
- private service discovery.

Linux is also the preferred self-hosted always-on service/adapter host. `systemd` timers provide deployment-owned scheduling while the PWA remains the UI.

## RFID/NFC

RFID is an adapter into the same immutable asset/location model, not a separate inventory database. See `../rfid-asset-tracking-contract.json`.

- Android NFC can submit near-field observations through the native companion.
- USB/serial/HID/network readers can submit observations through a Linux/desktop agent.
- EPC Gen2/UHF repeated reads are presence evidence and are deduplicated/bounded.
- a single passive read never silently moves an asset;
- only an explicitly configured, corroborated zone-transition policy may promote presence evidence to a canonical location event, and that write still requires idempotency + readback.

## Security boundary

All clients talk to the versioned service API in `../client-api-contract.json`. They do not connect directly to PostgreSQL, Google Sheets, Microsoft Lists, object storage or another canonical authority. Provider credentials stay server/adapter-side.
