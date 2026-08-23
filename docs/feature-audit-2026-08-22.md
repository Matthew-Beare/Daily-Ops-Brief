# LyfeOS / Daily Ops Feature Audit — 2026-08-22

This audit reconciles the user's durable requirements from the Daily Briefs project against live authorities and the two existing development branches. It is a release checklist, not mutable user state.

Status legend:

- **LIVE** — verified in current Sheets/automations or active connector behavior.
- **BUILT-PR2** — implemented on `codex/ops-overhaul-20260821` / PR #2 but not merged to `main`.
- **BUILT-PR1** — useful implementation exists only on `codex/rebuildable-ops-brief` / PR #1 and must be preserved during integration.
- **GAP** — requested behavior is not yet a verified implementation.
- **INFRA** — architecture is defined or desired, but requires a user-controlled bridge/service before it can run.

## 1. Brief scheduler and output

- **LIVE** Exactly one active Ops Brief automation, exact `02:45` and `14:45` America/New_York dispatcher; PM is the user's morning brief.
- **LIVE** Exactly one active Receipt & Order Lifecycle automation, exact `01:45` and `13:45` America/New_York.
- **BUILT-PR2** One deterministic Run ID per slot, Run Log, compact non-empty output sections, no duplicate support/retry jobs.
- **BUILT-PR2** Weather → route weather → shipments → appointments → important email → Ops status → miles/pay → action required → trip status ordering.
- **BUILT-PR2** Persistent/High/Medium/Low task model with classification/subsystem and visibility gates.

## 2. HOME / ROAD and trucking

- **LIVE** User-specific current schedule/state exists in the Ops Status Register; active `TRIP-001` is Morristown, TN → Rialto, CA, terminal RTO, I-40 west.
- **BUILT-PR2** Mode precedence: live unexpired explicit override > active trip forces ROAD > weekly default.
- **BUILT-PR2** Weekly default for this user: ROAD Friday 12:00 ET through Wednesday 16:30 ET, HOME otherwise; real active-trip delay can keep ROAD past the normal return boundary.
- **BUILT-PR2** ROAD suppresses ordinary HOME chores and Shady Valley HOME weather; route/location/ETA/status remain visible.
- **BUILT-PR2** Friday PM destination confirmation only when a planned/active trip does not already provide the destination.
- **BUILT-PR2** Saturday 02:45 AM routine location checkpoint for active trips when fresh location evidence is missing.
- **BUILT-PR2** First boot asks exact job title, actual duties, shift, weekly pattern, and recurring work travel.
- **BUILT-PR2** HOME/ROAD onboarding is conditional. Driving, trucking, delivery, field service, rotating worksites, transport crew, or recurring nights away enables the branch; non-travel roles bypass all HOME/ROAD questions and controls.
- **BUILT-PR2** Household members keep separate mutable mode state even if evidence is shared.

## 3. Appointments

- **BUILT-PR2** Appointment confirmation state is never rendered.
- **BUILT-PR2** Saturday 02:45 AM shows the next seven calendar days.
- **BUILT-PR2** Other AM briefs show that day's appointments; every PM brief shows the following day, producing day-before and morning-of reminders.
- **BUILT-PR2** Appointment cadence is mode-independent.

## 4. Mileage and pay

- **LIVE** Separate Mileage & Pay Tracker exists; rate is `$0.986` per company-paid mile.
- **LIVE** Current outbound `TRIP-001` entry records 2,184 company-paid miles and `$2,153.42` gross estimated.
- **BUILT-PR2** Thursday summary is mode-independent. Being HOME Wednesday PM and Thursday does not suppress either Thursday miles/pay summary.
- **BUILT-PR2** Friday-through-Thursday pay-week logic and Final/Estimated/Planned breakdown.
- **BUILT-PR2** Never infer company-paid/settlement miles from map distance; user/company evidence only.
- **BUILT-PR2** Hardened 3.1.1 runtime makes mileage failure section-scoped. Non-Thursday mileage failure cannot kill a brief; Thursday becomes Degraded with `Action Required — mileage/pay Sheet unavailable` and continues other sections.

## 5. Gmail, important mail, and mail safety

- **BUILT-PR2** Full relevant thread reads; snippets are not sufficient evidence.
- **BUILT-PR2** Important actionable mail stays in Inbox under `Ops/Archive Approval`; silence is not approval.
- **BUILT-PR2** Important-mail section ends with `Is it OK to archive these emails?`.
- **BUILT-PR2** Never send email automatically.
- **BUILT-PR2** Never delete Gmail without an explicit bounded request.
- **BUILT-PR2** Promotions/sales monitoring remains off unless explicitly reinstated.

## 6. Orders, shipments, cancellations, replacements, returns, refunds

- **LIVE** Active Shipments tab and Purchase & Receipt Archive are established authorities.
- **BUILT-PR2** One active shipment row per fulfillment/order; ordered → shipped → delivered/exception lifecycle.
- **BUILT-PR2** Delivered items are removed from active Shipments immediately, retained in append-only events, and reported exactly once in the next eligible brief.
- **BUILT-PR2** Five business days without credible progress becomes Action Required.
- **BUILT-PR2** Carrier evidence outranks stale vendor status; explicit user delivery statements outrank carrier evidence.
- **BUILT-PR2** Same merchant order revision stays on one Receipt ID.
- **BUILT-PR2** True replacement with a new merchant order number gets a new Receipt ID, reciprocal links, and a replacement-group ID; the cancelled/original order is never overwritten.
- **BUILT-PR2** Partial cancellations preserve cancelled lines and use merchant-confirmed surviving totals.
- **BUILT-PR2** Forwarded Amazon mail is parsed from the embedded sender/body instead of rejected because of the forwarding account.
- **BUILT-PR2** No per-order tasks, calendar events, or one-off automations.

## 7. Receipt archive, allocation, Drive, and inventory

- **BUILT-PR2** One canonical readable receipt per transaction, stable Receipt ID, searchable details, append-only events, many tags/assets, balanced allocations.
- **BUILT-PR2** Automotive filing uses exact vehicle folders; multi-vehicle purchases use links/allocations rather than duplicate spend.
- **BUILT-PR2** Tool receipts route to tool categories and can update Tool Inventory after integrity checks.
- **BUILT-PR2** Unknown category/vehicle/owner is queued, never guessed.
- **BUILT-PR2** Audit gate blocks archival/success unless database, Drive, classification, allocation, mapping, shipment, and required inventory side effects agree.
- **BUILT-PR2** Receipt Browser remains compact and searchable with expandable detail links.
- **GAP** The broader requested receipt taxonomy for house, bills, education, medical/personal records, warranties, etc. needs a verified generalized category map rather than only automotive/tools examples.

## 8. First boot / new-user enrollment

- **BUILT-PR2** Non-technical first boot: no JSON, terminal, Python, or Git knowledge required unless developer mode is chosen.
- **BUILT-PR2** First four questions are: system name; permanent authoritative IANA timezone; exact job/duties/shift/travel pattern; exact brief/order cadence plus notification mode.
- **BUILT-PR2** A new user never inherits this user's Eastern timezone, 2:45/1:45 schedules, vehicles, folders, or trucking rules.
- **BUILT-PR2** After kickoff, ask what slips through the cracks and probe for feasible automation opportunities.
- **BUILT-PR2** Stock Minimum Useful Setup includes briefs, consolidated order/receipt lifecycle, searchable recipe library, one mutable state authority, Drive structure, conditional modes, and private Git recovery.
- **BUILT-PR2** Manual sample brief and exact schedule are shown before the first automation write; initial bounded setup needs approval.
- **BUILT-PR2** Connectors begin with harmless reads; explain what each read verifies.
- **BUILT-PR2** Private-device/LAN limitations are explained instead of pretending cloud ChatGPT can silently reach a phone, NAS, desktop, or homelab.

## 9. Recipes

- **BUILT-PR2** Recipes are a stock first-boot module.
- **BUILT-PR2** Searchable title/ingredient/tag/source metadata, one canonical recipe body, many tags/categories, provenance preserved.
- **BUILT-PR2** Default human-facing representation is native/readable and collapsible rather than developer JSON.
- **GAP** Existing personal recipe corpus still needs migration/verification before this becomes live data rather than framework capability.

## 10. Git, policy-as-code, recovery, and change control

- **LIVE** Private repository exists: `Matthew-Beare/Daily-Ops-Brief`.
- **BUILT-PR2** Git is sole durable policy/code/test/bootstrap authority; Sheets remain sole mutable operational-state authorities.
- **BUILT-PR2** After initial standing authorization, every lasting policy/schema/feature/workflow/schedule/onboarding/output change automatically validates, commits, pushes, and verifies remote state without asking `should I push?` again.
- **BUILT-PR2** Standing authorization explicitly does not permit public publishing, releases, force-pushes, secrets, mutable data exports, or automatic PR merge.
- **BUILT-PR2** Policy fingerprint and Project-instruction bootstrap validation exist.
- **BUILT-PR1** Rebuildable skill renderer, Project-instruction renderer, schema contracts, migration files, shared-feature workflow, portable feature-manifest schema, starter isolation tests, and feature-manifest validator exist on PR #1 and must not be lost.
- **GAP** PR #1 and PR #2 are both draft/unmerged and diverged from `main`; the mature implementation is therefore not yet canonical production history.
- **GAP** Installed `$ops-brief-policy` deployment must be verified against the final merged commit; repository and runtime currently cannot be assumed identical merely because both exist.

## 11. Backups and durable data recovery

- **GAP** Requested backup policy — twice-daily incremental, daily cloud backup, weekly full, automatic rotation — is not yet a verified executable implementation in the current repo. It needs a concrete storage target, retention schedule, encryption/secret handling, and restore test.
- **BUILT-PR2** General recovery order and private-device boundaries are documented.

## 12. Knowledge ingestion / personal knowledge store

- **GAP** Requested knowledge ingestion contract needs a dedicated implementation: store only relevant excerpts by default, precise timestamps, source URL/title/metadata, provenance, searchable relationships, and optional pinning of full raw source.
- **GAP** Automatic persistence of newly verified specifications/part numbers/fitment/procedures into a structured knowledge store is not yet verified as executable.

## 13. Hierarchical storage / QR inventory

- **GAP** Immutable item IDs, QR scan-in/scan-out, hierarchical storage locations, grocery/inventory flows, and location queries are vision-level requirements, not verified runtime features yet.

## 14. Finance and spending

- **BUILT-PR2** Email/receipt-detected spending is explicitly distinguished from a complete bank/card ledger.
- **BUILT-PR2** Balanced expense allocations prevent multi-tag or multi-vehicle double counting.
- **GAP** Account-grounded finance automation requires a connected account-level finance source and should remain a separate capability from receipt-detected spend.

## 15. Home Assistant, Plex, voice, and self-hosted services

- **INFRA** Home Assistant/Plex/voice/private-SQL integrations require an explicit bridge/API/VPN/service account. The cloud system must not pretend they are directly reachable.
- **GAP** No production bridge contract is yet committed for these integrations.

## 16. Multi-user / family forks

- **BUILT-PR2** First boot is designed to create user-specific configuration rather than clone this user's mutable state.
- **BUILT-PR1** Portable feature contracts support sharing a capability without leaking production/user data.
- **GAP** A tested fork/update mechanism for family instances, including controlled upstream feature propagation, remains to be integrated across the two branches.

## Release blockers

1. Reconcile PR #2 with current `main` without losing the 3.1.1 ROAD/mileage fixes.
2. Port the unique PR #1 shared-feature/manifest/rebuild tooling into the integration branch.
3. Run all policy, shipment, bootstrap, repo-validation, project-instruction, and starter-isolation tests.
4. Verify CI on the resulting commit.
5. Merge only with explicit authority because the standing Git authorization forbids automatic PR merge.
6. Redeploy `$ops-brief-policy` from the verified merged source and verify its fingerprint/runtime behavior.
7. Re-run the Saturday ROAD/malformed-mileage regression and Thursday-HOME mileage regression against the deployed skill.

Until those blockers are cleared, do not call the repository fully production-integrated even though most requested core functionality has been built.
