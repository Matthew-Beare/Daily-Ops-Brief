# Capability and Existing-Evidence Discovery

First boot should discover what is already available before asking a user to rebuild their life manually or connect redundant services.

## Discovery order

1. **Current conversation and supplied files:** use facts/evidence already present.
2. **File Library / uploaded material when available:** search relevant existing files before requesting re-entry.
3. **Connected apps/tools/connectors:** inspect available capabilities and perform harmless bounded reads only when relevant.
4. **Existing canonical authorities:** detect usable Sheets/databases/Drive folders/calendars/repositories instead of automatically creating replacements.
5. **Available plugins/apps:** when a selected workflow needs an unavailable external capability, search supported integrations before declaring it impossible or giving manual workaround instructions.
6. **User interview:** ask only for information that evidence/capability discovery cannot resolve or that requires preference/consent.

Do not claim global access to arbitrary old ChatGPT conversations. If useful prior-chat content is not accessible from the current surface, ask the user to open/share/export the relevant conversation or move its durable information into an accessible canonical source. Once ingested, the old chat should not remain the only authority.

## Capability map

Build a temporary setup-time capability map such as:

| Capability | Example use | Gate |
|---|---|---|
| Git write | personal source/versioning | bounded write + remote readback |
| Drive/Docs/Sheets | state/evidence/docs | harmless read; write only after provisioning approval |
| Gmail | appointment/order/receipt/admin evidence | bounded full-message read when selected |
| Calendar | appointment and selected event projection | read first; create/update verification after approval |
| Financial data | transaction reconciliation | account coverage/freshness check |
| Fitness/activity integration | exercise evidence/progression | only user-selected metrics and permissions |
| Maps/weather/travel tools | trip/vacation planning | use only when selected/relevant |
| Other plugin/app | domain-specific workflow | inspect permissions/dependencies before relying on it |

The map is not permanent state by itself. Durable selected integration configuration belongs in the deployment source/config; live credentials remain with the provider.

## Existing-workflow import

For each selected domain ask: **Do you already have a system, plan, list, library, history, or connected app for this?**

When yes:
- inspect reachable evidence first;
- identify the existing authority and data quality;
- dedupe before import;
- preserve provenance;
- migrate only what is useful;
- do not create a second authoritative database by default.

This is especially important for recipes/meal plans, exercise history, calendars, school documents, projects, assets, receipts, and existing Git-based customizations.

## Fitness and wearable sources

If a fitness/wearable/activity connector is already available, offer it as optional evidence for selected routines. Do not assume a specific brand or that a connected service exposes every metric. Use only supported fields the user selects. Never infer medical diagnoses, injury status, or unsafe training progression from activity data.

## Discovery should create recommendations

The purpose is not merely to inventory apps. Cross-reference life friction with available capabilities. Examples:
- frequent missed appointments + Gmail + Calendar → offer verified appointment reconciliation;
- existing recipes + grocery friction → offer meal planning and shopping-intent integration;
- recurring hiking + Calendar/maps/weather → offer trip/hike planning and preparation checklists;
- travel-heavy job + limited away connectivity → offer context modes and offline-preparation workflows;
- exercise goal + activity connector → offer evidence-backed accountability/progression;
- retired user + appointment/admin load → offer appointments, renewals, documents, medication-refill reminders only if requested and supported, without medical advice.

The system should reveal adjacent useful options without enabling them silently.

## Dependency minimization

Every module declares the smallest dependency set it actually needs. Core onboarding/Git/versioning must not depend on Gmail, Calendar, finance, fitness, or another optional connector. Optional connector failure is section-scoped and must not break unrelated modules.

Prefer:
- one canonical authority per data class;
- one durable Git lineage per deployment;
- one consolidated scheduler dispatcher per cadence/purpose rather than per-record jobs;
- Calendar events for event-specific reminders rather than one ChatGPT task per appointment;
- adapters around optional integrations rather than cross-module direct coupling;
- readback/verification at module boundaries.

This reduces the number of layers that can fill their pants at once.