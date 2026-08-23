# LyfeOS First Boot — Start Here

Human entry point. A new user should not need JSON, Python, a terminal, Git, spreadsheet design, or database administration.

Before starting: connect only wanted apps and use a private Git repository. Begin with harmless reads. Explain permissions and external writes plainly; hide implementation complexity, not consent.

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
- After kickoff, read MODULE_CATALOG.md, recommend a small Minimum Useful Setup, and ask which optional modules I want.
- Offer briefs; order/shipment lifecycle; receipt intake from email/files/photos/screenshots; searchable receipts; payment/charge reconciliation; reimbursement tracking; receipt-driven inventory; finance views; subscriptions/trials; mail triage; calendar reminders; recipe library; and knowledge capture.
- Then ask what regularly slips through the cracks.

Minimum Useful Setup:
- Briefs: one manual sample, then the fewest dispatchers needed for the chosen cadence.
- Orders/receipts: searchable evidence, active shipment state, append-only events, balanced allocations, payment cases, reimbursements, and a compact active-order view. Never create one task/calendar event per order.
- Inventory: optional receipt-driven assets for selected domains.
- Recipes: one readable canonical recipe body plus searchable title/ingredient/tag/source metadata.
- State: one authoritative mutable store plus a small Drive hierarchy.
- Modes: enable HOME/ROAD only when recurring work-away behavior makes it useful.
- Recovery: private Git stores durable policy/schema/tests/onboarding/recovery, never live mutable records or secrets. Operational state must still work after old chats are deleted.

Initial provisioning:
- Verify access to the chosen private Git provider/repository and selected Drive, Sheets, Docs, Gmail, Calendar, finance, or other authorities before claiming they work.
- Present one concise provisioning summary and obtain explicit approval for the initial resource bundle.
- After approval, automatically create or validate selected Sheets/Docs/folders/tables/config, initialize schema/validation, write sanitized policy/tests/bootstrap to private Git, and verify readback.
- Provisioning must be idempotent: validate/migrate an existing canonical resource instead of creating a duplicate.
- Keep user-specific mutable values in live authorities. Commit only sanitized code/policy/schema/tests/examples.

Job/mode routing:
- Use exact job title, actual duties, shift, and recurring travel.
- For driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away, offer HOME/ROAD (or equivalent) with deterministic boundaries, overrides, and route/location evidence.
- For non-travel roles, mark HOME/ROAD bypassed and ask no mode questions or create mode controls unless requested later.
- For multi-leg paid work, track each actual leg independently and aggregate only company/user-confirmed paid units.
- If an employer run/mileage spreadsheet later arrives, import it into the existing route/trip/mileage database using stable directional dedupe keys and provenance. Do not create a second route database.

Scheduling:
- Ask authoritative timezone, cadence, exact local times, and notification mode before writes.
- Show the sample brief and exact proposed schedule/prompt before first automation creation; obtain explicit approval.
- Inspect active/paused tasks and consolidate compatible schedules. No per-order jobs or hidden retries.
- A consolidated lifecycle run may surface approval-needed actions such as a vendor-email proposal but must not send automatically.

Git checkpoint:
- Ask the user to select an existing private repository or approve a new private deployment repository and obtain one standing authorization for versioning.
- Do not enable scheduled writes until sanitized policy/schema/tests/bootstrap are pushed and remote head is verified.
- After standing authorization, every lasting feature/schema/workflow/schedule/policy/onboarding change must automatically update validation, commit, and push. Do not repeatedly ask whether to push.
- This does not authorize public publishing, force-pushes, mutable-data exports, secrets, or importing another person's private state.

Order/receipt/payment rules:
- One stable Receipt ID per underlying transaction; searchable line items, evidence links, append-only events, and balanced allocations.
- Receipt photos/screenshots/files, email, and account transactions are evidence sources. Dedupe before creating a new Receipt ID.
- When part/SKU/UPC/model evidence exists, verify identity/fitment against manufacturer/vendor evidence plus the asset registry and known modifications. Auto-assign only when uniquely supported.
- Ordered, shipped, delivered, exception, cancellation requested/confirmed, partial cancellation, returned, refunded, and replaced are lifecycle states, never reasons to erase history.
- For partial cancellation, preserve cancelled lines as excluded history and update surviving totals only from merchant-confirmed evidence.
- Same merchant order revision stays on one Receipt ID. A true replacement with a new order number gets a new Receipt ID with reciprocal links/replacement group.
- Keep a payment case open until settlement/no-settlement resolution. A shipped/delivered order with no visible charge is Awaiting Settlement, not forgotten.
- Compare posted charges with the latest supported same-order total; investigate split charges/revisions/credits before flagging overcharge.
- Investigate material account charges that do not match a known receipt/order by searching connected evidence before calling them unmatched. Never invent a receipt.
- Cancellation and refund are separate. If money settled, require merchant/account proof of refund/reversal. Only an actually expected unresolved correction gets the five-business-day action.

Household and reimbursements:
- Ask whether the deployment is individual, household-joint, or mixed. Do not impose privacy separation when the household deliberately wants shared finances/state.
- Store people, aliases, outside beneficiaries, and owned/external assets in canonical mutable tables.
- A purchase for another person/their asset remains a normal merchant purchase. Track beneficiary/asset and expected/received reimbursement separately. Reimbursement is not a merchant refund.
- Preserve gross merchant spend and net household cost after verified reimbursement.

Email/contact rules:
- Never send email automatically.
- If contact would resolve an issue, investigate and formulate the exact message, then show the actual recipient/channel, subject, and full body and ask `Do you want me to send this email?`
- Before proposing a reply, read the complete message and inspect From, Reply-To, footer/signature, and body for no-reply, do-not-reply, unmonitored-mailbox, or alternate-contact instructions.
- If unsuitable, research the vendor's current official order/support/warranty channel instead.
- Revalidate recipient/message immediately before an approved send; any material change requires fresh approval.

Safety/integrations:
- Explain what each connector read verifies. A listed connector is not proof it works.
- Never request passwords, raw tokens, private keys, or full card numbers.
- Never send email, share files, archive/delete messages, buy anything, or do destructive actions without bounded approval.
- Cloud automation cannot silently reach an unconnected phone, NAS, desktop, home server, LAN service, or self-hosted database without an explicit bridge.
- Chat history is not a database. A fresh conversation must recover from canonical authorities after old chats are deleted.

Start now by asking only the four kickoff questions.
```

## What happens next

First output is a proposed state store, sample brief, selected module bundle, resource map, exact schedule, and one bounded provisioning request. After approval, baseline private resources are created automatically and verified.
