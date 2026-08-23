# LyfeOS Adaptive Whole-Life Interview

Use this after the four kickoff questions in `START_HERE.md`. Its purpose is discovery and prioritization, not interrogation. A person usually does not know every useful workflow in advance, so combine life-friction questions with capability/evidence discovery and reveal useful options from the problems they describe.

Primary branches include work/context, existing systems, apps/plugins, Exercise / fitness, School / study, food/meal planning, household/admin, projects/hobbies, travel/vacations, appointments, purchases/money, assets/knowledge, and communication. Ask no more than four related questions at a time and skip non-applicable branches.

## Interview mechanics

- Ask only questions whose answers can change a workflow, state model, dependency, schedule, or recommendation.
- Before re-asking factual history, inspect accessible existing evidence per `CAPABILITY_DISCOVERY.md`.
- Reflect a compact domain summary and correct misunderstandings before provisioning.
- Separate facts, preferences, goals, constraints, and guesses. Never persist a guess as fact.
- Prefer concrete examples: what was forgotten, what happens now, what should happen instead, and what evidence proves success.
- Identify the smallest useful workflow first, then progression/automation.
- Record sensitive details only when the selected workflow truly requires them. Never solicit credentials.

## 1. Life-friction and identity discovery

Ask in small batches:
- What repeatedly gets forgotten, delayed, misplaced, overcomplicated, or done at the last minute?
- What decisions are made over and over that could use a stable rule or prioritized next action?
- Which information is scattered across email, calendar, notes, photos, documents, apps, chats, or memory?
- If LyfeOS worked extremely well six months from now, what would feel materially easier?

Do not limit discovery to what the user already names as an “AI feature.” Infer candidate domains and explain why they may help.

## 2. Existing systems and capability discovery

Before designing replacements, ask what already exists and inspect reachable sources:
- calendars, email, Drive/files, Sheets/databases, task apps, finance connections;
- fitness/wearable/activity apps;
- recipe/meal-planning collections;
- school/work systems and documents;
- Git repositories and existing automation;
- other connected plugins/apps relevant to the user's answers.

Use `CAPABILITY_DISCOVERY.md`. Do not claim arbitrary old ChatGPT conversations are globally searchable. If prior-chat information is inaccessible, provide an ingestion path rather than silently discarding it.

## 3. Work and context-mode gate

Ask explicitly: **Do you regularly work away from home, sleep away from home for work, rotate worksites, or live/work from a vehicle or field location?** Also learn what the user does for work, their **exact job title**, actual duties, schedule, and work environment.

If no, mark HOME/ROAD bypassed unless another context split clearly helps.

If yes, interview:
- solo/team arrangement, shift, sleep pattern, and travel rhythm;
- departure/return evidence and irregular-dispatch behavior;
- devices, connectivity, storage, space, and equipment away from home;
- tasks/routines that work anywhere, only at home, only away, or need variants;
- appointments/weather/route/pay information that matters away;
- paid miles/routes/per diem/commission or other work units only when relevant.

Recommend natural contexts such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, or custom labels. Driving/trucking is only one branch. Context never redefines canonical scheduling time.

## 4. Hobbies, recreation, travel and vacations

Ask what the user actually enjoys doing and what routinely surrounds those activities: hiking, camping, sports, gaming, photography, cooking, automotive work, crafting, volunteering, travel, or other interests.

For relevant hobbies discover:
- recurring preparation/checklists/equipment;
- reservations, permits, weather, route or destination research;
- maintenance/consumables;
- skill/progression goals;
- photos/documents/reference material worth organizing;
- trip/vacation ideas versus committed plans;
- whether Calendar/maps/weather/travel tools would materially reduce planning work.

Do not manufacture a project-management system around a hobby that the user wants to keep spontaneous.

## 5. Personal accountability and recurring routines

Offer this for exercise, household routines, creative practice, reading, paperwork, maintenance, or another recurring commitment. Accountability means evidence plus useful prompting, not scolding.

For each routine capture purpose, frequency, preferred windows, time/component blocks, contexts, resources, normal and **minimum viable version**, completed/partial/skipped/rescheduled definitions, check-in/anti-nag rule, miss policy, progression/review rule, and desired evidence.

For **Exercise / fitness**:
- support cardio, strength, mobility/stretching, yoga, warm-up/cool-down, or user-defined blocks;
- support progression from user-selected evidence such as consistency, duration, reps/sets, load, exercise variation, or yoga/mobility skill progression;
- distinguish home and away versions when equipment/space differs;
- if a fitness/wearable integration is available, offer it as optional evidence rather than requiring manual duplication;
- never invent medical restrictions, diagnoses, calorie targets, or unsafe progression.

Do not infer completion from silence.

## 6. Education and study coach

Offer this for school, certification, professional development, language learning, or another structured track.

Capture institution/program/course, source locations, verified assignments/exams/projects/deadlines, current state, weekly target, study methods, **home versus away/on the road** options, offline/download needs, realistic windows, accountability behavior, and optional Calendar Projection.

Next-action rule:
1. read verified deadlines and prerequisites;
2. choose the smallest actionable next step;
3. favor urgent/high-impact work without skipping prerequisite learning;
4. fit current context/time when known;
5. keep context-incompatible work in backlog;
6. update progress only from user confirmation or connected evidence.

The system may explain, quiz, summarize user-provided material, plan study, and review work. It must not fabricate submissions, attendance, grades, citations, or proof of work and must not encourage academic dishonesty.

## 7. Food, recipes and meal planning

Always make this option discoverable. Ask: **Do you want help with meal planning, recipes, grocery planning, pantry/freezer use, leftovers, cooking logistics, or reducing food cost/waste?**

If yes, capture only useful preferences:
- household/serving pattern and cooking frequency;
- foods/cuisines liked or disliked;
- dietary constraints/preferences the user explicitly supplies;
- typical time/effort budget and cooking equipment;
- repeat-favorite versus novelty preference;
- leftovers/batch cooking/freezer strategy;
- grocery cadence and stores when operationally useful;
- home/away/camping/travel variants;
- cost or nutrition goals only when the user wants them and evidence supports them.

Before starting over, search accessible existing recipes, meal plans, notes, files, Drive material, and current conversation evidence. Reconcile into one canonical recipe/meal-planning library with provenance. A meal plan may create shopping intent; purchase history remains separate.

## 8. Household, administration, projects and appointments

Explore useful areas only:
- chores/seasonal maintenance and grouped errands;
- bills/subscriptions/trials/paperwork;
- shared household responsibilities;
- active projects with milestones/next actions;
- renewals/registrations/documents;
- appointments/reservations and how reminders arrive.

For appointments ask whether the user wants email-derived appointment reconciliation. If yes, define which senders/event classes count, the target calendar, reminder defaults, tentative/revision/cancellation behavior, confidence threshold, and ambiguity policy.

A retired or schedule-flexible user may still benefit from appointments, renewals, documents, household projects, exercise, hobbies, travel, and selected medical-event organization. Never assume retirement means inactivity or that medical tracking is wanted.

## 9. Appointment email → Calendar verification contract

When the user explicitly enables an appointment class:
1. read the complete relevant message/evidence;
2. dedupe against canonical appointment/source identity and existing Calendar Projection;
3. extract only evidence-backed title/provider/location/date/time/timezone/source fields;
4. create or update the single linked calendar event;
5. configure the user's chosen calendar reminders;
6. read the event back and verify event ID, calendar, title, time/timezone, reminder policy, and source linkage;
7. write/verify the canonical projection/reconciliation state;
8. only then mark the appointment source reconciled.

Revision/cancellation mail updates/cancels the same event. Low-confidence or conflicting evidence asks the user. Do not create one ChatGPT Scheduled Task per appointment; event-specific reminders belong in Calendar, while ChatGPT uses consolidated brief/accountability dispatchers.

For medical appointments, default to minimum necessary calendar detail and never infer diagnosis, treatment, or medical advice.

## 10. Information, assets and knowledge

Ask what the user repeatedly searches for: receipts, manuals, work/school documents, warranties, recipes, policies, reference PDFs, photos, vehicle/equipment specs, or other evidence.

For selected classes define authoritative storage, naming/index fields, immutable identity where appropriate, provenance, dedupe, retention, and how later queries return canonical links/source sections.

## 11. Communication and email

Ask which senders/domains matter, what is actionable, what should be grouped with appointments/orders/projects, what must never be archived automatically, and whether drafting assistance is wanted. External sending is approval-gated.

## 12. Calendar, time and scheduler evidence

Ask which facts deserve Calendar Projection versus brief/task visibility only. Candidate classes include appointments, work travel, deadlines, deliveries, study/routines, bills/trials, maintenance, reservations, and selected tasks.

For Scheduled Tasks verify canonical VEVENT/TZID/local time, exactly one intended enabled dispatcher, timing mode, expected **notification** state, no **duplicate** jobs, and a subsequent **actual firing**/Run Log. A `default_timezone` label is authoritative only when the **provider contract** defines it as persistent task execution state.

## 13. Money and purchase organization

Ask whether the user wants searchable receipts/orders, active shopping intent, account transaction reconciliation, subscriptions/trials, reimbursements/shared purchases, budgets, or reports.

Keep concepts separate: shopping intent is not purchase history; merchant refund is not household reimbursement; expected charge is not posted charge; one purchase total is never counted once per category/asset.

## 14. Git lineage and portable feature sharing

Read `PERSONAL_FORK_LIFECYCLE.md`. Ask which user-owned repository will hold durable deployment source, verify its upstream provenance, visibility, read/write capability, standing versioning authority, and merge policy.

First boot must produce a coherent Git checkpoint after provisioning approval. When later customization creates a coherent reusable feature, ask whether the user wants to make it available to other people. Sharing is opt-in and sanitization/test gated; never publish personal configuration/state automatically.

## 15. Brief design and anti-noise rules

Ask what deserves interruption versus digest, preferred length, priority model, what stays visible until done, what disappears after acknowledgement, which sections vary by context, and degraded-module wording.

Every brief should answer some combination of: what changed, what needs action, what is next, and **what to do next** when the user asks for prioritization.

## 16. Final synthesis before provisioning

Before the initial write bundle, summarize:
- canonical timezone and context model;
- work pattern, major hobbies/travel patterns, and top problems;
- existing authorities/capabilities discovered;
- selected and deferred modules;
- routines/study/meal-planning/appointment behavior where selected;
- authoritative apps/data and minimum dependency set;
- schedules/notifications and scheduler evidence plan;
- Git fork/upstream/versioning/share policy;
- destructive/external-send boundaries;
- remaining ambiguity.

Then show the Minimum Useful Setup. Provision only after explicit approval, verify every write, commit/push the coherent user deployment checkpoint, and keep optional expansion available without requiring a rebuild.