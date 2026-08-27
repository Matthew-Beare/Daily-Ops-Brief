# MIRROR work-packet policy

## Ownership model

The user is the **customer/product owner**. The customer supplies desired outcomes, pain points, preferences, constraints, priority overrides, and acceptance feedback. The customer is not required to decompose work, design architecture, manage dependencies, size packets, maintain backlog state, or understand implementation details.

The assistant/developer owns:

- feature decomposition and stable IDs;
- dependency analysis and backlog ranking;
- architecture and reversible implementation decisions;
- packet sizing and sequencing;
- acceptance-criteria drafting;
- branch/commit/PR discipline;
- test and provider-readback requirements;
- `CURRENT_WORK.md` maintenance;
- roadmap/backlog/feature documentation;
- explicit recovery checkpoints.

Ask the customer technical questions only when the answer materially changes product behavior, cost, irreversible architecture, privacy/safety boundaries, or an acceptance criterion. Prefer a documented reversible engineering decision over wasting customer attention.

## Packet definition

A work packet must represent one bounded outcome, preferably a vertical slice rather than a subsystem. It should normally be finishable and verifiable in one working session.

Every packet records:

- packet ID and name;
- related feature/work IDs;
- branch;
- base SHA and current head SHA;
- objective;
- explicit acceptance criteria;
- dependencies/blockers;
- completed evidence;
- exact next action/resume point.

If a packet is clearly too large, split it **before implementation**. A packet must not silently grow because adjacent ideas were discussed.

## Scope rule

The customer may brainstorm freely without special syntax. New ideas go to the backlog by default.

A new idea may enter the active packet only when:

1. it is required to satisfy an existing acceptance criterion; or
2. it exposes a previously unknown hard dependency that blocks completion; or
3. the customer explicitly overrides/reprioritizes the active packet.

If the customer explicitly reprioritizes, first checkpoint the displaced packet with its exact resume point and record both displaced and new work in Git, then switch scope.

## Priority rule

Backlog priority is dynamic, not FIFO. Recompute priority using this order of concern:

1. data integrity, privacy, security, and active acceptance blockers;
2. hard prerequisites for the active milestone;
3. foundational capabilities that unlock multiple downstream features;
4. user-visible vertical-slice value;
5. reliability/hardening necessary for release evidence;
6. enhancements and cosmetics.

Recent arrival does not make an item low priority. A newly discovered prerequisite may become the next packet immediately.

## Completion rule

Code existence is not feature completion. Track evidence through distinct delivery levels:

1. desired;
2. specified;
3. implemented;
4. test-verified;
5. integration-verified;
6. live-verified.

CI cannot substitute for provider readback, physical-device verification, production signing/registration, live scheduler firing, or mutable external-state proof.

## Green-before-growth rule

Do not add unrelated feature work while the active branch fails required baseline gates. Fix or isolate the failure first unless the failure is explicitly proven unrelated and the packet design documents that boundary.

## Data-preservation rule

Legacy production data is never a development sandbox. Existing user Google spreadsheets, Drive artifacts, briefs, schedules, and other live state must remain untouched during MIRA 2.0 development unless an explicit migration packet authorizes bounded changes.

MIRA 2.0 development uses a separate namespace/data space. A migration packet must include backup, rollback, mapping/reconciliation, dry-run or equivalent preflight, bounded writes, and provider readback.

## Timeout/recovery rule

Assume any session or tool chain can fail without warning. Therefore:

- checkpoint durable work frequently;
- update `CURRENT_WORK.md` at every packet boundary and meaningful interruption;
- never leave the only description of unfinished work in chat;
- after recovery, read Git state before relying on conversation reconstruction;
- record the first uncompleted audit item or implementation step, not merely a vague percentage complete.

## Merge rule

Prefer small PRs and frequent merges. Completed packets should be independently understandable and revertible. Large integration branches may exist as references, but they are not release evidence merely because they aggregate many capabilities.
