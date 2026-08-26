<p align="center">
  <img src="starter/clients/pwa/brand-mark.svg" width="96" alt="MIRA logo">
</p>

<h1 align="center">MIRA</h1>
<p align="center"><strong>MIRROR · Reflecting reality.</strong></p>

MIRROR is the reality layer: verified state, identity, evidence, relationships, history, and provenance. MIRA is the intelligence layer that talks with the user, reasons over that reality, plans, recommends, and carries out approved actions.

With the integrations and authorities a user chooses, MIRROR can keep a connected record across assets and inventory, finances and reimbursements, calendars and appointments, email, orders, shipments, receipts and refunds, tasks and projects, reminders, documents and knowledge, travel and work, mileage, meals and groceries, and new domains the user creates. The point is not to dump everything into chat. The point is to maintain durable, queryable reality so MIRA can answer questions and coordinate work from evidence instead of guesswork.

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

Stock MIRA is Google-first. A normal user can use MIRA with ChatGPT and connected Google Workspace without installing Linux, Docker, a homelab, VPS, or separate MIRROR server. GitHub is optional for stock use and becomes necessary when custom executable source must be versioned.

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
