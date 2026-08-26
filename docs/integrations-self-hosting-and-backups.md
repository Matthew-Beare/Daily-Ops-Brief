# Integrations, self-hosting, local services and backups

## Two product modes

MIRA has two deployment modes but one domain model.

### Stock: MIRA with Google Workspace

This is the normal consumer/personal setup.

- Google Workspace is required for mutable stock operation.
- ChatGPT is the conversational intelligence surface.
- Google Sheets/Drive/Gmail/Calendar provide the user-owned reality/data plane according to granted capability.
- No Linux server, Docker host, NAS, VPS or homelab is required.
- GitHub is optional until a user creates executable custom source/policy.
- Local/self-hosted services can still be added through an enrolled MIRA local bridge running on Windows, Linux or Android.

If Google is disconnected, MIRA may explain setup and recovery but must not silently create a competing stock authority.

### Full/self-hosted MIRROR

Advanced users may operate the MIRROR service locally or on infrastructure they control.

- Docker and Podman are supported deployment options, not product requirements.
- Windows users can run the service using Docker Desktop/compatible container tooling, but the Windows MIRA client itself does not require Docker.
- Linux users may run native/client packages independently from the optional service container.
- The container is a Linux OCI image and therefore runs through an OCI-compatible runtime even when the host is Windows.
- HTTPS should terminate at a trusted reverse proxy such as the included Caddy production profile.

A self-hosted migration must preserve UUID identity, provenance and export formats shared with Google-native mode.

## Local service enrollment

The Integrations screen is the stable home for future services. Each adapter declares:

- service type;
- connection mode;
- authentication type;
- read/write capabilities;
- dangerous capabilities that require explicit enablement;
- health/readback contract;
- whether it is available in Google-first local-bridge mode, direct self-hosted mode, or both.

Initial catalog/foundation entries include:

- Paperless-ngx: document search/read/ingest and future metadata updates;
- Home Assistant: state/events and opt-in service/shopping/media controls;
- Plex: library/search/player discovery and opt-in playback control;
- Sonarr/Radarr: library/search and opt-in media requests;
- Node-RED: read flows/status and advanced opt-in flow deployment;
- MQTT: subscription and explicit topic-allowlisted publishing;
- future solar/energy telemetry;
- generic HTTP adapter for advanced cases.

External services are adapters. They do not become canonical MIRROR authority merely because they are connected.

## Google-first local bridge

ChatGPT cannot directly address a private LAN host such as `192.168.x.x`. Stock MIRA therefore uses a local bridge rather than requiring a server.

1. The user enrolls a service in MIRA.
2. An MIRA Windows, Linux or Android client on the same LAN stores the service address and secret in local OS-protected storage.
3. ChatGPT writes a scoped Integration Action into the Google authority.
4. The local bridge claims the action, executes only the approved capability and records provider readback.
5. The result is written to the Google authority.
6. Local service credentials never enter ChatGPT or Google Sheets/Drive.

This lets a Google-first user operate Home Assistant, Plex, Paperless or similar services without running MIRROR as a server.

## Node-RED and MQTT

Node-RED and MQTT are useful integration tools but are not required core dependencies.

- Node-RED is an optional workflow adapter for unusual local automation.
- MQTT is an event transport for telemetry and commands.
- Neither is a data authority.
- Canonical rules remain in MIRROR policy/domain code rather than being scattered across arbitrary Node-RED flows/topics.
- MQTT publishing must use an explicit topic allowlist and appropriate TLS/authentication when traffic leaves a trusted LAN.

This reserves a clean future path for solar, energy, environmental and device telemetry without forcing those systems into the v1 product before their architecture is known.

## Paperless-ngx

Paperless can be added as a document-management adapter without replacing MIRROR evidence identity.

A document ingested into Paperless keeps its MIRROR `evidence_uuid`, hash and relationships. The Paperless document ID becomes a provider binding. Search/read/ingest can be enabled independently. Metadata writes remain opt-in and require provider readback.

## Media

MIRROR owns provider-neutral media identity. Plex/Sonarr/Radarr IDs are provider bindings.

This allows requests such as:

- play a known media item on an explicitly selected Plex player;
- request a movie through Radarr;
- request a series through Sonarr;
- reconcile available library state back into MIRROR.

MIRA must not guess playback targets or silently execute a write capability that was not enabled.

## Maintenance and equipment purchases

Vehicles, mowers, generators, compressors and similar equipment are normal Assets.

They may have:

- odometer readings;
- engine/runtime hours;
- cycles;
- maintenance events;
- receipt and receipt-line relationships;
- exact part/SKU/GTIN/manufacturer part-number relationships;
- costs and evidence.

When a receipt line looks like oil, filters, fluids, brake parts, tires, blades or another maintenance consumable, MIRA may ask whether it belongs to an existing equipment asset. If accepted, the maintenance event links the equipment UUID, meter reading, receipt, line item, identifiers and cost.

## Radios

A radio is an Asset. Manufacturer/model/serial/FCC ID/firmware are identifiers or metadata, while manuals, photos and programming/configuration exports are evidence.

Future CHIRP or manufacturer-programming adapters should save a versioned pre-write configuration snapshot, apply the requested configuration, verify device readback when possible and preserve the older configuration for rollback. Reprogramming a radio never creates a new asset identity.

## Paid integrations

Future paid provider/lookup/connectors use a separate entitlement boundary.

An entitlement may disable one connector capability. It may never:

- lock a user out of core Google-native MIRA;
- lock a self-hosted user out of core MIRROR;
- delete user data;
- prevent export;
- silently create a recurring charge.

External cost must be shown before activation and recurring billing requires explicit user acceptance.

## Backups

Boomer-mode defaults:

- complete backup: once a week;
- change/incremental request: once a day;
- stock destination: Google Drive;
- alternate destinations: OneDrive or self-hosted local storage.

A backup is successful only after provider/readback verification. Until every mutation path has a certified complete change journal, an incremental request is fulfilled as a clearly labelled full fallback snapshot rather than falsely claiming it contains only changed data.

Source-code rollback is separate from runtime-data backup. Before an automatic upstream source update, Personal Production preserves the previous main revision under a durable `mira-rollback/...` tag. Updates never delete the existing repository or its history.

## HTTPS and browser trust

A public/self-hosted HTTPS deployment needs a hostname and certificate trusted by the user's devices. The included Caddy profile can obtain/renew public ACME certificates when the hostname/DNS/network path qualifies.

For an isolated LAN-only hostname that cannot receive a public certificate, use a managed private CA and install that CA on client devices. MIRA must not train users to click through browser certificate warnings or disable TLS verification.
