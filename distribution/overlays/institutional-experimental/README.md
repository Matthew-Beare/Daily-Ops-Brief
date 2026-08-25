# Life Planner (Institutional-Experimental)

This is the sanitised institutional experiment channel for Life Planner. It supports controlled evaluation in corporate, government, health-care and other locked-down environments.

Begin with [`starter/ENTERPRISE_PILOT.md`](starter/ENTERPRISE_PILOT.md), then select the approved provider lane in [`starter/PROVIDER_ONBOARDING.md`](starter/PROVIDER_ONBOARDING.md). End users do not need a local shell, Git client or personal cloud account.

## Hard boundary

This Git repository stores source, schemas, non-secret configuration and synthetic fixtures only: no PHI/PII in Git. Do **not** put PHI, PII, VA-sensitive data, clinical records, employee records, receipts, email bodies, authority IDs or mutable operational state in Git—even though this repository is private.

Demonstrations use generic or synthetic personas and scenarios. Never embed real viewer identities, private disclosures, relationships, or inferred motives in fixtures, prompts, configuration, or presentation material.

Sensitive runtime use is blocked until the accountable organization confirms the exact approved runtime, ATO/approval scope, identity, purpose, storage tenant/resources, connector actions, retention and audit controls. Reachability, a product name or a generic compliance claim is not approval.

This is a generated distribution, not an independent source of truth. `DEPLOYMENT_CHANNEL.json` pins its canonical source revision. Changes must be made and tested in Personal-Production, rebuilt, audited, promoted, read back and accepted by green CI.
