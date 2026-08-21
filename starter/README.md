# Generic First-Boot Starter

This directory is a reusable onboarding kit. It is not a copy of the current user's live setup.

The human entry point is [`START_HERE.md`](START_HERE.md). A new user pastes its first-boot prompt into ChatGPT and completes setup conversationally. JSON, templates, scripts, and Git are the developer/recovery layer, not the onboarding interface.

## Goal

Build a small, auditable personal-ops system from a structured interview and live capability audit. The result should use one authoritative mutable state store, minimal scheduled dispatchers, explicit privacy boundaries, and a private version-controlled recovery path.

## First-boot workflow

1. Start with `START_HERE.md`; ask only its four kickoff questions.
2. Produce a Minimum Useful Setup before optional deep discovery.
3. Load `questions.json` only as a staged follow-up and skip anything already answered reliably.
4. Ask no more than four related questions at a time; do not force every optional question into one sitting.
5. Explain each integration read before using it, then inspect connected email, calendar, Drive, Sheets, and GitHub harmlessly. A listed connector is not proof that authorization works.
6. Privately inspect existing scheduled tasks before proposing a new or rebuilt one. Prefer an in-place update or consolidation over duplicates and require approval before mutation.
7. Agree on the single mutable state authority and the smallest useful Drive hierarchy.
8. Keep configuration behind the scenes. A developer may fill `config.example.json` into an untracked `config.local.json` and render `INSTRUCTIONS.md.tmpl` with `scripts/bootstrap.py`.
9. Create or adapt a policy skill; keep scheduled prompts as tiny dispatchers.
10. Validate deterministic policy and recovery material before publishing or enabling scheduled writes.

## Integration caveats

- A cloud task cannot silently reach a private phone, NAS, home server, desktop, LAN, or local database. That requires an explicit bridge or sync design.
- Never request passwords or raw access tokens in chat. Use connected apps or a secret manager appropriate to the integration.
- A connector can be installed but disconnected. Test with harmless reads.
- Scheduled execution may not be instantaneous. Design briefs to tolerate modest delivery delay and to use the actual run time.
- Repository changes do not silently replace a ChatGPT Project's instruction field. Provide the complete replacement when no direct write tool exists.
- Never expose raw HTML, JSON, Markdown, or source-code link cards as the active Drive interface. Use native Workspace documents, Sheets views, or supported shortcuts for user-facing navigation.

## Improve without prompt bloat

- Put mutable facts in the live state store.
- Put durable policy in the skill and tests.
- Put setup/recovery instructions in the private repository.
- Record lessons as schema or policy changes, not paragraphs pasted into an automation prompt.
- Review duplicates, failed dependencies, stale overrides, and noisy output periodically.
