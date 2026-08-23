# LyfeOS First-Boot Dependencies

First boot must verify every selected dependency before claiming a module is installed. Missing access blocks only the dependent module; explain the exact setup and continue with modules whose authorities work.

Never ask a non-technical user for passwords, personal access tokens, OAuth secrets, private keys, or full payment-card numbers.

## Private Git repository — required for durable LifeOS deployments

LifeOS durable policy, schemas, tests, migrations, onboarding and recovery material require a private Git repository. Mutable personal records do not go in Git.

### ChatGPT side

1. Open ChatGPT **Settings** and open the current **Plugins / Apps** directory (wording can vary by client).
2. Find **GitHub** and choose Connect/Configure.
3. Complete the GitHub sign-in/authorization flow.
4. Return to ChatGPT and verify that the intended private deployment repository is actually visible with a harmless repository/file read.
5. If the selected workflow needs writes, verify a bounded branch/file write only after the user's initial provisioning approval. A successful read does not prove write permission.

GitHub availability varies by ChatGPT plan/surface. If GitHub is not exposed in the current standard chat experience, explain which available ChatGPT surface/plugin supports it rather than pretending the repository is connected.

### GitHub side

During/after the authorization flow, GitHub controls which repositories the installed GitHub App can access.

1. In GitHub, create or choose the user's **private** deployment repository. When a stable `Life-Ops-Starter` release exists, prefer a private fork/derived deployment from that release instead of another person's production repo.
2. In GitHub account settings, open **Applications / Installed GitHub Apps** and locate the GitHub App installed by the ChatGPT/OpenAI authorization flow.
3. Configure repository access so the intended private deployment repository is included. Prefer **Only select repositories** unless broader access is deliberately wanted.
4. Confirm required repository permissions shown by GitHub for the intended workflow. Do not broaden permissions merely to silence an error.
5. Return to ChatGPT and repeat the harmless read/write verification.

If the connected ChatGPT GitHub action cannot create repositories, give the exact GitHub UI creation/fork step and resume automatically after the new private repo becomes visible. Do not call setup complete before remote readback succeeds.

## Google Drive / Docs / Sheets — required for the normal starter data plane

Current Google Docs, Sheets and Slides actions are exposed through the Google Drive integration.

### ChatGPT side

1. Open ChatGPT **Settings → Plugins / Apps**.
2. Connect **Google Drive** and approve the selected Google account.
3. Verify a harmless Drive listing/search.
4. After initial provisioning approval, verify creation/readback of the starter folder plus a small native Sheet/Doc when those modules were selected.

### Google side

Complete Google's OAuth consent flow for the intended account. If Google presents requested scopes, review them and approve only the scopes required for the selected LifeOS modules. A Drive read-only connection is insufficient for automatic database/folder provisioning.

## Gmail

Required for email-driven receipts/orders/mail triage. Connect Gmail through the available ChatGPT plugin/app flow, verify a harmless profile/label or bounded search read, then verify labeling/archive actions only when those modules are selected. Sending remains separately approval-gated by policy.

## Google Calendar

Required only for calendar reading or selected Calendar Projection event classes. Verify calendar listing/read access before claiming appointment support. After the user selects projection classes and approves provisioning, verify one bounded create/update/delete test or the first real user-approved projection. Adding attendees/invites is a separate permission/action boundary.

## Financial accounts

Account-level charge/refund/net-worth reconciliation is optional and separate from receipt-detected spending. Use the product's account-linking flow; never request banking credentials in chat. After linking, inspect coverage/freshness before treating absent transactions as evidence that no charge/refund exists.

## Dependency gate output

Before first provisioning writes, show a concise table/state summary:

- dependency;
- required by selected module(s);
- Connected + read verified / write verified / missing / partial;
- exact next setup action when missing;
- whether the rest of onboarding can continue.

Do not enable scheduled writes for a module until its required authorities and private Git recovery path are verified.
