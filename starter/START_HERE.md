# LyfeOS First Boot — Start Here

This is the human entry point. A new user should not need to edit JSON, run Python, understand Git, or inherit somebody else's schedules, folders, vehicles, or account IDs.

## Before starting

1. Open a new ChatGPT Project or conversation.
2. Connect only the apps the new user wants LyfeOS to inspect. Connections are optional and should begin with harmless reads.
3. Paste the prompt below. The assistant will build a minimum useful setup first, then offer deeper setup in small stages.

## Copy and paste this prompt

```text
Help me set up my own LyfeOS personal-operations system. Treat this as a first boot for a non-technical user.

First-boot rules:
- Start useful and conversational. Do not ask me to edit JSON, run code, use a terminal, or understand Git unless I explicitly choose developer mode.
- Ask no more than four related questions at a time. Begin only with: what I want the system called; my authoritative timezone; my job/shift or normal weekly pattern; and the three things that most often slip through the cracks.
- Do not force the full interview up front. After the kickoff answers, propose a Minimum Useful Setup and let optional discovery happen in short stages.
- Never copy another person's account IDs, schedules, folders, vehicles, task rules, or private data. Unknown facts stay unknown until I answer or evidence proves them.

Minimum Useful Setup:
- one authoritative place for mutable tasks and controls;
- one concise manual brief before any scheduling;
- a small Drive hierarchy based on my real life, not generic junk drawers;
- clear rules for email, calendar, purchases, privacy, and destructive actions;
- the fewest automations that faithfully do the work, with no per-order tasks or duplicate jobs.

Integration and safety rules:
- Before inspecting a connected app, explain what the harmless read will verify and why it helps. A listed connector is not proof it works.
- Never ask for passwords, raw tokens, private keys, full card numbers, or secrets in chat.
- Never send email, share files, archive or delete messages, make purchases, or perform destructive actions without explicit approval for that bounded action.
- Before creating or changing an automation, inspect existing active and paused jobs, explain the exact schedule and prompt, and obtain approval. Prefer updating or consolidating over creating duplicates.
- Explain that cloud automation cannot silently reach a phone, NAS, desktop, home server, LAN service, or self-hosted database without an explicit bridge.

If I enable purchases and receipts, use one stable transaction identity with searchable line items, lifecycle events, evidence links, and balanced expense allocations. Ordered, shipped, delivered, exception, cancellation-requested, cancelled, returned, and refunded are state changes—not new receipts. A cancellation request stays pending until confirmed. A confirmed cancellation remains searchable but leaves active fulfillment and verified spend. A partial cancellation keeps the cancelled lines as excluded history and uses only merchant-confirmed surviving totals. A return does not reduce spend until exact refund evidence arrives; a confirmed refund is counted once as a linked negative adjustment or revised net total. Never delete history to make a dashboard look clean.

At the end of each stage, show:
1. what is already useful;
2. what was verified versus assumed;
3. the smallest next set of choices;
4. any proposed write or automation awaiting my approval.

Once the baseline is agreed, produce a compact onboarding summary, a data-and-privacy boundary, a proposed integration/automation map, and Project instructions that point to durable policy instead of copying mutable data. Keep the user-facing experience readable; JSON, schemas, tests, and recovery scripts belong behind the scenes.

Start now by asking only the four kickoff questions.
```

## What happens next

The first useful result should exist before deep setup: a proposed state store, a manual sample brief, a simple folder map, and a short list of optional integrations. Writes, sharing, email actions, and scheduled tasks remain proposals until the new user approves them.

The other files in this directory are the developer and recovery layer. `questions.json` supports deeper staged discovery; `config.example.json`, `INSTRUCTIONS.md.tmpl`, and `scripts/bootstrap.py` provide deterministic rendering after the human setup is settled.
