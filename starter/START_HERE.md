How do you currently use AI?

# Life Assistant Discovery Interview

Use this script to design a personal operations assistant around one person’s actual life instead of cloning somebody else’s habits. Run it conversationally, one question at a time. Do not dump the entire questionnaire on the interviewee.

## Interviewer rules

- Ask the opening discovery sequence before offering tools or feature pitches.
- Ask one primary question at a time. Use at most one short follow-up when an answer is materially ambiguous.
- Accept “skip,” “not sure,” and “not now.” Record uncertainty instead of inventing an answer.
- Separate permanent policy from mutable state. Preferences and boundaries belong in versioned configuration; current tasks, meals, trips, workouts, and appointments belong in the private operational database.
- Never request passwords, recovery codes, API keys, patient data, personnel records, private case details, or real examples containing protected information.
- Challenge feature ideas that cost more attention than they save. Every proposed feature needs a trigger, authoritative input, useful output, failure behaviour, and success test.
- End each phase with a two-sentence readback and ask whether it is accurate.
- Stop when the minimum viable assistant is defined. Uncertain extras become backlog items, not launch requirements.

## Opening

Say this, then ask the three questions one at a time:

> I’m going to design this around your life instead of assuming you need somebody else’s features. I’ll ask one question at a time and finish with a small first version plus a backlog.

1. How do you currently use AI?
2. What do you regularly have trouble doing, remembering, deciding, or organising?
3. Which parts of that would you want automated, summarised, tracked, or placed into a brief?

Do not infer needs from age, job, hobbies, or another person’s setup. Use the answers to choose only the relevant modules below.

## Phase 1 — Outcomes and friction

Ask in this order after the opening sequence, skipping questions already answered:

1. What would have to be easier after 30 days?
2. What three recurring chores, decisions, or bits of mental bookkeeping annoy you most?
3. What do you already handle well and not want automated?
4. What is the most expensive failure: forgetting something, being late, wasting money, overcommitting, missing recovery, eating badly, or something else?
5. What must the assistant never do without asking first?

Read back the desired outcomes, top friction points, and prohibited actions.

### Branch from the actual problem

Convert each stated problem into a candidate capability before asking domain questions.

Example: if a user says they lose track of doctor appointments, do not clone another person’s shipment or travel system. Explore an appointment feature: authoritative calendar or portal, reminder window, preparation checklist, transportation needs, what may appear in a brief, what health detail must remain private, and what happens when the calendar is unavailable.

Example: if another user says meal planning burns time, explore household size, nutrition constraints, budget, shopping, prep capacity, leftovers, and grocery-list output. If they never mention hiking or workouts, skip those modules entirely.

## Phase 2 — Rhythm, attention, and brief design

1. What timezone should permanently govern schedules?
2. What does a normal workday, day off, and any other recurring day type you mentioned look like?
3. When are you actually willing to read a brief or answer a prompt?
4. Would one daily brief, two short briefs, or event-triggered prompts fit best?
5. What deserves an interruption outside the brief?
6. How short must the normal output be before you will consistently read it?
7. Which channels are acceptable: ChatGPT only, email, calendar, or something else?

Convert answers into exact schedules, named timezones, interruption thresholds, and maximum normal brief length.

## Phase 3 — Personal administration

1. Which calendars, inboxes, lists, or spreadsheets currently contain your real commitments?
2. Which one should be authoritative for appointments and which for tasks?
3. Which email categories deserve attention: bills, subscriptions, orders, travel, healthcare, employment, security, or others?
4. May routine processed mail be archived automatically?
5. Which email actions always require approval? Deletion must default to explicit approval.
6. Do you want shipment tracking, appointment preparation, bill reminders, subscription review, or household inventory?
7. What recurring life-admin tasks are most likely to be forgotten?

Record each source of truth and a precise read/write/archive/delete boundary.

## Conditional module — Regulated or sensitive work

Use this module only when the interviewee wants help with an employer, healthcare, government, legal, financial, or other regulated workflow.

Until the interviewee identifies an employer-approved AI environment and the exact governing rules, treat the assistant as personal and work-adjacent only. Protected records, credentials, internal documents, screenshots, and nonpublic email are forbidden inputs. Discuss categories of work and generic workflows without requesting real records or identifiers.

For a VA employee, Veteran, patient, employee, claim, payment, medical, personnel, credential, internal-document, screenshot, and nonpublic email data remain blocked unless she identifies documented VA approval for the specific tool and data type. Ask:

> Which AI tools and data types has your employer explicitly approved for your role, and where is that approval documented?

If the answer is unknown, record `Work integration: blocked pending documented approval` and continue with non-sensitive use cases such as personal scheduling, generic checklists, or general writing practice.

## Conditional module — Appointments and healthcare logistics

Use this module when the interviewee mentions appointments, medical administration, forgetting dates, transportation, preparation, or follow-up tasks. Do not request diagnoses, medical records, insurance identifiers, or portal credentials.

1. Where are appointments authoritative: a calendar, patient portal, paper card, email, or another source?
2. How far ahead should appointments appear in a brief?
3. What preparation is useful: forms, questions, medication list reminder, fasting instruction reminder, documents, transportation, or arrival time?
4. Which details may appear in the brief, and which must remain private or hidden?
5. Should confirmations suppress repeat prompts without being displayed?
6. What counts as urgent: a new appointment, cancellation, reschedule, missing transportation, or incomplete preparation?
7. May the assistant write calendar reminders, or only suggest them for approval?
8. What should happen when the calendar or portal is unavailable?

The feature should manage logistics and reminders, not interpret medical information.

## Conditional module — Hiking

Ask only questions relevant to her hiking style:

1. What kinds of hikes do you do: local day hikes, long day hikes, backpacking, winter hiking, solo, group, or mixed?
2. What regions and seasons are typical?
3. What information changes a go/no-go decision: forecast, lightning, heat, snow/ice, wildfire/smoke, stream crossings, trail closures, daylight, or road access?
4. Which official or trusted trail/weather sources do you already use?
5. What lead time is useful for planning and for a final conditions check?
6. Should a trip record include route, trailhead, start time, turnaround time, expected return, party, gear checklist, and emergency contact plan?
7. What conditions should trigger an explicit warning rather than a normal summary?
8. Should completed hikes feed mileage, training load, gear maintenance, or a trail journal?

Do not imply that an assistant replaces navigation, emergency communications, official closures, or personal judgement. Define hiking features as decision support with source and timestamp visibility.

## Conditional module — Strength training

1. What is the primary goal: strength, hypertrophy, general fitness, sport support, or a mixture?
2. What program or progression method are you currently following?
3. How many sessions per week are realistic, and what equipment is available?
4. What does she want recorded: exercises, sets, reps, load, RPE/RIR, pain flags, bodyweight, or personal records?
5. Should the assistant merely log and summarize, or also suggest sessions and progression?
6. What rules govern missed sessions, deloads, exercise substitutions, and fatigue?
7. Are there injuries, clinician restrictions, or movements that must be treated as hard constraints?
8. Which weekly trend would be useful without becoming obsessive?

Keep medical diagnosis and rehabilitation outside scope unless a qualified clinician’s explicit plan is being transcribed without reinterpretation.

## Conditional module — Meals and groceries

1. Who is being fed, and how many meals or servings are needed?
2. What are the goals: convenience, cost, protein, calories, macros, dietary quality, variety, or weight change?
3. What allergies, intolerances, ethical restrictions, hard dislikes, and medical constraints apply?
4. What calorie or macro targets are already established, and who established them?
5. What is the weekly grocery budget and preferred stores?
6. How many cooking sessions are realistic, and how much leftover repetition is acceptable?
7. What appliances, freezer space, pantry staples, and work-lunch constraints matter?
8. Should the output include a menu, recipes, prep order, consolidated grocery list, estimated cost, and leftover plan?
9. What foods or plans have repeatedly failed, and why?

Make the system optimize around adherence and actual cooking capacity, not theoretical meal-plan perfection.

## Phase 7 — Permissions, privacy, and failure behaviour

1. Which connectors may be read, and which may be written?
2. Which actions may happen automatically, which need approval, and which are forbidden?
3. What data may be retained, and for how long?
4. What should happen when a connector, database, or source is unavailable?
5. Should the assistant show uncertainty and source timestamps? Default to yes for safety, money, travel, and work-related decisions.
6. Who may access the private deployment repository and operational data?
7. Which parts are safe to extract into the shared feature repository?

Default failure behaviour is explicit degradation: report the missing authority, do not substitute memory, and do not claim a write succeeded when it did not.

## Phase 8 — Select the first release

List every candidate feature, then ask her to rank them by value and effort. Choose no more than three for version 1.

For each selected feature, obtain:

- user trigger;
- authoritative inputs;
- expected output;
- allowed mutations;
- approval boundary;
- failure output;
- one example that should succeed;
- one example that must be rejected or escalated;
- measurable 30-day success criterion.

Good first-release candidates for this profile may include a compact daily brief, meal-plan and grocery-list generation, workout logging/weekly summary, or an explicitly armed hiking conditions check. These are suggestions only; her ranked problems decide the release.

## Final readback and deliverables

End with:

> Here is what I think you want, what the first release will do, what it will not do, and what still needs a decision. Stop me anywhere I got it wrong.

Produce these artifacts in her private deployment repository:

1. `docs/DISCOVERY.md` — goals, rhythms, boundaries, and unresolved questions.
2. `config/profile.example.json` — sanitized configuration shape with placeholders only.
3. `config/profile.local.json` — real private values, ignored by Git.
4. `docs/MVP.md` — selected features and acceptance tests.
5. `docs/DATA_BOUNDARY.md` — allowed, approval-required, and forbidden data/actions.
6. `features.lock.json` — installed shared feature IDs, versions, and source commits; no personal data.

Do not build until she approves the readback and the data boundary.
