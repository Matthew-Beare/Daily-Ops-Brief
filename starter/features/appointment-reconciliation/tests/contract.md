# Appointment Reconciliation Acceptance Contract

A compliant deployment must prove:

1. appointment automation is opt-in by event/evidence class;
2. complete relevant evidence is read before mutation;
3. one canonical appointment/source identity maps to at most one active linked Calendar event;
4. create/update is followed by Calendar readback verifying event ID, title, time/timezone, reminders, target calendar and source linkage;
5. canonical projection state is also verified before the source is marked reconciled;
6. revisions/cancellations update the same event;
7. ambiguity asks instead of guessing;
8. Calendar handles appointment-specific reminders instead of per-appointment Scheduled Tasks;
9. sensitive appointments use minimum necessary detail and do not create medical inferences;
10. email, Calendar and canonical-state adapter failures remain module-scoped.