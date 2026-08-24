# LyfeOS Profiles and Context Modes

This contract separates **who the system is helping**, **where/how that person is operating right now**, and **which stock services are active**. Do not collapse these into one giant `mode` flag.

## 1. Per-person life profile

Each primary user/person gets a private mutable profile in the selected canonical structured state authority. A profile may have a user-selected friendly alias, but aliases, family relationships, schedules, appointments, and other personal state never belong in the portable public starter source.

Useful life-profile classes include:
- `working`
- `retired_nonworking`
- `student`
- `caregiving`
- `mixed`
- `custom`

These classes route onboarding questions; they are not identities and may change over time.

Retired/nonworking profile routing bypasses work-away machinery by default. Its brief can instead emphasize selected appointments, household/admin, family commitments, volunteering, hobbies, travel, routines, projects, documents, and other enabled domains. This is the generic pattern for an appointment-centric retired-family deployment without hard-coding any person's name or nickname.

## 2. Dynamic context mode

Context mode answers a different question: **what environment is the person operating in now?** It is enabled only when that distinction materially changes available tasks, equipment, evidence, notifications, routes, weather, or routines.

Examples:
- `HOME / ROAD`
- `HOME / TRUCK`
- `HOME / FIELD`
- `HOME / CAMPUS`
- `HOME / AWAY`
- user-defined labels

The exact labels are user configuration stored in mutable state. Portable source may recommend labels but must never silently decide a personal context split from a job title alone.

Routing contract:
1. Ask employment/life pattern and exact job title/duties when applicable.
2. Ask whether recurring work/sleep away, rotating sites, field work, vehicle living/working, or another environment split actually occurs.
3. If explicitly no, mark context mode `bypassed` unless the user selects another useful split.
4. If explicitly yes, recommend a mode pair from the duties/environment and ask the user to confirm or rename it.
5. If the role strongly suggests travel/field work but work-away evidence is unresolved, mark `needs_confirmation`; never auto-enable from a title keyword.
6. Driver/trucker/courier/delivery roles normally recommend `HOME / ROAD`, with `HOME / TRUCK` as an alternate when the vehicle itself is the useful boundary.
7. Field-service/rotating-site/overnight roles normally recommend `HOME / FIELD` or `HOME / AWAY`.
8. Student/campus contexts may recommend `HOME / CAMPUS` only when location materially changes work or resources.
9. Explicit user-defined labels outrank recommendations.
10. Context mode never changes the deployment's canonical IANA scheduling timezone.

Departure/return evidence, overrides, task visibility, equipment/connectivity, route/weather behavior, paid work units, and mode-specific routine variants are configured only after the context split is selected.

## 3. Stock-provisioned services

The starter ships the contracts for these baseline services so a new user does not have to invent them:
- brief/action digest;
- receipt and order lifecycle;
- recipe library/intake.

**Stock-provisioned does not mean silently enabled.** First boot records an explicit activation state for each service: `enabled`, `disabled`, or `unresolved`.

When enabled:
- Briefs ask for cadence, exact local slot(s), canonical IANA timezone, notification/delivery mode, length, and anti-noise rules.
- Receipt/order lifecycle asks which evidence sources are permitted, update cadence/slot(s), notification behavior, retention, and approval boundaries. It never creates one scheduler job per order.
- Recipe library asks which existing recipe sources should be reconciled/imported and where structured indexes and retained recipe bodies live. Meal planning remains a separate opt-in feature.

A disabled stock service remains available for later activation without reinstalling source.

## 4. AI-use discovery

After the four kickoff questions, onboarding should learn how the person currently uses AI, what work they repeat manually, and what they wish an assistant could remember or coordinate. This is discovery only. Never promise automation that available capabilities cannot actually perform.

## 5. Failure isolation

Profile routing, context routing, briefs, orders, recipes, appointments, and other modules are separate failure domains. Failure of one optional adapter or module must not disable healthy modules. Mutable profile/context/service state remains in its canonical authority; Git stores only the reusable contracts, schemas, tests, and non-secret configuration.

## 6. Verification

Before calling onboarding complete:
- every installed question-bank ID is terminally resolved or explicitly deferred;
- profile class and any private alias are written/read back from canonical state;
- context mode is `bypassed`, explicitly selected, or still visibly unresolved;
- each stock service has an explicit activation state;
- any enabled recurring schedule is verified against its canonical IANA timezone and provider readback;
- no personal alias/state leaked into portable source.