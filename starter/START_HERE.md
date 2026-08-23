# LyfeOS First Boot — Start Here

Human entry point. A new user should not need JSON, Python, a terminal, or Git knowledge.

Before starting: connect only wanted apps, have a private Git provider available, and use `MODULE_CATALOG.md` after kickoff. Connections begin with harmless reads.

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
- Explicitly offer recurring briefs; order/shipment lifecycle; searchable receipt database; receipt-driven inventory; receipt-detected financial reports; subscriptions/trials; important-mail triage; calendar reminders; recipe library; and knowledge capture.
- Financial enrollment must offer weekly, monthly, YTD, rolling-12-month, and calendar-year views and distinguish receipt/email-detected spend from a complete bank/card ledger.
- Then ask what regularly slips through the cracks and probe for feasible automation.

Minimum Useful Setup:
- Briefs: show one manual sample, then use the fewest scheduled dispatchers for my chosen cadence.
- Orders/receipts: searchable evidence, active shipment state, lifecycle events, classification questions, balanced allocations, and a compact active-order view. Never create one task/calendar event per order.
- Inventory: optional receipt-driven assets only for domains I select.
- Recipes: one readable recipe body with searchable title/ingredient/tag/source metadata; many tags/categories without duplicate bodies.
- State: one authoritative mutable store plus a small Drive hierarchy based on my real life.
- Modes: add HOME/ROAD only when recurring work-away-from-home behavior makes it useful.
- Recovery: private Git stores durable policy/schema/tests/onboarding/recovery, never live mutable records or secrets.

Job/mode routing:
- Use exact job title, actual duties, shift, and recurring travel. Ask whether work regularly takes me away from home enough that briefs should behave differently while away.
- For driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away, offer HOME/ROAD (or equivalent), deterministic boundaries, early-return/vacation overrides, route/location evidence, and per-mode visibility.
- For non-travel roles, mark HOME/ROAD bypassed and ask no mode questions or create mode controls. Enable later only by explicit request.
- Keep each person's mode state separate.
- For multi-leg paid work, track each actual leg independently; never assume the first destination returns directly home. Aggregate only company/user-confirmed paid units.

Scheduling:
- Ask authoritative timezone, cadence, exact local times, and notification mode before schedule writes.
- Show the sample brief and exact proposed schedule/prompt before the first automation write; obtain explicit approval.
- Inspect active/paused jobs and consolidate compatible schedules. No per-order jobs, hidden retries, or duplicate briefs.

Git checkpoint:
- Ask the user to choose an existing private repository or approve a new one and obtain one standing authorization for automatic versioning.
- Do not enable scheduled writes until sanitized policy/schema/tests/bootstrap are pushed and remote head is verified.
- After standing authorization, every lasting feature/schema/workflow/schedule/policy/onboarding change must automatically update validation, commit, and push. Do not repeatedly ask whether to push.
- This does not authorize auto-merge, public publishing, releases, force-pushes, mutable-data exports, or secrets.

Order/receipt rules:
- One stable Receipt ID per underlying transaction; searchable line items, evidence links, append-only events, and balanced allocations.
- Items on one receipt may have different categories, subcategories, cost owners, projects, or assets. Classify line items independently and count the receipt total once.
- When a part number/SKU/exact product identity exists, verify identity and fitment from manufacturer/OEM/vendor evidence plus owned-asset specs. Auto-assign only when uniquely supported; otherwise ask one classification question.
- Ordered, shipped, delivered, exception, cancellation requested/confirmed, partial cancellation, returned, refunded, and replaced are lifecycle states, not reasons to erase history.
- For partial cancellation, retain cancelled lines as excluded history and update surviving items/totals only from merchant-confirmed evidence.
- Confirmed cancelled items disappear from active orders/shipments/spend/inventory effects but keep auditable identity/evidence.
- Cancellation and refund are separate. If money settled, require merchant/account proof of refund/reversal; if an order was revised before settlement, record that instead of inventing a refund. After five business days without expected money resolution, surface Action Required through the normal brief.
- Same merchant order revision stays on one Receipt ID. A true replacement with a new order number gets a new Receipt ID with reciprocal links/replacement group. Never assume old money vanished.
- Queue ambiguous ownership/category/asset/fitment; never guess.

Safety/integrations:
- Explain what each harmless connector read verifies. A listed connector is not proof it works.
- Never request passwords, raw tokens, private keys, or full card numbers.
- Never send email, share files, archive/delete messages, buy anything, or do destructive external actions without explicit bounded approval.
- Explain that cloud automation cannot silently reach a phone, NAS, desktop, home server, LAN service, or self-hosted database without an explicit bridge.

At each stage show: what is useful now; verified vs assumed; smallest next choices; proposed writes awaiting initial approval; Git checkpoint state.

When baseline is agreed, produce a compact onboarding summary, privacy boundary, integration map, data model, test plan, and Project instructions that point to durable policy rather than mutable data.

Start now by asking only the four kickoff questions.
```

## What happens next

First output is a proposed state store, manual sample brief, selected module bundle, folder map, and exact schedule. Initial writes/automations wait for approval. Later durable Git commits/pushes follow standing authorization.
