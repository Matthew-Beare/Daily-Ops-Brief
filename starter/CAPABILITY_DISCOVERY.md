# Capability and Existing-Evidence Discovery

First boot should discover what is already available before asking a user to rebuild their life manually or connect redundant services. For new-user deployments, private Git is the canonical personal-state authority; connected apps provide evidence, projections, or actions around that state.

## Discovery order

1. **Private deployment Git:** verify/read the current deployment repo and existing state/config first.
2. **Current conversation and supplied files:** use facts/evidence already present.
3. **File Library / uploaded material when available:** search relevant existing files before requesting re-entry.
4. **Connected apps/tools/connectors:** inspect available capabilities and perform harmless bounded reads only when relevant.
5. **Existing external systems:** detect calendars, Drive folders, Sheets/databases, finance sources, wearables, or other systems that may contain useful evidence to import/reconcile rather than automatically creating replacements.
6. **Available plugins/apps:** when a selected workflow needs an unavailable external capability, search supported integrations before declaring it impossible or giving manual workaround instructions.
7. **User interview:** ask only for information that evidence/capability discovery cannot resolve or that requires preference/consent.

Do not claim global access to arbitrary old ChatGPT conversations. If useful prior-chat content is not accessible from the current surface, ask the user to open/share/export it. Once approved and normalized, durable state should be committed into the private Git deployment so the old chat is no longer required.

## Capability map

Build a temporary setup-time capability map such as:

| Capability | Example use | Role | Gate |
|---|---|---|---|
| Private Git write | personal state + source/versioning | canonical authority | bounded write + remote readback |
| Drive/Docs/Sheets | import/export/bulky evidence | optional adapter | harmless read; write only after approval |
| Gmail/email | appointment/order/receipt/admin evidence | optional evidence adapter | bounded full-message read when selected |
| Calendar | appointment/event projection + reminders | optional projection adapter | read first; create/update/readback after approval |
| Financial data | transaction evidence | optional evidence adapter | account coverage/freshness check |
| Fitness/activity integration | exercise evidence/progression | optional evidence adapter | only supported user-selected metrics |
| Maps/weather/travel tools | trip/vacation planning inputs | optional current-input adapter | use only when relevant |
| Other plugin/app | domain-specific workflow | optional adapter | inspect permissions/dependencies first |

The capability map is setup-time reasoning, not canonical state by itself. Selected capability configuration and stable provider references belong in private Git. Credentials remain with providers.

## Existing-workflow import

For each selected domain ask: **Do you already have a system, plan, list, library, history, or connected app for this?**

When yes:
- inspect reachable evidence first;
- identify what is useful and its data quality;
- dedupe before import;
- preserve provenance/source references;
- normalize only approved useful data into Git state;
- do not maintain a second hidden authoritative database by default.

This is especially important for recipes/meal plans, exercise history, calendars, school documents, projects, assets, receipts, and existing Git-based customizations.

An existing external system may remain the authoritative source for facts that inherently belong to that provider during collection, such as a Gmail message or bank transaction, but LyfeOS's accepted personal operational state and reconciliation result live in the private Git deployment.

## Fitness and wearable sources

If a fitness/wearable/activity connector is already available, offer it as optional evidence for selected routines. Do not assume a specific brand or that a connected service exposes every metric. Use only supported fields the user selects. Never infer medical diagnoses, injury status, or unsafe training progression from activity data.

Accepted activity/completion/progression facts may be written as Git state events after the configured evidence rule is satisfied.

## Discovery should create recommendations

The purpose is not merely to inventory apps. Cross-reference life friction with available capabilities. Examples:
- frequent missed appointments + Gmail + Calendar → offer verified appointment reconciliation with canonical Git state;
- existing recipes + grocery friction → offer meal planning and shopping-intent integration;
- recurring hiking + Calendar/maps/weather → offer hike/trip preparation and vacation planning;
- travel-heavy job + limited away connectivity → offer context modes and offline-preparation workflows;
- exercise goal + activity connector → offer evidence-backed accountability/progression;
- retired user + appointment/admin load → offer appointments, renewals, documents, and reminders only when useful, without forcing a work model.

The system should reveal adjacent useful options without enabling them silently.

## Dependency minimization

Every module declares the smallest dependency set it actually needs. Core onboarding/state/versioning must not depend on Gmail, Calendar, finance, fitness, or another optional connector. Optional connector failure is section-scoped and must not break unrelated modules.

Prefer:
- one canonical personal-state authority: private Git;
- one durable Git lineage per deployment;
- one consolidated scheduler dispatcher per cadence/purpose rather than per-record jobs;
- Calendar events for event-specific reminders rather than one ChatGPT task per appointment;
- adapters around optional integrations rather than cross-module direct coupling;
- Git and provider readback/verification at transaction boundaries.

This reduces the number of layers that can fill their pants at once.