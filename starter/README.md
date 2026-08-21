# Generic First-Boot Starter

This directory is a reusable onboarding kit. It is not a copy of the current user's live setup.

## Goal

Build a small, auditable personal-ops system from a structured interview and live capability audit. The result should use one authoritative mutable state store, minimal scheduled dispatchers, explicit privacy boundaries, and a private version-controlled recovery path.

## First-boot workflow

1. Load `questions.json` and skip anything already answered reliably.
2. Ask questions in short topical groups. Required unknowns come first; do not force the user through every optional question in one sitting.
3. Inspect connected email, calendar, Drive, Sheets, and GitHub with harmless reads. A listed connector is not proof that authorization works.
4. Privately inspect existing scheduled tasks before creating or rebuilding one. Prefer an in-place update or consolidation over duplicates.
5. Agree on the single mutable state authority and the smallest useful Drive hierarchy.
6. Fill `config.example.json` into an untracked `config.local.json`.
7. Render `INSTRUCTIONS.md.tmpl` with `scripts/bootstrap.py`.
8. Create or adapt a policy skill; keep scheduled prompts as tiny dispatchers.
9. Validate the repository and test deterministic policy code before publishing.
10. Create or change scheduled tasks only after every required dependency read succeeds.

## Integration caveats

- A cloud task cannot silently reach a private phone, NAS, home server, desktop, LAN, or local database. That requires an explicit bridge or sync design.
- Never request passwords or raw access tokens in chat. Use connected apps or a secret manager appropriate to the integration.
- A connector can be installed but disconnected. Test with harmless reads.
- Scheduled execution may not be instantaneous. Design briefs to tolerate modest delivery delay and to use the actual run time.
- Repository changes do not silently replace a ChatGPT Project's instruction field. Provide the complete replacement when no direct write tool exists.

## Improve without prompt bloat

- Put mutable facts in the live state store.
- Put durable policy in the skill and tests.
- Put setup/recovery instructions in the private repository.
- Record lessons as schema or policy changes, not paragraphs pasted into an automation prompt.
- Review duplicates, failed dependencies, stale overrides, and noisy output periodically.
