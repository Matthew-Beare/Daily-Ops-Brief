# LyfeOS Adaptive Whole-Life Interview

Use this after the four kickoff questions in `START_HERE.md`. Its purpose is discovery and prioritization, not interrogation for its own sake. A person usually does not know every useful AI workflow in advance. The interview should reveal where structured state, reminders, evidence, planning, accountability, search, or automation would materially help.

Primary accountability branches include **Exercise / fitness** and **School / study**, alongside household, administrative, project, hobby, maintenance, document, purchase, work and user-defined life domains. The interview must discover enough context to answer **what to do next** without reconstructing the user's life from scratch each time.

## Interview mechanics

- Ask no more than four related questions at a time.
- Ask only questions whose answers could change a recommendation, workflow, state model, schedule, or dependency.
- Reflect a compact summary after each domain and correct misunderstandings before provisioning.
- Separate facts, preferences, goals, constraints, and guesses. Never convert a guess into persistent state.
- Skip non-applicable branches. Revisit a branch later if new information makes it relevant.
- Prefer concrete examples: what was forgotten, what happens today, what should happen instead, and what evidence proves completion.
- Identify the smallest useful workflow first, then progression/automation after the manual workflow makes sense.
- Record sensitive personal details only when actually needed for the selected workflow. Never solicit credentials or unrelated medical/private information.

## 1. Life-friction discovery

Start by finding the recurring pain rather than pitching features.

Ask in small batches:
- What repeatedly gets forgotten, delayed, misplaced, or done at the last minute?
- What decisions are made over and over that could use a stable rule or prioritized next action?
- Which parts of life feel scattered across email, calendar, notes, photos, documents, apps, or memory?
- Which goals are important but inconsistent because no one notices when momentum disappears?

Then sort the answers into candidate domains such as work/travel, school, routines/fitness, household, money/admin, purchases, vehicles/equipment, maintenance, documents, relationships, appointments, hobbies/projects, recipes, or knowledge.

## 2. Work-away and context-mode gate

Ask explicitly: **Do you regularly work away from home, sleep away from home for work, rotate worksites, or live/work from a vehicle or field location?**

If no:
- mark HOME/ROAD bypassed unless another context split would clearly help;
- do not burden the user with route/travel questions.

If yes, interview:
- exact job title and actual duties;
- solo/team arrangement, shift and sleep pattern;
- normal departure/return rhythm and what reliably proves each transition;
- whether travel is predictable, dispatch-based, rotating, or irregular;
- what devices/connectivity/storage are available away from home;
- tasks/routines that can happen anywhere, only at home, only away, or need different versions;
- appointments/weather/route/pay information that matters while away;
- paid miles, routes, per diem, commissions, or other employer units only when relevant;
- whether paid route values are symmetric or directional when route mileage exists.

Recommend natural context names such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, or custom labels. Mode changes must be deterministic and must not redefine the canonical timezone.

## 3. Personal accountability and recurring routines

Offer this when the user names a habit, exercise plan, household routine, creative practice, maintenance cadence, medication reminder, or another recurring commitment. Do not assume accountability means aggressive nagging.

For each selected routine capture:
- purpose and desired outcome;
- target frequency and preferred days/windows;
- estimated total time and optional component blocks;
- where it can happen and which context modes support it;
- equipment/resources required;
- normal version and minimum viable version for difficult days;
- what counts as completed, partial, skipped, or intentionally rescheduled;
- preferred check-in timing and tone;
- what happens after a miss: reschedule, reduce scope, review cause, or simply continue next cycle;
- progression rule and review cadence when progression matters;
- evidence the user wants recorded, such as duration, sets/reps, session type, completion checkbox, notes, or milestone.

For exercise/fitness routines specifically:
- allow components such as cardio, strength, mobility/stretching, yoga, warm-up/cool-down, or user-defined blocks;
- support progression by evidence such as consistency, duration, repetitions, load, exercise variation, or a user-defined yoga/mobility progression;
- distinguish a home routine from an away/road version when equipment or space differs;
- never invent injury restrictions, medical diagnoses, calorie targets, or unsafe progression. User-provided health constraints are constraints, not material for diagnosis.

Accountability behavior:
- surface the agreed next action before the session;
- do not claim completion from silence;
- record misses without moralizing;
- avoid repeating a reminder after acknowledgement when the anti-nag rule says not to;
- use trends to adjust the plan only with user-supported evidence.

## 4. Education and study coach

Offer this when the user is in school, certification training, professional development, language learning, or another structured learning track.

Capture:
- institution/program/course/certification and current term or milestone;
- syllabi, assignment lists, exam dates, project deadlines and source locations;
- current standing: what is complete, in progress, blocked, or not started;
- weekly study target and realistic session lengths;
- preferred study methods and materials;
- which work can be done at home versus away/on the road;
- offline/downloadable materials or device constraints while away;
- recurring windows when study is realistically possible;
- how the user wants accountability handled after missed sessions;
- whether calendar projection of deadlines/study blocks is wanted.

Next-action engine:
1. read verified deadlines and prerequisite relationships;
2. identify the smallest actionable next step;
3. favor urgent/high-impact work without ignoring prerequisite study;
4. offer a short session when time/energy is constrained;
5. maintain a separate backlog for items that cannot be done in the current context;
6. update progress only from user confirmation or connected evidence.

The system may explain concepts, quiz, summarize user-provided materials, make study plans, and help organize work. It must not fabricate finished assignments, attendance, grades, or evidence and must not encourage academic dishonesty.

## 5. Household and personal administration

Explore only relevant areas:
- recurring chores and seasonal maintenance;
- appointments and renewals;
- bills, subscriptions, trials and paperwork;
- mail/documents that require action;
- shared household responsibilities and ownership;
- errands that should be grouped by place/context;
- warranties, manuals and product records;
- vehicles/equipment/home assets needing maintenance or parts;
- recipes, meal planning, shopping intent or consumables when wanted.

Ask which items should appear in briefs, calendar, task state, or only searchable reference. Avoid turning every fact into a reminder.

## 6. Projects, hobbies and long-term goals

For each meaningful project or goal capture:
- outcome and why it matters;
- current state and next milestone;
- deadline if real, not invented;
- dependencies/materials/documents;
- recurring or one-time work sessions;
- context restrictions such as home-only equipment;
- next-action rule;
- review cadence and completion definition.

Separate a project backlog from active commitments so briefs do not become a landfill of aspirational nouns.

## 7. Information and document retrieval

Ask what the user repeatedly searches for: receipts, manuals, school documents, employment records, vehicle specs, warranties, recipes, policies, notes, reference PDFs, photos, or other evidence.

For selected classes define:
- authoritative storage;
- naming/index fields;
- immutable identity where appropriate;
- source/provenance;
- dedupe rules;
- retention;
- how a future query should return the item, including canonical links and page/section when supported.

## 8. Communication and email

Ask:
- which senders/domains matter;
- what is actionable versus merely informational;
- which messages should be grouped with orders/projects;
- what should never be archived automatically;
- whether draft assistance is wanted.

External sending is always approval-gated. Never silently turn accountability into messages to another person.

## 9. Calendar and time

Ask which facts deserve calendar projection versus brief/task visibility only. Candidate classes include appointments, work travel, deadlines, deliveries, study sessions, routines, bills, trials, maintenance, and selected tasks.

For every enabled class collect:
- target calendar;
- timezone semantics;
- tentative-date handling;
- revision/cancellation behavior;
- attendee/invite policy.

A schedule is not healthy until both its visible timezone definition and the provider's stored/execution timezone match the canonical IANA timezone. Current travel/device timezone is context, not scheduling authority.

## 10. Money and purchase organization

Ask whether the user wants:
- searchable receipt/order history;
- active shopping/procurement intent;
- account-level transaction reconciliation;
- subscriptions/trials;
- reimbursements/shared purchases;
- budgets/reports.

Keep concepts separate: shopping intent is not purchase history, merchant refund is not household reimbursement, expected charge is not posted charge, and one purchase total must not be counted once per category/asset.

## 11. Brief design and anti-noise rules

Build the brief only after the interview identifies useful domains.

Ask:
- what deserves interruption versus digest;
- preferred length;
- priority model;
- what stays visible until done;
- what disappears after acknowledgement;
- which sections vary by context mode;
- what degraded-module wording is acceptable.

Every brief should answer some combination of: what changed, what needs action, what is next, and what can safely be ignored.

## 12. Final synthesis before provisioning

Before any initial write bundle, summarize:
- canonical timezone and work/context model;
- top problems to solve;
- selected modules and rejected/deferred modules;
- routines/goals and accountability rules;
- school/study workflow if selected;
- authoritative apps/data;
- schedules/notifications;
- destructive/external-send approval boundaries;
- Git recovery/versioning state;
- anything still ambiguous.

Then show the Minimum Useful Setup first. Provision only after explicit approval, verify every write, and keep optional expansion available without requiring a rebuild.
