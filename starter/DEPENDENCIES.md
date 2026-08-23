# LyfeOS First-Boot Dependencies

First boot verifies every selected dependency before claiming a module is installed. Missing access blocks only the dependent module. Never ask a non-technical user for passwords, access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Git repository — required durable source

LyfeOS stores durable policy, schemas, tests, migrations, onboarding, and recovery material in Git. Mutable personal records remain in the selected live authorities such as Sheets/Drive/database services.

A deployment repository may be **public or private by explicit user choice**. Public deployment source is allowed only when the user understands that its entire reachable Git history is public and the public-source audit passes. Never commit secrets, credentials, mutable operational exports, Gmail bodies, receipts, financial account data, school submissions, or other information the user did not deliberately choose to publish.

### ChatGPT side

1. Open ChatGPT **Settings → Apps / Plugins** and connect GitHub.
2. Return to ChatGPT and verify the intended repository with a harmless repository/file read.
3. **Separately verify write capability.** Read access is not evidence that ChatGPT can create branches or edit files.
4. Read provider repository metadata and record whether the repository is public or private. Do not infer visibility from documentation.
5. If durable automatic versioning is selected, perform one bounded branch/file write after initial provisioning approval and verify remote readback before enabling scheduled LyfeOS writes.

If a write-capable GitHub experience is unavailable, report that exact dependency and continue only modules that do not depend on durable source mutation.

### GitHub side

1. Fork/clone the public LyfeOS source or create/select another repository owned by the user.
2. In GitHub account settings open **Applications / Installed GitHub Apps** and locate the app authorized by the ChatGPT/OpenAI flow.
3. Configure repository access so the deployment repository is included; prefer **Only select repositories** unless broader access is deliberate.
4. Review repository permissions and grant only what selected workflows require.
5. Return to ChatGPT and repeat read verification plus bounded write/readback when approved.

A new deployment must not reuse another user's Google authority IDs, schedules, aliases, mutable records, or deployment configuration merely because the source repository was forked. The `starter/` boundary is portable; current-deployment files elsewhere in the repository are examples/reference for that deployment, not new-user state.

## Public-source gate

Before a public release, public fork handoff, or public deployment-source push:

1. run `python3 scripts/audit_public_source.py .` when that tool exists in the source tree;
2. run `python3 scripts/audit_starter_privacy.py starter`;
3. run repository validation and all tests;
4. verify `.env`, local configuration, credentials, mutable exports, receipt/mail bodies, and account data are absent;
5. verify generated starter/deployment source contains only information the user intentionally allows in Git.

Public visibility is not itself a failure. **Unintended data exposure is.**

## Google Drive / Docs / Sheets

Current Google Docs/Sheets workflows use the Google Drive integration.

### ChatGPT side

1. Open ChatGPT **Settings → Apps / Plugins**.
2. Connect Google Drive and approve the intended account.
3. Verify a harmless Drive listing/search.
4. After provisioning approval, verify creation/readback of the selected starter folder and native Sheet/Doc when required.

Read-only access is insufficient for automatic data-plane provisioning.

## Gmail

Required only for selected email-driven modules such as receipts/orders/mail triage or school/admin evidence. Verify a harmless bounded read first. Label/archive writes are separately verified when selected. Sending remains approval-gated.

## Google Calendar

Required only for calendar reads or selected Calendar Projection classes. Verify calendar read access first. After projection choices and provisioning approval, verify a bounded create/update/delete or the first real projection. Adding attendees/invites is a separate action boundary.

## Scheduled Tasks and timezone integrity

Scheduled Tasks are optional unless the user wants recurring briefs, digests, accountability check-ins, or condition watches.

Treat scheduling as an evidence chain:

1. **Schedule definition:** VEVENT/RRULE uses the canonical IANA timezone and requested local time.
2. **Dispatcher state:** exactly the intended job is enabled with the correct timing mode and no active duplicates.
3. **Notification state:** expected push/email delivery is enabled.
4. **Observed execution:** after setup or repair, an actual firing or canonical Run Log lands in the intended local slot.

A connector field called `default_timezone` is not automatically proof of stored execution timezone. Treat such metadata as authoritative only when the **provider contract** explicitly defines it as persistent task execution state.

Provisioning rules:
- Show sample output and exact intended schedule before the first task write.
- Snapshot existing tasks before consolidation/replacement.
- Prefer editing an existing notification-capable dispatcher over replacing it.
- After every create/update, verify title, enabled state, cadence, local time, TZID, timing mode, required notification state, and duplicate count.
- If replacement is unavoidable, prove the replacement can notify before disabling the known-good dispatcher.
- Require the next actual firing/Run Log before declaring a scheduler incident cleared.
- If the slot is missed despite healthy readback, fail scheduler maintenance closed and issue the Pants Filling With Shit Report. Do not create hidden hourly retries, AM/PM child jobs, per-order jobs, or travel-timezone compensation schedules.

Scheduled Tasks are server-side and are intended to execute whether or not ChatGPT is open. Merely leaving ChatGPT Work or changing HOME/ROAD mode is not a scheduling-state change. Task/chat deletion, platform pauses, notification settings, usage limits, or scheduler/runtime faults are separate conditions to diagnose.

## Financial accounts

Optional for account-level charge/refund/cash-flow reconciliation and separate from receipt-detected spending. Use the product's account-linking flow; never request banking credentials in chat. Inspect coverage/freshness before treating missing transactions as proof of no charge/refund.

## Local/private devices

A NAS, home server, phone-local store, or LAN-only service requires an explicit supported bridge. Never imply cloud ChatGPT can silently reach an unconnected private network.

## Dependency gate output

Before provisioning, summarize each selected dependency as: required module(s); read verified / write verified / missing / partial; exact next action; and whether unrelated onboarding can continue. Do not enable scheduled writes until authorities and schedule/notification checks are verified; do not call scheduler repair complete until the next real firing proves it.