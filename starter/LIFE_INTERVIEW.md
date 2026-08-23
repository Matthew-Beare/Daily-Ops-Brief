# LyfeOS Adaptive Whole-Life Interview

Use this after the four kickoff questions in `START_HERE.md`. Its purpose is discovery and prioritization, not interrogation for its own sake. A person usually does not know every useful AI workflow in advance, so reveal useful options from the problems they describe.

Primary branches include **Exercise / fitness** and **School / study**, alongside work/travel, household, administration, projects, hobbies, maintenance, documents, purchases, money, assets, and knowledge. The interview must discover enough context to answer **what to do next** without reconstructing the user's life from scratch each time.

## Interview mechanics

- Ask no more than four related questions at a time.
- Ask only questions whose answers can change a workflow, state model, schedule, dependency, or recommendation.
- Reflect a compact summary after each domain and correct misunderstandings before provisioning.
- Separate facts, preferences, goals, constraints, and guesses. Never persist a guess as fact.
- Skip non-applicable branches and revisit only when new information makes them relevant.
- Prefer concrete examples: what was forgotten, what happens today, what should happen instead, and what evidence proves completion.
- Identify the smallest useful workflow first, then add progression/automation.
- Record sensitive details only when the selected workflow truly requires them. Never solicit credentials.

## 1. Life-friction discovery

Ask in small batches:
- What repeatedly gets forgotten, delayed, misplaced, or done at the last minute?
- What decisions are made over and over that could use a stable rule or prioritized next action?
- Which information is scattered across email, calendar, notes, photos, documents, apps, or memory?
- Which goals lose momentum because nobody notices a missed week?

Sort answers into candidate domains and recommend a Minimum Useful Setup before optional expansion.

## 2. Work-away and context-mode gate

Ask explicitly: **Do you regularly work away from home, sleep away from home for work, rotate worksites, or live/work from a vehicle or field location?**

If no, mark HOME/ROAD bypassed unless another context split clearly helps.

If yes, interview:
- exact job title and actual duties;
- solo/team arrangement, shift, sleep pattern, and travel rhythm;
- departure/return evidence and irregular-dispatch behavior;
- devices, connectivity, storage, space, and equipment away from home;
- tasks/routines that work anywhere, only at home, only away, or need variants;
- appointments/weather/route/pay information that matters while away;
- paid miles/routes/per diem/commission or other work units only when relevant;
- whether paid route values are symmetric or directional when route mileage exists.

Recommend natural context names such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, or custom labels. Context must never redefine canonical scheduling time.

## 3. Personal accountability and recurring routines

Offer this when the user identifies exercise, household routines, creative practice, maintenance, reading, paperwork, or another recurring commitment. Accountability means evidence plus useful prompting, not scolding.

For each routine capture:
- purpose/outcome;
- target frequency and preferred windows;
- estimated time and component blocks;
- supported contexts;
- equipment/resources;
- normal version and **minimum viable version**;
- completed/partial/skipped/rescheduled definitions;
- check-in timing and anti-nag rule;
- miss/reschedule policy;
- progression/review rule;
- evidence the user wants recorded.

For **Exercise / fitness**:
- support cardio, strength, mobility/stretching, yoga, warm-up/cool-down, or user-defined blocks;
- support progression from user-selected evidence such as consistency, duration, reps/sets, load, exercise variation, or yoga/mobility skill progression;
- distinguish home and away versions when equipment/space differs;
- never invent medical restrictions, diagnoses, calorie targets, or unsafe progression.

Do not infer completion from silence.

## 4. Education and study coach

Offer this for school, certification, professional development, language learning, or another structured track.

Capture:
- institution/program/course/certification and current milestone;
- source locations for syllabi/materials;
- verified assignments, exams, projects, and deadlines;
- current complete/in-progress/blocked/not-started state;
- weekly study target and realistic session sizes;
- preferred study methods;
- **home versus away/on the road** work options;
- offline/download requirements and device constraints;
- realistic study windows;
- accountability behavior after missed sessions;
- optional Calendar Projection.

Next-action rule:
1. read verified deadlines and prerequisites;
2. choose the smallest actionable next step;
3. favor urgent/high-impact work without skipping prerequisite learning;
4. fit the action to current context/time when known;
5. keep context-incompatible work in backlog;
6. update progress only from user confirmation or connected evidence.

The system may explain, quiz, summarize user-provided material, plan study, and review work. It must not fabricate submissions, attendance, grades, citations, or proof of work and must not encourage academic dishonesty.

## 5. Household, administration, projects, and hobbies

Explore only useful areas:
- chores and seasonal maintenance;
- appointments/renewals;
- bills/subscriptions/trials/paperwork;
- actionable mail/documents;
- shared household responsibilities;
- grouped errands;
- active projects with milestones/next actions;
- hobbies and long-term goals;
- warranties/manuals/product records;
- vehicles/equipment/home assets;
- recipes/meal planning/shopping intent.

Avoid turning every fact into a reminder.

## 6. Information, assets, and knowledge

Ask what the user repeatedly searches for: receipts, manuals, school documents, employment records, warranties, recipes, policies, notes, reference PDFs, photos, vehicle specs, or other evidence.

For selected classes define:
- authoritative storage;
- naming/index fields;
- immutable identity where appropriate;
- source/provenance;
- dedupe rules;
- retention;
- how later queries return canonical links and page/section provenance when supported.

## 7. Communication and email

Ask which senders/domains matter, what is actionable, what should be grouped with orders/projects, what must never be archived automatically, and whether drafting assistance is wanted. External sending is approval-gated; never turn accountability into messages to another person without explicit authority.

## 8. Calendar and time

Ask which facts deserve Calendar Projection versus brief/task visibility only. Candidate classes include appointments, work travel, deadlines, deliveries, study sessions, routines, bills, trials, maintenance, and selected tasks.

For each enabled class collect target calendar, canonical timezone semantics, tentative-date handling, revision/cancellation behavior, and attendee policy.

### Scheduler evidence chain

When Scheduled Tasks are enabled, setup must verify:
1. canonical VEVENT/TZID/local time;
2. exactly one intended enabled dispatcher and correct timing mode;
3. expected **notification** state;
4. no active **duplicate** jobs;
5. a subsequent **actual firing** or canonical Run Log in the intended local slot after creation/repair.

A `default_timezone` or stored/default/execution-timezone label is authoritative only when the **provider contract** explicitly says it is persistent task execution state. Travel/device timezone is context. Do not create compensation schedules merely because ambiguous metadata follows the user while traveling.

## 9. Money and purchase organization

Ask whether the user wants searchable receipt/order history, active shopping/procurement intent, account-level transaction reconciliation, subscriptions/trials, reimbursements/shared purchases, budgets, or reports.

Keep concepts separate: shopping intent is not purchase history; merchant refund is not household reimbursement; expected charge is not posted charge; and one purchase total is never counted once per category/asset.

## 10. Git/source visibility and recovery

Ask which Git repository holds durable source and whether it is public or private.

- Public and private repositories are both supported.
- Public source must pass public-source audit and contain no secrets, credentials, mutable operational exports, private message/receipt bodies, financial account data, or other information the owner did not intentionally publish.
- Private source follows the same no-secrets rule.
- Repository visibility is verified from provider metadata, not assumed from a file name or README.
- A fork of the public upstream never authorizes inheriting the reference deployment's authorities or mutable state.

A fresh conversation should recover from canonical state/evidence plus versioned source, not remembered chat history.

## 11. Brief design and anti-noise rules

Ask what deserves interruption versus digest, preferred length, priority model, what stays visible until done, what disappears after acknowledgement, which sections vary by context, and degraded-module wording.

Every brief should answer some combination of: what changed, what needs action, what is next, and what can safely be ignored.

## 12. Final synthesis before provisioning

Before the initial write bundle, summarize:
- canonical timezone and context model;
- top problems to solve;
- selected and deferred modules;
- routine/accountability rules;
- school/study workflow;
- authoritative apps/data;
- schedules/notifications and scheduler evidence plan;
- repository/visibility/source-audit policy;
- destructive/external-send boundaries;
- Git recovery/versioning state;
- remaining ambiguity.

Then show the Minimum Useful Setup. Provision only after explicit approval, verify every write, and keep optional expansion available without requiring a rebuild.