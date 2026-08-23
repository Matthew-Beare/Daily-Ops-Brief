# LyfeOS First-Boot Dependencies

First boot must verify every selected dependency before claiming a module is installed. Missing access blocks only the dependent module; explain the exact setup and continue with modules whose authorities work.

Never ask a non-technical user for passwords, personal access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Private Git repository — required for durable LifeOS deployments

LifeOS durable policy, schemas, tests, migrations, onboarding and recovery material require a private Git repository. Mutable personal records do not go in Git.

### ChatGPT side

1. Open ChatGPT **Settings → Apps / Plugins** and find GitHub.
2. Choose Connect/Configure and complete the GitHub authorization flow.
3. Return to ChatGPT and verify the intended private repository with a harmless repository/file read.
4. **Separately verify write capability.** The standard GitHub app may provide repository read/search only depending on plan and ChatGPT experience. A successful read is not evidence that ChatGPT can create branches, edit files or push commits.
5. If durable automatic versioning is selected, use an available write-capable GitHub workflow such as Codex or an installed GitHub plugin/app exposing bounded write actions. After the user's initial provisioning approval, perform a harmless branch/file write and verify remote readback before enabling scheduled LifeOS writes.

If GitHub or a write-capable GitHub experience is unavailable on the user's current plan/surface, state that exact dependency and do not pretend the durable deployment is fully provisioned.

### GitHub side

GitHub controls which repositories the installed app can access.

1. Create or choose the user's **private** deployment repository. When a stable `Life-Ops-Starter` release exists, derive/fork from that sanitized release rather than another person's production repo.
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

Required for email-driven receipts/orders/mail triage. Connect Gmail, verify a harmless bounded read, then verify label/archive writes only when selected. Sending remains separately approval-gated.

## Google Calendar

Required only for calendar reads or selected Calendar Projection classes. Verify calendar read access first. After projection classes and initial provisioning are approved, verify a bounded event create/update/delete or the first real projection. Adding attendees/invites is a separate action boundary.

## Financial accounts

Optional for account-level charge/refund/net-worth reconciliation and separate from receipt-detected spending. Use the product's account-linking flow; never request banking credentials in chat. Inspect coverage/freshness before treating missing transactions as evidence of no charge/refund.

## Dependency gate output

Before provisioning, show each dependency as: required module(s); read verified / write verified / missing / partial; exact next action; whether unrelated onboarding can continue.

Do not enable scheduled writes for a module until its authorities and private-Git recovery path are verified.
