# MIRA | MIRROR First-Boot Starter

This reusable starter builds a new user's **MIRROR** system with **MIRA** as the default assistant without copying the reference deployment's mutable state.

Start with [`QUICK_START.md`](QUICK_START.md). It is the default non-technical browser path. [`INSTALL.md`](INSTALL.md) is the detailed capability/troubleshooting reference, and [`START_HERE.md`](START_HERE.md) is the deeper interview contract.

The former **Life Planner** name and the `life-planner` skill/package path remain compatibility identifiers during migration.

## What goes where

- **Git or approved managed source**: policy, schemas, migrations, tests, onboarding, non-secret configuration, reusable features, and version lineage.
- **Google Sheets / Microsoft Lists or Excel / another approved structured provider**: mutable personal records and canonical structured state.
- **Google Drive / OneDrive or SharePoint / another approved evidence store**: retained evidence and documents where useful.
- **Calendar**: optional projection and reminders, not automatically the sole state database.

Git is not the default database for mutable personal records.

## Default identity

MIRROR is the system. MIRA is the assistant.

First boot must not make a non-technical user invent those names. A private assistant alias can be chosen later and stored as mutable profile state without renaming upstream.

## Durable interview

First boot creates an `Authority Registry` and an `Interview Ledger` in canonical structured state. Questions stay open until they are answered, resolved from evidence, not applicable, or explicitly deferred. A conversational detour does not silently abandon onboarding.

## Built-in discovery

The starter can discover and configure, when useful:

- briefs and next actions;
- work, study, household, retirement, caregiving, and family contexts;
- meal planning, recipes, groceries, pantry/freezer, and leftovers;
- appointments and reminders;
- orders, receipts, shopping, refunds, and payment reconciliation;
- assets, manuals, identifiers, specifications, and retained knowledge;
- travel/work context modes;
- optional finance and health-organization workflows; and
- reusable custom features.

Existing connected evidence should be inspected before asking the user to rebuild information manually.

## Same code across release channels

MIRROR Personal-Production, Personal-Experimental, and Institutional-Experimental use the same portable application code from one canonical source revision. Channel-specific feature forks are forbidden. Only deployment policy, visibility, approved provider/runtime configuration, data classification, and external mutable state differ.

## Boundaries

Never inherit another deployment's accounts, IDs, timezone, schedules, assets, receipts, tasks, or mutable records. Never treat ChatGPT GitHub read access as proof of Codex write access. Never send email automatically. Never claim a provider write before readback.

The `life-planner` package name is retained until a bounded compatibility migration proves every dependent path and test.
