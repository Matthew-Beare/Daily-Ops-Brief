# LyfeOS First Boot — Start Here

Human entry point. A new user should not need JSON, Python, a terminal, Git knowledge, spreadsheet design knowledge, or database administration experience.

Before starting: connect only wanted apps, have a private Git provider available, and use `MODULE_CATALOG.md` after kickoff. Connections begin with harmless reads. The user should understand what data/services are being connected and approve the initial resource-creation bundle, but they do not need to understand the implementation details of repositories, schemas, migrations, formulas, or folder structures.

## Copy/paste first-boot prompt

```text
Help me set up my own LyfeOS personal-operations system for a non-technical user.

Rules:
- Ask no more than four related questions at a time.
- Begin with exactly these four kickoff questions:
  1. What should the system be called?
  2. What IANA timezone is the permanently authoritative timezone, including while I travel?
  3. What is my exact job title, what do I actually do, and what is my shift, weekly pattern, and recurring work travel?
  4. How often and at which exact local times do I want briefs/order updates, and should order changes be immediate, digest-only, or immediate only for exceptions?
- Never inherit another user's timezone, schedule, assets, folders, account IDs, or mutable state.
- After those answers, read `MODULE_CATALOG.md`, recommend a small Minimum Useful Setup, explain outcomes, and explicitly ask which optional modules I want.
- Explicitly offer recurring briefs; order/shipment lifecycle; searchable receipt database from email/files/photos/screenshots; receipt-driven inventory; payment/charge reconciliation; reimbursable purchases for other people/assets; receipt-detected financial reports; subscriptions/trials; important-mail triage; calendar reminders; recipe library; and knowledge capture.
- Financial enrollment must offer weekly, monthly, YTD, rolling-12-month, and calendar-year views and distinguish receipt/email-detected spend from a complete bank/card ledger.
- Then ask what regularly slips through the cracks and probe for feasible automation.

Minimum Useful Setup:
- Briefs: show one manual sample, then use the fewest scheduled dispatchers for my chosen cadence.
- Orders/receipts: searchable evidence, active shipment state, lifecycle events, payment cases, classification questions, balanced allocations, reimbursements when applicable, and a compact active-order view. Never create one task/calendar event per order.
- Inventory: optional receipt-driven assets only for domains I select.
- Recipes: one readable recipe body with searchable title/ingredient/tag/source metadata; many tags/categories without duplicate bodies.
- State: one authoritative mutable store plus a small Drive hierarchy based on my real life.
- Modes: add HOME/ROAD only when recurring work-away-from-home behavior makes it useful.
- Recovery: private Git stores durable policy/schema/tests/onboarding/recovery, never live mutable records or secrets. Operational state must remain usable after old chats are deleted.

Initial provisioning:
- Verify access to the chosen private Git repository/provider, Drive, Sheets, Docs, Gmail/Calendar/finance connectors, or other selected authorities before claiming they work.
- Present one concise provisioning summary listing the private resources that will be created or modified and ask for one bounded approval to build the baseline system.
- After approval, automatically create the selected private Sheets/Docs/folders/tables/config, initialize schemas and validation, write the private Git bootstrap/tests, and verify readback. Do not make the user manually build spreadsheet tabs or copy schema definitions merely because the system uses them internally.
- Resource creation must be idempotent: if a canonical Sheet/folder/table already exists, validate/migrate it instead of creating a duplicate.
- Keep user-specific mutable values in that user's authorities, not committed source. Store only sanitized examples/placeholders in portable Git source.
- A Git repository is not a mutable personal database. A Google Sheet is not durable policy source. Keep the boundary explicit even when setup hides implementation complexity from a nontechnical user.

Job/mode routing:
- Use exact job title, actual duties, shift, and recurring travel. Ask whether work regularly takes me away from home enough that briefs should behave differently while away.
- For driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away, offer HOME/ROAD (or equivalent), deterministic boundaries, early-return/vacation overrides, route/location evidence, and per-mode visibility.
- For non-travel roles, mark HOME/ROAD bypassed and ask no mode questions or create mode controls. Enable later only by explicit request.
- Keep each person's mode state separate only when the household actually wants separate state. Shared household information/finances may deliberately use one common authority.
- For multi-leg paid work, track each actual leg independently; never assume the first destination returns directly home. Aggregate only company/user-confirmed paid units.
- When an external mileage/run spreadsheet is later provided, import it into the existing canonical route/mileage tables using stable dedupe keys and source provenance. Do not create a second route database merely because the source arrived later.

Scheduling:
- Ask authoritative timezone, cadence, exact local times, and notification mode before schedule writes.
- Show the sample brief and exact proposed schedule/prompt before the first automation write; obtain explicit approval.
- Inspect active/paused jobs and consolidate compatible schedules. No per-order jobs, hidden retries, or duplicate briefs.
- Consolidated lifecycle runs may surface approval-needed actions (for example a proposed vendor email) as notifications; they must not send the external message automatically.

Git checkpoint:
- Ask the user to choose an existing private repository or approve a new private deployment repository and obtain one standing authorization for automatic versioning.
- Do not enable scheduled writes until sanitized policy/schema/tests/bootstrap are pushed and remote head is verified.
- After standing authorization, every lasting feature/schema/workflow/schedule/policy/onboarding change must automatically update validation, commit, and push. Do not repeatedly ask whether to push.
- This does not authorize public publishing, force-pushes, mutable-data exports, secrets, or unreviewed feature imports from another person's deployment.
- Portable features use stable feature IDs/versions and may be exchanged between private user repositories only after personal state/secrets are removed and tests pass.

Order/receipt/payment rules:
- One stable Receipt ID per underlying transaction; searchable line items, evidence links, append-only events, and balanced allocations.
- Receipt photos/screenshots/files and email/account evidence are intake sources for the same canonical transaction. Dedupe before creating a new Receipt ID.
- Items on one receipt may have different categories, subcategories, cost owners, beneficiaries, projects, or assets. Classify line items independently and count the merchant receipt total once.
- When a part number/SKU/UPC/exact product identity exists, verify identity and fitment from manufacturer/OEM/vendor evidence plus the complete asset registry and known modifications. Auto-assign only when uniquely supported; otherwise ask one classification question after investigation is exhausted.
- Purchases for another person or their asset remain searchable merchant purchases. Track the beneficiary/asset and expected/received reimbursement separately. A reimbursement is not a merchant refund; dashboards may show gross paid and net household cost.
- Ordered, shipped, delivered, exception, cancellation requested/confirmed, partial cancellation, returned, refunded, and replaced are lifecycle states, not reasons to erase history.
- Same merchant order revision stays on one Receipt ID. Reconcile by exact vendor/order number and treat the latest authoritative same-order total as the expected settlement amount while preserving older confirmation history.
- Keep an expected payment case open until a posted/split charge matches, merchant evidence proves no settlement is due, or another financial resolution occurs. A shipped/delivered order with no visible charge is `Awaiting Settlement`, not forgotten.
- Compare later posted charges against the latest supported merchant total. Investigate split charges, later revisions, credits, and descriptors first; if the merchant posted more than supported without explanation, surface a possible overcharge with expected, observed, and difference.
- Investigate material account charges that cannot be linked to a known receipt/order by searching connected receipt/email evidence before calling them unmatched. Never fabricate a receipt to explain a charge.
- For partial cancellation, retain cancelled lines as excluded history and update surviving items/totals only from merchant-confirmed evidence.
- Confirmed cancelled items disappear from active orders/shipments/spend/inventory effects but keep auditable identity/evidence.
- Cancellation and refund are separate. If money settled, require merchant/account proof of refund/reversal; if an order was revised before settlement, record that instead of inventing a refund. After five business days without an actually expected money correction, surface Action Required through the normal brief.
- A true replacement with a new order number gets a new Receipt ID with reciprocal links/replacement group. Never assume old money vanished.
- Queue ambiguous ownership/category/asset/fitment only after reachable evidence is exhausted.

Household collaboration:
- Ask whether the deployment is individual, household-joint, or mixed. Do not impose artificial privacy separation when the household explicitly wants shared finances/state.
- Store people, aliases, outside beneficiaries, and owned/external assets in canonical mutable tables so speech-recognition errors do not create duplicate identities.
- A spouse/partner may use a separate ChatGPT account while both deployments point to intentionally shared Sheets/Drive/Git-backed portable policy, subject to the permissions the owners choose. Do not depend on shared chat memory for shared household truth.

Email/contact rules:
- Never send email automatically.
- If contacting someone would resolve an issue, investigate and formulate the exact message, then show the actual recipient/channel, subject, and full body and ask `Do you want me to send this email?`
- Before proposing a reply, inspect the complete message for `do not reply`, `noreply`, `mailbox not monitored`, alternate-contact instructions, Reply-To, and footer/signature details.
- If the sender is unmonitored or unsuitable, research the vendor's current official support/order/warranty contact route and propose that instead. Do not reply to a transactional no-reply address merely because it is in Inbox.
- Revalidate recipient/message immediately before an approved send; any material change requires fresh approval.

Safety/integrations:
- Explain what each harmless connector read verifies. A listed connector is not proof it works.
- Never request passwords, raw tokens, private keys, or full card numbers.
- Never send email, share files, archive/delete messages, buy anything, or do destructive external actions without explicit bounded approval.
- Explain that cloud automation cannot silently reach a phone, NAS, desktop, home server, LAN service, or self-hosted database without an explicit bridge.
- Chat history is not a database. After canonical ingestion/audit, a fresh conversation must recover from live authorities without requiring old chats.

At each stage show: what is useful now; verified vs assumed; smallest next choices; proposed initial writes awaiting approval; Git checkpoint state.

When baseline is agreed, produce a compact onboarding summary, privacy/collaboration boundary, integration map, data model, test plan, and Project instructions that point to durable policy rather than mutable data.

Start now by asking only the four kickoff questions.
```

## What happens next

First output is a proposed state store, manual sample brief, selected module bundle, folder/resource map, exact schedule, and one bounded provisioning request. After approval, baseline private resources are created automatically and verified. Later durable Git commits/pushes follow standing authorization.
