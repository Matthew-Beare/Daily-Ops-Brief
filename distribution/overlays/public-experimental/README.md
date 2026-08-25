# M.I.R.R.O.R. Personal-Experimental

**M.I.R.R.O.R.** means **Memory, Integration, Reality, Reconciliation, Observation, and Record**. **MIRA** is the **MIRROR Intelligence and Reasoning Assistant**. The deliberately forced acronym is a nod to Dennis E. Taylor's *Bobiverse* books and his fondness for a good forced acronym. M.I.R.R.O.R. is the reality layer that **holds the durable reflection of reality**; MIRA is the intelligence layer that talks with the user and reasons over that reflection.

This is the **public, sanitised** Personal-Experimental onboarding distribution. With user-approved integrations, M.I.R.R.O.R. can connect assets, finances, calendars, email, orders and shipments, receipts and refunds, appointments, tasks, medications and opt-in reminder schedules, documents and knowledge, travel/work context, meals, and custom skills.

> **Magic MIRA on the wall...**

Start with [`starter/QUICK_START.md`](starter/QUICK_START.md). The deeper provider and enterprise references remain available under `starter/`.

## Create and share new skills

Tell MIRA what recurring problem you want solved in ordinary language. MIRA should inspect existing capabilities, design the behavior and data boundaries, implement it on a feature branch, add tests and synthetic fixtures, verify it privately, and commit a coherent checkpoint.

Personal skills stay private by default. When a skill is coherent, MIRA asks exactly: **Do you want to make this feature available to other people?** If you approve, MIRA sanitizes the feature, removes personal identifiers and live data, declares dependencies and permissions, runs privacy/source tests, shows the exact public diff, and only then prepares an upstream pull request under explicit publication approval.

See [`starter/SHARED_FEATURE_WORKFLOW.md`](starter/SHARED_FEATURE_WORKFLOW.md).

## Distribution boundary

This public repository contains portable source and synthetic fixtures only. It is not the canonical source and must not receive secrets, live authority IDs, receipts, health records, employment records, or mutable user state. `DEPLOYMENT_CHANNEL.json` identifies the exact canonical source revision.

Personal-Experimental uses the same portable code as Personal-Production and Institutional-Experimental. Experimental means provider writes, schedules, and regulated-data use remain gated by exact runtime capability and readback.
