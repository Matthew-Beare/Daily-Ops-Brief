# LyfeOS First-Boot Dependencies

First boot must verify every selected dependency before claiming a module is installed. Missing access blocks only the dependent module; explain the exact setup and continue with modules whose authorities work.

Never ask a non-technical user for passwords, personal access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Private Git repository — required for durable LyfeOS deployments

LyfeOS durable policy, schemas, tests, migrations, onboarding and recovery material require a private Git repository. Mutable personal records do not go in Git.

### ChatGPT side

1. Open ChatGPT **Settings → Apps / Plugins** and find GitHub.
2. Choose Connect/Configure and complete the GitHub authorization flow.
3. Return to ChatGPT and verify the intended private repository with a harmless repository/file read.
4. **Separately verify write capability.** A successful read is not evidence that ChatGPT can create branches, edit files or push commits.
5. If durable automatic versioning is selected, use an available write-capable GitHub workflow. After initial provisioning approval, perform a harmless branch/file write and verify remote readback before enabling scheduled LyfeOS writes.

If GitHub or a write-capable GitHub experience is unavailable on the current plan/surface, state that exact dependency and do not pretend the durable deployment is fully provisioned.

### GitHub side

GitHub controls which repositories the installed app can access.

1. Create or choose the user's **private** deployment repository. When a stable sanitized starter release exists, derive/fork from that release rather than another person's production repo.
2. In GitHub account settings open **Applications / Installed GitHub Apps** and locate the app authorized by the ChatGPT/OpenAI flow.
3. Configure repository access so the private deployment repo is included; prefer **Only select repositories** unless broader access is deliberate.
4. Review the app's repository permissions. Grant only permissions required by the selected read/write workflow.
5. Return to ChatGPT and repeat read verification and, when supported/approved, bounded write verification.

If the available ChatGPT GitHub action cannot create a repository, give the exact GitHub UI create/fork step and resume when the repo becomes visible. Setup is not complete until remote readback succeeds.

## Google Drive / Docs / Sheets — normal starter data plane

Current Google Docs/Sheets/Slides workflows use the Google Drive integration.

### ChatGPT side

1. Open ChatGPT **Settings → Apps / Plugins**.
2. Connect Google Drive and approve the intended Google account.
3. Verify a harmless Drive listing/search.
4. After provisioning approval, verify creation/readback of the selected starter folder plus a small native Sheet/Doc when required.

### Google side

Complete Google's OAuth consent flow for the intended account and required scopes. Read-only access is insufficient for automatic database/folder provisioning.

## Gmail

Required for email-driven receipts/orders/mail triage and optional school/admin evidence. Connect Gmail, verify a harmless bounded read, then verify label/archive writes only when selected. Sending remains separately approval-gated.

## Google Calendar

Required only for calendar reads or selected Calendar Projection classes. Verify calendar read access first. After projection classes and initial provisioning are approved, verify a bounded event create/update/delete or the first real projection. Adding attendees/invites is a separate action boundary.

## Scheduled Tasks and timezone integrity

Scheduled Tasks are optional unless the user wants recurring briefs, digests, accountability check-ins, or condition watches.

Treat timezone configuration as a two-part dependency:

1. **Schedule definition:** the visible schedule/VEVENT uses the user's canonical IANA timezone and requested local time.
2. **Provider execution timezone:** after create/update, read the task back and verify the scheduler's stored/default/execution timezone also equals that same canonical IANA timezone.

A task is **not** healthy merely because its RRULE contains the desired TZID. If the provider silently stamps the current travel/device timezone, current location has leaked into scheduling authority.

Provisioning rules:
- Show the sample output and exact intended schedule before the first task write.
- Snapshot existing tasks before consolidation or replacement.
- After every create/update, verify title, enabled state, cadence, local time, TZID, provider execution timezone, and duplicate count.
- If provider execution timezone differs from canonical timezone and the available task API/UI does not expose a reliable setter, fail closed for the scheduled module. Preserve the desired schedule in policy/state, keep unrelated manual workflows working, and give the user the exact Scheduled-page/platform correction required.
- Never compensate by inventing hidden hourly retry jobs, AM/PM child jobs, per-order jobs, or a travel-location-specific schedule that will break on the next trip.
- After a timezone repair, require readback showing the canonical execution timezone and verify the next actual firing/run-log timestamp before clearing the incident.

Being offline or outside a work context is not itself a reason for a server-side Scheduled Task to stop. Context modes affect content; they must not redefine the canonical scheduler timezone.

## Financial accounts

Optional for account-level charge/refund/net-worth reconciliation and separate from receipt-detected spending. Use the product's account-linking flow; never request banking credentials in chat. Inspect coverage/freshness before treating missing transactions as evidence of no charge/refund.

## Local/private devices

Optional workflows may use a NAS, home server, phone-local store or LAN-only service only when an explicit supported bridge exists. Never imply cloud ChatGPT can silently reach an unconnected private network. Ask what must remain local, what bridge is authorized, and what happens while the user is away.

## Dependency gate output

Before provisioning, show each dependency as: required module(s); read verified / write verified / missing / partial; exact next action; whether unrelated onboarding can continue.

Do not enable scheduled writes for a module until its authorities, scheduler-timezone integrity, and private-Git recovery path are verified.
