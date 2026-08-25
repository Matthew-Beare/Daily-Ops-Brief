# Personal Google onboarding

Use this browser-only lane for personal, non-regulated data. Never send a non-technical user to a terminal.

## Required capabilities

- one private user-controlled repository made from the public Life Planner template;
- verified repository read, write, remote readback, and green CI;
- one exact Google identity for Drive and the structured-state workbooks;
- Gmail only when selected email evidence requires it;
- Google Calendar only when selected projections/reminders require it;
- a notification-capable scheduler only when recurring delivery is selected.

Connection badges are not evidence. Read back the authenticated profile for GitHub, Drive, Gmail, and Calendar separately.

## Bootstrap transaction

1. Verify the public template repository and exact upstream commit.
2. Verify the user's private repository owner, visibility, default branch, head commit, read access, and write access.
3. Collect the four kickoff answers, canonical IANA timezone, enabled modules, and Google identity.
4. Create a deployment UUID and owner UUID. Keep the resulting plan out of portable Git because it contains personal provider references.
5. Run `google_bootstrap.py plan` with the bundled blueprint and question bank.
6. Create the planned native Google workbooks and tabs. Preserve header order exactly, set each native spreadsheet's timezone property to the canonical IANA timezone, and read that property back.
7. Create the planned Drive root/folders and move or link evidence resources there when the provider permits it.
8. Populate `Metadata`, `Authority Registry`, `Interview Ledger`, `Integration Registry`, `People`, and `Services` from the plan.
9. If Gmail is enabled, prove a bounded read without changing mail.
10. If Calendar is enabled, create one clearly synthetic setup event, read it back, record its provider ID, then remove or retain it according to the user's test-record policy.
11. Build an observed readback document from provider responses and run `google_bootstrap.py verify --strict`. Use unformatted cell values for readback; the verifier compares offset-aware ISO and Excel/Sheets serial timestamps as instants while keeping all other seed fields strict.
12. Generate the deployment's non-secret policy/config/schema files, validate, commit, push, read back the remote commit, and require green CI.
13. If recurring delivery is enabled, create the fewest required dispatchers and do not claim scheduling healthy until one real firing and Run Log record are observed.

## Ready means

The bootstrap verifier returns `ready`, source CI is green, and every selected live provider action has exact readback. A deployment awaiting its first scheduled firing is `degraded`, not failed and not fully proven.
