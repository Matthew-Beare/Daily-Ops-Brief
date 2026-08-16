# Life-Ops Starter

**NON-PRODUCTION:** this directory is a quarantined, forkable discovery scaffold. The production Daily Ops Brief does not import it, render it, schedule it, or use its policy. Changes here cannot alter the production system unless a feature is deliberately extracted, reviewed, and committed there later.

## First run

Open `START_HERE.md` and conduct the interview one question at a time. The first three questions discover:

1. how the person currently uses AI;
2. what they have trouble doing, remembering, deciding, or organising;
3. what could usefully be automated, summarised, tracked, or placed in a brief.

The interview then loads only relevant modules. Doctor-appointment logistics for one user, hiking conditions for another, and meal planning for a third are separate feature candidates—not mandatory starter behaviour.

## Isolation guarantees

- No production automation invokes this directory.
- The production skill renderer copies only the root `skill/` directory.
- The production policy fingerprint excludes `starter/`.
- No live Sheet IDs, Gmail IDs, email bodies, appointments, tasks, health records, VA data, credentials, or personal configuration belong here.
- `config/profile.example.json` contains shape and placeholders only. A fork creates `config/profile.local.json`, which must remain ignored.
- A starter feature is inert until its owner chooses authorities, permissions, schedules, schemas, and tests in their own fork.

## When another user is ready

1. Create a clean `Life-Ops-Starter` repository from this directory so the production repository history is not copied.
2. Keep that upstream private until its full history passes a privacy audit.
3. Have the new user fork `Life-Ops-Starter`.
4. Run `START_HERE.md` in their fork.
5. Commit only sanitized structure and portable features. Keep real interview answers and operational configuration in the user’s private fork.
6. Use `SHARED_FEATURE_WORKFLOW.md` for cross-fork contributions.

## Validate

From this directory:

```bash
python3 tools/validate_feature_manifest.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```
