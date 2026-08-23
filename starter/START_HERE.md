# LyfeOS First Boot — Start Here

This is the human entry point. A new user should not need to edit JSON, run Python, understand Git, or inherit another person's schedules, folders, assets, account IDs, or private data.

## Before starting

1. Open a new ChatGPT Project or conversation.
2. Connect only the apps the user wants LyfeOS to inspect. Connections begin with harmless reads.
3. Have a connected Git provider available. The assistant handles versioning; the user only chooses or approves a private repository.
4. Paste the prompt below.

Read `MODULE_CATALOG.md` after the kickoff. It is the canonical menu of optional modules and first-boot enrollment questions.

## Copy and paste this prompt

```text
Help me set up my own LyfeOS personal-operations system. Treat this as first boot for a non-technical user.

First-boot rules:
- Be useful and conversational. Do not ask me to edit JSON, run code, use a terminal, or understand Git unless I choose developer mode.
- Ask no more than four related questions at a time.
- Begin with exactly these four questions:
  1. What should the system be called?
  2. What IANA timezone is permanently authoritative, including while I travel?
  3. What is my exact job title, what do I actually do, and what is my shift, weekly pattern, and recurring work travel?
  4. How often and at which exact local times do I want briefs and order updates, and should order changes be immediate, digest-only, or immediate only for exceptions?
- Never inherit another user's times or assume twice daily. Use the named timezone so daylight-saving changes remain correct.
- After those answers, read and use MODULE_CATALOG.md. Recommend a small useful bundle, explain each outcome, and explicitly ask which optional modules the user wants. Do not silently enable modules merely because a connector exists.
- At minimum, explicitly offer: recurring briefs; order/shipment lifecycle; searchable receipt database; receipt-driven inventory; receipt-detected financial reports; subscriptions/trials; important-mail triage; calendar reminders; recipes; and knowledge capture.
- Financial-report enrollment must offer weekly, monthly, year-to-date, rolling-12-month, and calendar-year views, while clearly distinguishing receipt/email-detected spending from a complete bank/card ledger.
- After module enrollment, ask what most often slips through the cracks and probe for additional feasible automation opportunities.

Stock Minimum Useful Setup:
- Briefs: one concise manual sample first, then the fewest scheduled dispatchers that deliver the user's chosen local cadence.
- Orders: searchable receipts, shipment state, delivery/exception notifications, classification questions, and a compact active-order view. Never create one task or calendar event per order.
- Receipts: optional searchable receipt/purchase database with canonical evidence, deduplication, lifecycle history, line-item category/asset tags, and balanced allocations.
- Inventory: optional receipt-driven asset inventory for only the domains the user selects.
- Financial views: optional receipt/email-detected weekly, monthly, YTD, rolling-12-month, and calendar-year summaries. Never imply these are complete account ledgers unless an account-level source is connected.
- Recipes: a searchable, readable recipe library using native collapsible headings plus a filterable title/ingredient/tag index. One recipe may have many categories/tags without duplicate recipe bodies.
- State: one authoritative mutable store and a small Drive hierarchy based on the user's real life.
- Modes: conditionally add a per-user `HOME`/`ROAD` layer only for driving, trucking, delivery, field-travel, rotating-site, or recurring overnight-route work; otherwise bypass the module entirely.
- Recovery: one private Git repository containing durable policy, schema, tests, onboarding, and recovery material.

Job-to-mode routing:
- Use the explicit job title, actual duties, shift, and recurring travel pattern. Do not ask only “are you a trucker?”; ask whether the person regularly works away from home enough that the brief should behave differently while away.
- If the role involves driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away from home, offer HOME/ROAD (or user-named equivalent) and collect deterministic boundaries/triggers, early-return or vacation overrides, route/location evidence, and per-mode visibility.
- If the role does not involve recurring work travel, mark HOME/ROAD bypassed and ask no mode questions or create mode controls/automations. Enable it later only on an explicit request.
- Never copy another household member's mode schedule or state. Shared evidence may be linked, but each person keeps separate mutable controls and preferences.
- When paid work is multi-leg, model each actual leg separately. Never assume the worker returns directly from the first destination to home. Close an arrived leg, open the next known leg, and aggregate company/user-confirmed paid miles or pay units inside the configured pay week.

Scheduling and notification rules:
- Ask for the authoritative timezone, frequency, exact local times, and order-notification mode before proposing any schedule.
- Show a manual sample brief and the exact schedule/prompt before the first automation write; obtain explicit approval for that initial bounded setup.
- Inspect active and paused jobs first. Consolidate compatible time slots and never create per-order jobs, duplicate briefs, hidden retries, or support jobs.
- The order pipeline may check before a digest or run on another user-chosen cadence. Exceptions may notify immediately only if the user chooses that mode.

Git checkpoint:
- In the first follow-up stage, ask the user to choose an existing private repository or approve creation of one, then obtain one standing authorization for automatic versioning.
- Setup is not complete and scheduled writes are not enabled until the initial sanitized policy/schema/tests/bootstrap commit is pushed and the remote head is verified.
- After standing authorization, every lasting feature, schema, workflow, schedule, policy, or onboarding change must automatically update validation, commit, and push. Never ask “should I push?” again.
- Automatic push does not authorize auto-merge, public publishing, releases, force-pushes, or committing mutable records, message bodies, receipts, credentials, tokens, keys, or full payment data.

Order and receipt rules:
- Use one stable Receipt ID per underlying transaction with searchable line items, evidence links, append-only events, and balanced allocations.
- Items on the same receipt may belong to different categories, subcategories, cost owners, projects, or assets. Classify line items independently and count the receipt total only once.
- When a manufacturer part number, SKU, or exact product identity exists, verify identity/fitment against credible manufacturer/OEM/vendor evidence and the user's owned assets. Auto-assign only when evidence uniquely resolves the asset; otherwise ask one classification question.
- Ordered, shipped, delivered, exception, cancellation requested/confirmed, partial cancellation, returned, refunded, and replaced are state changes, not reasons to erase audit history.
- For a confirmed partial cancellation, keep cancelled lines as excluded history and update surviving items/totals only from merchant-confirmed evidence.
- A confirmed cancellation disappears from active orders, active shipments, current spend, dashboards, and inventory side effects, but its Receipt ID/evidence remain auditable with spend excluded.
- Cancellation and refund are separate facts. If money settled, do not mark the financial correction complete until exact merchant/account evidence verifies the refund/reversal; if the merchant revised the order before settlement, record that instead of inventing a refund.
- If an expected refund/reversal remains unverified for five business days, surface one Action Required through the normal brief rather than creating a separate reminder automation.
- If no replacement exists, a confirmed cancelled order simply terminates as Cancelled. A same-merchant-order revision stays on one Receipt ID. A true replacement with a new order number gets a new Receipt ID linked bidirectionally to the original through one replacement group.
- If original cancellation/refund is unconfirmed, keep the old order as an exception and track the new order separately; never assume the old charge vanished.
- Unknown ownership/category/asset stays queued for the next chosen brief instead of being guessed.
- Start with the user-editable primary taxonomy in MODULE_CATALOG.md rather than assuming Automotive and Tools are the whole known universe.

Recipe rules:
- Keep titles, ingredients, directions, tags, source links, and provenance as searchable text, not screenshots or opaque blobs.
- Use one canonical recipe body with many tags/categories and links. Preserve source material; inspect, rename, and file ambiguous sources only after the user authorizes the read/write scope.
- Default to a polished native document or app-like view with collapsed recipe headings and an index; keep developer formats out of the user-facing folder.

Integration and safety rules:
- Explain what each harmless connector read verifies. A listed connector is not proof it works.
- Never request passwords, raw tokens, private keys, full card numbers, or secrets in chat.
- Never send email, share files, archive/delete messages, buy anything, or perform destructive actions without explicit bounded approval.
- Explain that cloud automation cannot silently reach a phone, NAS, desktop, home server, LAN service, or self-hosted database without an explicit bridge.

At the end of each stage, show:
1. what is already useful;
2. what is verified versus assumed;
3. the smallest next choices;
4. proposed writes awaiting initial approval;
5. whether the private Git checkpoint is verified.

Once baseline setup is agreed, produce a compact onboarding summary, privacy boundary, integration/automation map, data model, test plan, and Project instructions that point to durable policy instead of copying mutable data.

Start now by asking only the four kickoff questions.
```

## What happens next

The first useful result is a proposed state store, manual sample brief, selected module bundle, folder map, and exact notification schedule. Initial writes and automations remain proposals until approved. Once private-repository standing authorization is granted, later durable Git commits and pushes are automatic.

The remaining files are the deterministic developer/recovery layer.
