# MIRA | MIRROR release channels

MIRROR uses one canonical source and two generated experimental distributions. **MIRA is the assistant; MIRROR is the system.** Generated distributions are deterministic products of one exact canonical source revision.

| Human channel | Branded target | Current compatibility repository ID | Visibility | Purpose |
|---|---|---|---|---|
| MIRROR Personal-Production | `MIRROR-Personal-Production` | `Life-Planner-Personal-Production` | Private | Sole source of truth |
| MIRROR Personal-Experimental | `MIRROR-Personal-Experimental` | `Life-Planner-Public-Experimental` | Public | Sanitised browser template |
| MIRROR Institutional-Experimental | `MIRROR-Institutional-Experimental` | `Life-Planner-Institutional-Experimental` | Private | Sanitised institutional pilot source/config |

The compatibility repository IDs remain in the machine release contract until the branded repositories actually exist and their identity, visibility, branch, commit, and CI are remotely read back. Do not point users at repository names that have not been created.

## Same-code invariant

All three channels use the **same portable application code from the same canonical source revision**. No channel may carry its own feature fork. Differences are limited to repository visibility, deployment policy, approved runtime/provider configuration, data classification, and mutable external state.

Separate repositories exist for security and distribution boundaries, not because they are separate products.

## Promotion transaction

1. Make and test a coherent change in Personal-Production.
2. Commit and push it without force.
3. Build each distribution from that exact 40-character source commit.
4. Run distribution validation, source/privacy audits, and portable starter tests.
5. Publish the exact generated trees without manual edits.
6. Perform remote readback of repository identity, visibility, `main` head, manifest, and source revision.
7. Require green CI before calling promotion complete.

Never patch a distribution repository by hand. Fix the canonical source and promote again.

## Data boundary

Git contains source, policy, schemas, migrations, synthetic fixtures, and non-secret configuration. It contains no PHI/PII or mutable operational state. Regulated data may exist only in the exact approved runtime and storage for that purpose.
