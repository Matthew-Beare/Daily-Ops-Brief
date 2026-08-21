# Generic First-Boot Starter

This reusable onboarding kit builds a new user's LyfeOS without copying the current user's data, schedules, accounts, assets, or rules. The human entry point is [`START_HERE.md`](START_HERE.md); JSON, templates, scripts, tests, and Git stay behind the interface.

## Stock product

Every first boot provisions three stock behaviours, configured to the user's named timezone and chosen cadence:

1. concise manual and scheduled briefs;
2. one consolidated order/receipt lifecycle with shipment, delivery, exception, cancellation, replacement, return, and refund handling;
3. a searchable, collapsible recipe library with a filterable title/ingredient/tag index;
4. a conditional per-user HOME/ROAD layer for driving/travel/overnight roles, bypassed for non-travel work.

These modules are stock; their accounts, exact times, notification mode, taxonomy, and retention rules are not assumed.

## First-boot workflow

1. Ask only the four kickoff questions in `START_HERE.md`: name, authoritative timezone, exact job title/duties/shift/travel pattern, and exact brief/order cadence plus notification mode.
2. Produce a Minimum Useful Setup and manual sample before optional discovery.
3. Ask no more than four related follow-ups at a time from `questions.json`.
4. Explain harmless connector reads, then verify connected email, calendar, Drive, Sheets, GitHub, and existing automations.
5. Select or create a private repository and obtain one standing authorization for automatic durable versioning.
6. Commit and push the sanitized initial policy, schema, tests, bootstrap, and recovery material; verify the remote head before enabling scheduled writes.
7. Agree on one mutable-state authority and the smallest useful Drive hierarchy.
8. Inspect active/paused tasks, show exact schedules/prompts, and obtain explicit approval for the initial automation mutations.
9. Create/adapt policy and tests; keep scheduled prompts as tiny dispatchers.
10. After standing Git authorization, automatically validate, commit, push, and remotely verify every lasting feature/schema/workflow/schedule/policy/onboarding change. Do not ask again whether to push.

## Boundaries

- Never inherit another user's timezone, schedule, or mode state. Household members get separate controls even when evidence is shared.
- Never create one automation per order. Consolidate checks and notifications at the chosen cadence.
- Same-order revisions remain one transaction; true replacements use two linked Receipt IDs and never erase the original.
- One recipe body may have many categories/tags; preserve searchable text and provenance instead of duplicating it.
- Never request or commit passwords, tokens, keys, full card data, Gmail bodies, receipts, or mutable exports.
- Automatic Git push does not authorize auto-merge, public publishing, releases, or force-pushes.
- A cloud task cannot reach an unconnected private device or LAN service without an explicit bridge.
- User-facing Drive navigation must use readable native surfaces, not raw HTML/JSON/Markdown cards.

## Developer/recovery layer

A developer may copy `config.example.json` to untracked `config.local.json` and render `INSTRUCTIONS.md.tmpl` with `scripts/bootstrap.py`. Durable facts belong in policy/schema/tests; mutable facts stay in the authoritative state store.
