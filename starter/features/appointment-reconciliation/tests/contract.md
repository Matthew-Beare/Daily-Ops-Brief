# Appointment Reconciliation Acceptance Contract

A compliant deployment must prove:

1. appointment automation is opt-in by event/evidence class;
2. manual appointment tracking works with private Git even when email/Calendar adapters are absent;
3. complete relevant evidence is read before mutation;
4. one canonical private Git appointment/source identity maps to at most one active linked Calendar event;
5. create/update is followed by Calendar readback verifying event ID, title, time/timezone, reminders, target calendar and source linkage;
6. the verified appointment/reconciliation event + snapshot and provider references are then validated, committed, pushed fast-forward only and read back from private Git;
7. the source is marked reconciled only after required Calendar projection and canonical Git state agree;
8. revisions/cancellations update the same Git appointment and linked Calendar event;
9. ambiguity asks instead of guessing;
10. Calendar handles appointment-specific reminders instead of per-appointment Scheduled Tasks;
11. sensitive appointments use minimum necessary detail and do not create medical inferences;
12. email and Calendar adapter failures remain module-scoped, while Git-state failure stops completion rather than falling back to chat/shadow state.