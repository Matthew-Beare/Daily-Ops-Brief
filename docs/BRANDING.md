# Product naming

## Current working name

**Life Planner** is the owner-selected working name for the product family and non-technical onboarding.

It is deliberately descriptive rather than presented as a cleared trademark. Before a commercial launch, perform a proper trademark/domain/app-store clearance for the final distinctive name. A web search is not legal clearance.

## Repository-channel names

- Human title: **Life Planner (Personal-Production)**; GitHub slug: `Life-Planner-Personal-Production`.
- Human title: **Life Planner (Public-Experimental)**; GitHub slug: `Life-Planner-Public-Experimental`.
- Human title: **Life Planner (Institutional-Experimental)**; GitHub slug: `Life-Planner-Institutional-Experimental`.

GitHub repository slugs cannot contain spaces or parentheses, so the human titles and slugs deliberately differ. Personal-Production is the private canonical source. Public-Experimental and Institutional-Experimental are generated distribution channels.

## Per-user name

Every personal deployment asks the owner what their own system should be called. That private name belongs in mutable deployment configuration/state and does not rename or contaminate the public upstream.

## Legacy compatibility identifiers

The current reference deployment may still contain `LyfeOS Control Cycle`, `Daily Ops Brief` or `Personal Ops Planner` as an automation title, policy key, path, historical evidence label or compatibility alias. Those are compatibility identifiers, not the current product name.

Do not rename the live automation, provider resources, Drive folders, schema keys, or historical references as a cosmetic bulk edit. Migrate each live identifier only in a bounded transaction with dependency inspection, provider readback, rollback, and observed scheduled execution. Source documentation should label such identifiers as legacy when confusion is possible.
