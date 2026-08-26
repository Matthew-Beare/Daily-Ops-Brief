<p align="center">
  <img src="assets/brand/mira-logo.png" width="320" alt="MIRA — Reflecting reality">
</p>

<h1 align="center">MIRA</h1>
<p align="center"><strong>Reflecting reality.</strong></p>
<p align="center"><strong>MIRA is the assistant. MIRROR is the private data and evidence that keeps MIRA grounded.</strong></p>

## The simple version

**MIRA is the assistant you talk to.** It reasons, plans, recommends, and helps carry out approved actions.

**MIRROR is the private data and evidence underneath MIRA.** It keeps the durable record of what is actually true: your settings, files, identities, relationships, history, evidence, and connected data.

**The MIRA app is one client for the system.** It is mainly a dashboard plus a fast way to capture or ingest information into MIRROR. The app is useful on a phone, computer, or always-on tablet, but it is **not the whole MIRA/MIRROR project**. MIRA can also work through ChatGPT and other supported assistant surfaces.

You should not need to understand databases, schemas, provider APIs, record IDs, or infrastructure to use MIRA. Those details stay under Advanced unless you deliberately go looking for them.

MIRROR is the deeper reality layer: verified state, identity, evidence, relationships, history, and provenance. With the integrations and authorities a user chooses, it can maintain connected records across assets and inventory, finances and reimbursements, calendars and appointments, email, orders, shipments, receipts and refunds, tasks and projects, reminders, documents and knowledge, travel and work, mileage, meals and groceries, and new domains the user creates. The point is not to dump everything into chat. The point is to maintain durable, queryable reality so MIRA can reason from evidence instead of guesswork.

> **MIRA, mirror on the wall...**

## Start here

Non-technical users start with [`starter/QUICK_START.md`](starter/QUICK_START.md). It explains Git and GitHub in plain language and requires no command prompt, terminal, local Git client, token, SSH key, or code editor.

[`starter/INSTALL.md`](starter/INSTALL.md) is the detailed browser-only reference for capability gates and troubleshooting. [`starter/START_HERE.md`](starter/START_HERE.md) is the deeper first-boot interview contract. The default reality layer is **MIRROR** and the default assistant is **MIRA**; a user does not have to invent either name.

## Build and share new skills

MIRA is designed to grow with the user. A non-technical user can describe a recurring problem in ordinary language, for example: `Design a feature that tracks maintenance for my equipment and reminds me when service is due.`

MIRA should then:

1. inspect existing capabilities first so it does not build a duplicate;
2. define the behavior, required evidence, state authority, permissions, connectors, failure behavior, and success criteria;
3. target every supported client automatically unless the feature is inherently platform-specific;
4. create executable work on a feature branch and keep reusable behavior separate from private user data;
5. add or update configuration, schemas or migrations, tests, and synthetic fixtures as needed;
6. test the feature against synthetic fixtures and verified interfaces, then commit and push a coherent checkpoint;
7. preserve the user's previous Personal Production revision for rollback; and
8. keep the feature private by default unless the user explicitly chooses to publish it.

The full contract is in [`starter/SHARED_FEATURE_WORKFLOW.md`](starter/SHARED_FEATURE_WORKFLOW.md).

## Architecture

MIRA always uses a durable MIRROR data layer. There is no chat-only deployment.

The three supported deployment choices are:

1. **Cloud** — ChatGPT plus Google Workspace or Microsoft 365. This is the recommended setup and requires no Linux or self-hosted server.
2. **Cloud + local services** — the same cloud MIRROR, plus optional bridges to services such as Home Assistant, Plex or Paperless on the user's network.
3. **Self-hosted** — ChatGPT plus a user-owned MIRROR deployment. Google and Microsoft become optional integrations.

The MIRA app is deliberately narrower than the whole platform. It provides display, capture, scanning, file/photo ingestion, inventory interaction, provider setup, diagnostics, notifications, and optional always-on display behavior. Higher-level reasoning such as meal planning, nutrition recommendations, purchase-pattern analysis, scheduling strategy, or other assistant work belongs to MIRA. The app may display those results or collect opted-in inputs, while MIRROR holds the durable context.

For every supported mode, **ChatGPT and every MIRA app must reference the same MIRROR authority**. A client write is not successful until it is written to MIRROR and read back from the selected authority. Photos, receipts and files must also be linked to the correct MIRROR record before success is shown.

Self-hosted MIRROR is an optional deployment for native/offline/local-service workflows. Clients talk to the MIRROR API rather than directly to SQLite, PostgreSQL, Google Sheets, Drive, OneDrive, or local integrations, so authorities can migrate without rewriting Android, Windows, Linux, and web clients.

Mutable operational state does not live only in chat or Git. It lives in the selected canonical authority, with retained evidence in the selected evidence store when needed. The portable source contains no credentials, live authority IDs, private receipt or email bodies, or mutable personal exports.

## Release channels

All three onboarding repositories use one portable code line:

- **MIRA Personal Production** — canonical source;
- **MIRA Public Experimental** — sanitised public experimental distribution; and
- **MIRA Institutional Experimental** — sanitised institutional experimental distribution containing no live regulated or operational data.

All channels consume the same portable application code from the same canonical source revision. Channel differences are limited to approved deployment policy, provider/runtime configuration, data classification, and external mutable state. There are no channel-specific feature forks.

## Reliability rules

- MIRA reasons from MIRROR's verified state; guesses never silently become reality.
- One canonical authority owns each mutable data class.
- Important provider writes require readback before success is reported.
- Email sending remains approval-gated.
- Optional connector failures degrade only the dependent module.
- Recurring work uses consolidated scheduling rather than one task per order, appointment, or chore.
- Clean upgrades preserve the previous Personal Production revision for rollback; source conflicts stop for a plain-language human decision.
- Green CI proves source integrity, not live provider behavior, physical hardware behavior, or an actual scheduled firing.

## Validate

```bash
python3 scripts/validate_repo.py .
python3 scripts/feature_catalog.py --check
python3 scripts/audit_public_source.py . --history
python3 scripts/audit_starter_privacy.py starter
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skill/ops-brief-policy/scripts -p 'test_*.py'
python3 starter/tools/validate_feature_manifest.py --check-files
python3 -m unittest discover -s starter/tests -p 'test_*.py'
```
