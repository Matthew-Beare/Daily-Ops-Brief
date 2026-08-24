# LyfeOS State Authority Model

LyfeOS separates **portable source** from **mutable life state**.

## Default authority stack

For new-user deployments the default is intentionally boring and inspectable:

- **Git repository:** code, policy, schemas, migrations, feature manifests, non-secret configuration, tests, onboarding, provenance, and recovery/version history.
- **Google Sheets:** structured mutable operational state.
- **Google Drive:** retained documents, images, receipts, manuals, recipe bodies or other bulky evidence that does not belong in table cells.
- **Google Calendar:** optional projection/reminder surface. Calendar is not the sole state authority.

Another supported database can replace Sheets later if its adapter satisfies the same read/write/dedupe/audit contract. Do not require a second state database merely because one is available.

Git is never the default database for recipes, appointments, routines, meal history, shopping rows, medical-event scheduling, receipt bodies, or similar changing personal records.

## Authority Registry

First boot creates an `Authority Registry` in the selected structured state store. Each row has at minimum:

- Authority UUID
- Data Class
- Provider/type
- Provider resource ID or URL
- Owner person UUID
- Scope (`personal`, `household`, `shared`, or another configured scope)
- Read/write capability status
- Sharing policy
- Last verified timestamp
- Notes

Every mutable data class has exactly one canonical authority. Drive evidence can be linked from canonical rows by stable IDs/URLs without becoming a second database.

## Default Sheets / Drive layout

A starter deployment may use one Google Sheet workbook with tables such as:

- `Authority Registry`
- `Interview Ledger`
- `People`
- `Tasks & Projects`
- `Routines & Accountability`
- `Appointments`
- `Calendar Projection`
- `Recipes`
- `Meal Plans`
- `Pantry & Freezer`
- `Shopping & Procurement`
- `Orders / Receipts / Payment Reconciliation`
- `Assets`
- `Knowledge Index`
- `Integration Registry`
- `Run Log`

The exact enabled tables depend on selected modules. Do not create unused databases for sport.

Drive may contain folders such as `Receipts`, `Manuals & Reference`, `Recipes`, `Appointments & Admin`, or another selected evidence class. Sheet rows retain the Drive file ID/link and provenance.

## Sharing and collaboration

Sharing state and sharing a feature are different operations.

A deployment can support:

1. **Personal authority:** only the owner/service accounts explicitly authorized by the owner.
2. **Whole-authority sharing:** the owner deliberately grants another person access to the workbook/folder.
3. **Scoped shared authority:** create/select a separate shared workbook/folder for household, travel, meal planning, projects, or another domain when the owner does not want to expose the entire personal authority.

Never infer that a family member should receive access. Record grants in the Authority Registry and verify provider read/write access after the owner changes sharing.

The system should be able to explain which data would become visible before a broad share.

## Mutation contract

For every state-changing workflow:

1. read the canonical row/object and relevant evidence;
2. correlate/dedupe with stable IDs;
3. write the smallest required mutation;
4. read the canonical authority back;
5. verify identifiers and material fields;
6. only then report completion or trigger dependent projections;
7. retain append-only event/history rows where the module contract requires history.

If the canonical state authority is unavailable, stop that state-changing module and report `Action Required — <authority> unavailable`. Do not substitute chat memory or Git files as mutable state.

## Git lineage

Each user still inherits the public LyfeOS foundation and should have their own Git lineage from first boot. Git records:

- exact upstream version/provenance;
- enabled modules/features;
- schemas and migrations for the selected state store;
- authority *references/types*, never credentials;
- generated deployment policy and configuration;
- integration contracts;
- custom feature code/policy/tests;
- release/recovery history.

After standing Git authorization, lasting behavior/config/schema changes validate, commit, push, and receive remote readback automatically. Routine mutable state changes do not create Git commits.

## Portability boundary

When a personal feature becomes reusable, LyfeOS asks exactly:

`Do you want to make this feature available to other people?`

A yes exports behavior/schema/migrations/tests with synthetic fixtures and configuration placeholders. It never exports the user's Sheet rows, Drive evidence, Calendar events, provider IDs that expose private state, or credentials.
