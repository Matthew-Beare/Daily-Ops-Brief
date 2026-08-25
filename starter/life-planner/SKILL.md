---
name: life-planner
description: Run and maintain a provider-backed personal planning system using canonical structured state, retained evidence, mail, calendars, versioned policy, and scheduled or manual briefs. Use for Life Planner onboarding; personal Google setup; tasks, routines, appointments, meal planning, receipts, orders, shopping, assets, manuals, job watch, work/travel tracking, daily briefs, recovery, and durable feature changes.
---

# Life Planner

Keep changing personal facts in the selected canonical provider, durable behaviour and schemas in the deployment repository, and retained files in the selected evidence store. Never substitute chat memory for an unavailable authority or claim a provider write before readback.

## Route the request

- Personal Google onboarding or recovery: read `references/personal-google-onboarding.md`, use `assets/personal-google-blueprint.json`, and run `scripts/google_bootstrap.py` to plan and verify the provider transaction.
- Manual or scheduled brief/control cycle: read `references/control-cycle.md`.
- Tasks, routines, household work, study, meal planning, profiles, goals, or next actions: read `references/planning.md`.
- Orders, receipts, payments, shopping, inventory, assets, identifiers, manuals, or specifications: read `references/commerce-assets.md`.
- Appointments, Calendar projection, medication reminders, or caregiver delivery: read `references/appointments-health.md`.

## Core transaction

1. Resolve the deployment repository and selected Authority Registry.
2. Read only the authorities required by the requested module.
3. Correlate and deduplicate using stable provider IDs and immutable UUIDs.
4. Write the smallest canonical mutation.
5. Read it back and verify material fields before reporting success.
6. Reconcile optional projections independently; never roll back canonical state because an unrelated projection failed.
7. Record provider/resource health in the Integration Registry.

## Boundaries

- Use exactly one canonical authority per mutable data class. Calendar and email are evidence/projection surfaces unless explicitly selected otherwise.
- Keep credentials, message bodies, receipts, medical records, financial records, mutable exports, and live provider IDs out of portable Git source.
- Never send email automatically. Show the recipient, subject, and complete draft, then ask `Do you want me to send this email?`.
- Never infer medication dose/timing, health status, sharing permission, relationship authority, completion, or a context mode from weak evidence.
- Use one consolidated dispatcher for a chosen cadence. Event-specific reminders belong on one linked Calendar event, not separate automations.
- At scheduled entry, capture the runtime clock, convert it through the deployment's IANA timezone, and verify the configured local slot. Device/travel timezone never silently replaces it.
- A missing required authority blocks only its module. A missing optional adapter degrades only that path.
- After two unchanged failures, an ambiguous write, a permission failure, or contradictory readback, stop that module, preserve known-good state, and report one exact next action.
- Validate, commit, push, remotely read back, and require green CI for lasting policy/schema/test/onboarding changes when standing source-write permission exists. Routine personal state never creates a Git commit.

## Completion standard

Call setup or a mutation complete only when exact account/resource identity, bounded write, provider readback, and source readback are proven. Green CI proves source integrity; it does not prove a live Google write, scheduler notification, or observed firing.
