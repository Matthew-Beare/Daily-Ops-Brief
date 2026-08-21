# LyfeOS First Boot — Start Here

This is the human entry point. A new user should not need to edit JSON, run Python, understand Git, or inherit another person's schedules, folders, assets, account IDs, or private data.

## Before starting

1. Open a new ChatGPT Project or conversation.
2. Connect only the apps the user wants LyfeOS to inspect. Connections begin with harmless reads.
3. Have a connected Git provider available. The assistant handles versioning; the user only chooses or approves a private repository.
4. Paste the prompt below.

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
- After those answers, propose the stock Minimum Useful Setup before deeper discovery. Then ask what most often slips through the cracks.

Stock Minimum Useful Setup:
- Briefs: one concise manual sample first, then the fewest scheduled dispatchers that deliver the user's chosen local cadence.
- Orders: searchable receipts, shipment state, delivery/exception notifications, classification questions, and a compact active-order view. Never create one task or calendar event per order.
- Recipes: a searchable, readable recipe library using native collapsible headings plus a filterable title/ingredient/tag index. One recipe may have many categories/tags without duplicate recipe bodies.
- State: one authoritative mutable store and a small Drive hierarchy based on the user's real life.
- Modes: conditionally add a per-user `HOME`/`ROAD` layer for driving, trucking, delivery, field-travel, rotating-site, or recurring overnight-route work; otherwise bypass the module.
- Recovery: one private Git repository containing durable policy, schema, tests, onboarding, and recovery material.

Job-to-mode routing:
- Use the explicit job title, actual duties, shift, and recurring travel pattern. If the role involves driving/trucking, delivery routes, field service, rotating worksites, transport crew, or recurring nights away from home, branch into `HOME`/`ROAD` setup and collect deterministic boundaries/triggers, early-return or vacation overrides, route/location evidence, and per-mode visibility.
- If the role does not involve recurring work travel, mark HOME/ROAD bypassed and ask no mode questions or create mode controls/automations. Enable it later only on an explicit request.
- Never copy another household member's mode schedule or state. Shared evidence may be linked, but each person keeps separate mutable controls and preferences.

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
- Ordered, shipped, delivered, exception, cancellation requested/confirmed, returned, refunded, and replaced are state changes—not reasons to erase history. A partial cancellation preserves cancelled lines and uses only merchant-confirmed surviving items and totals.
- A same-merchant-order revision stays on one Receipt ID. A true replacement with a new order number gets a new Receipt ID linked bidirectionally to the original through one replacement group. If original cancellation/refund is unconfirmed, keep the old order as an exception and track the new order separately; never assume the old charge vanished.
- Unknown ownership/category/asset stays queued for the next chosen brief instead of being guessed.

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

The first useful result is a proposed state store, manual sample brief, stock order/recipe design, folder map, and exact notification schedule. Initial writes and automations remain proposals until approved. Once private-repository standing authorization is granted, later durable Git commits and pushes are automatic.

The remaining files are the deterministic developer/recovery layer.
