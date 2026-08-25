# MIRROR (Institutional-Experimental)

This is the sanitised institutional experiment channel for **MIRROR**. **MIRA** is the assistant surface when the approved runtime supports it.

Begin with [`starter/ENTERPRISE_PILOT.md`](starter/ENTERPRISE_PILOT.md), then select an approved provider lane. End users do not need a local shell, Git client, or personal cloud account.

## Hard boundary

This Git repository stores source, schemas, non-secret configuration, and synthetic fixtures only: **no PHI/PII in Git**. Do **not** put PHI, PII, VA-sensitive data, clinical records, employee records, receipts, email bodies, authority IDs, or mutable operational state in Git even though the repository is private.

Demonstrations use generic or synthetic personas. Sensitive runtime use is blocked until the accountable organization confirms the exact approved runtime, ATO/approval scope, identity, purpose, storage, connector actions, retention, and audit controls.

This is a generated distribution, not an independent source of truth. It uses the same portable code as Personal-Production and Personal-Experimental. `DEPLOYMENT_CHANNEL.json` pins the canonical source revision.

The historical title `Life Planner (Institutional-Experimental)` remains a compatibility identifier until the branded repository migration is remotely verified.
