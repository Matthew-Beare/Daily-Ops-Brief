# Appointment Reconciliation

## Purpose

Turn user-approved classes of appointment/reservation evidence into a single verified canonical appointment and linked Calendar event, then reconcile later revisions/cancellations without duplicates.

## Enablement

This module is opt-in by appointment class. First boot captures:
- evidence sources/senders/domains that are eligible;
- target calendar;
- timezone and reminder defaults;
- tentative-date handling;
- revision/cancellation policy;
- confidence threshold and ambiguity behavior;
- minimum-detail policy for sensitive appointment classes;
- whether invitations/attendees are prohibited or separately approval-gated.

## Reconciliation transaction

For each candidate:
1. read complete relevant evidence;
2. correlate/dedupe against canonical appointment/source identity and existing projection;
3. extract only evidence-backed event fields;
4. if confidence is below the configured threshold or evidence conflicts, ask rather than write;
5. create or update the linked Calendar event;
6. read the event back and verify event ID, target calendar, title, date/time/timezone, reminder policy and source linkage;
7. write/verify canonical appointment + Calendar Projection state;
8. only after both sides agree mark the evidence reconciled.

Later revision/cancellation evidence updates/cancels the same linked event. Never create a duplicate merely because a new email arrived.

## Reminders and scheduler isolation

Calendar owns appointment-specific reminders. ChatGPT may surface upcoming appointments through a consolidated brief/accountability dispatcher. Do not create one Scheduled Task per appointment.

## Failure contract

If Calendar write/readback or canonical-state write fails, preserve the source as unresolved and surface the exact blocked operation. An ambiguous partial write receives readback before any corrected retry. Failure of email ingestion does not prevent manual/canonical appointment entry; failure of Calendar does not corrupt the appointment source record.

## Sensitive appointments

Medical or other sensitive appointments may be organized when the user selects them. Default to the minimum calendar detail necessary for the user's reminder workflow. Never infer diagnosis, treatment, prognosis or other medical facts from scheduling evidence.

## Minimal dependencies

Manual appointment tracking can function with the canonical state authority alone. Email ingestion and Calendar projection are optional adapters. Each adapter fails independently.

## Portability

Portable source contains rules/config/tests only. Real emails, appointments, provider names, medical details, event IDs and calendar history remain deployment runtime data.