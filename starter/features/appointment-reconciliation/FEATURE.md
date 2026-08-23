# Appointment Reconciliation

## Purpose

Turn user-approved classes of appointment/reservation evidence into one verified canonical **private Git appointment** and optional linked Calendar event, then reconcile later revisions/cancellations without duplicates.

Manual appointment tracking works with private Git alone. Email and Calendar are optional adapters.

## Enablement

This module is opt-in by appointment class. First boot captures:
- whether appointment/reservation or medical-event scheduling help is wanted;
- evidence sources/senders/domains eligible when email is connected;
- target calendar when projection is enabled;
- timezone/reminder defaults;
- tentative-date handling;
- revision/cancellation policy;
- confidence threshold and ambiguity behavior;
- minimum-detail policy for sensitive appointment classes;
- whether invitations/attendees are prohibited or separately approval-gated.

## Reconciliation transaction

For each candidate:
1. read complete relevant evidence;
2. read current remote Git HEAD and dedupe against canonical Git appointment/source identity plus any existing projection;
3. extract only evidence-backed event fields;
4. if confidence is below threshold or evidence conflicts, ask rather than write;
5. create/update the linked Calendar event when Calendar is enabled;
6. read the Calendar event back and verify event ID, target calendar, title, date/time/timezone, reminder policy, and source linkage;
7. append/update the private Git appointment/reconciliation event + snapshot, including verified linked Calendar event ID/source references;
8. validate, commit, push fast-forward only, and read the Git state back;
9. only after the required provider projection and canonical Git state agree mark the evidence reconciled.

Later revision/cancellation evidence updates/cancels the same canonical Git appointment and linked Calendar event. Never create a duplicate merely because a new email arrived.

If Calendar is disabled, steps 5-6 are skipped and the canonical appointment remains fully usable from Git state.

## Reminders and scheduler isolation

Calendar owns appointment-specific reminders when enabled. ChatGPT may surface upcoming appointments through a consolidated brief/accountability dispatcher. Do not create one Scheduled Task per appointment.

Git remains the canonical appointment state even when Calendar supplies reminders.

## Failure contract

- If Calendar write/readback fails, preserve the Git/source candidate as unresolved and surface the exact blocked projection operation.
- If the canonical Git commit/push/readback fails, the appointment mutation is not complete even if Calendar changed; read back Calendar and Git before any corrected retry.
- If remote Git HEAD moved, re-read/reconcile instead of force-pushing.
- Email ingestion failure does not prevent manual Git appointment entry.
- Calendar failure does not corrupt the canonical Git appointment record.
- Each adapter fails independently.

## Sensitive appointments

Medical or other sensitive appointments may be organized only when the user selects them. Store the minimum detail needed for the chosen reminder/organization workflow. Never infer diagnosis, treatment, prognosis, or other medical facts from scheduling evidence.

The personal repository must be private before sensitive appointment state is written.

## Minimal dependencies

Private Git is the only required dependency. Email ingestion and Calendar projection are optional adapters. Basic appointment tracking remains usable without either.

## Portability

Portable source contains rules/config/tests only. Real emails, appointments, provider names, medical details, event IDs, source references, and calendar history live in private deployment `state/` or remain with the originating provider. They are excluded from upstream contributions.