# Life Planner release channels

Life Planner uses one canonical repository—the sole source of truth—and two generated distribution channels.

| Channel | Repository | Visibility | Purpose |
|---|---|---|---|
| Personal-Production | `Matthew-Beare/Life-Planner-Personal-Production` | Private | Sole source of truth, full reference deployment, release tooling and tests |
| Public-Experimental | `Matthew-Beare/Life-Planner-Public-Experimental` | Public | Sanitised, provider-neutral browser template using public or synthetic data only |
| Institutional-Experimental | `Matthew-Beare/Life-Planner-Institutional-Experimental` | Private | Sanitised source/configuration for approved institutional pilots; no PHI/PII or operational records in Git |

Separate repositories are justified because visibility and data-handling boundaries differ. They are not independent forks. Public and institutional trees are deterministic products of the exact canonical commit recorded in `DEPLOYMENT_CHANNEL.json`.

## Promotion transaction

1. Make and test a coherent change in Personal-Production.
2. Commit and push it without force.
3. Build each distribution from that exact 40-character source commit with `scripts/build_distribution.py`.
4. Run the distribution validator, source/privacy audits and portable starter tests against each fresh output.
5. Publish the exact generated trees to the matching repositories without manual edits.
6. Perform remote readback of repository identity, visibility, `main` head, manifest and source revision.
7. Require green CI before calling the promotion complete.

If a distribution needs a change, fix the canonical source and promote again. Never patch a distribution repository by hand: that creates an unreviewed fourth truth.

## Data boundary

Git contains source, policy, schemas, migrations, synthetic fixtures and non-secret configuration. It contains no mutable personal, employee, veteran, patient, customer or operational records. Regulated data may be processed only in the exact organization-approved runtime and storage covered for that purpose. A private repository is access control, not authorization to store PHI/PII.
