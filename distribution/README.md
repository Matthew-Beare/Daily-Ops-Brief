# MIRA | M.I.R.R.O.R. release channels

M.I.R.R.O.R. uses one canonical source and two generated experimental distributions. **M.I.R.R.O.R. is the reality layer; MIRA is the intelligence layer.** Generated distributions are deterministic products of one exact canonical source revision.

All three GitHub repositories are public onboarding surfaces. Public visibility is for installation, inspection, and contribution. It never authorizes live personal, regulated, or operational data in Git.

| Human channel | Repository | Visibility | Purpose |
|---|---|---|---|
| M.I.R.R.O.R. Personal-Production | `MIRA-Personal-Production` | Public | Sole canonical source |
| M.I.R.R.O.R. Personal-Experimental | `MIRA-Public-Experimental` | Public | Sanitised browser-first personal onboarding distribution |
| M.I.R.R.O.R. Institutional-Experimental | `MIRA-Institutional-Experimental` | Public | Sanitised institutional pilot source/config with no live regulated data |

## Same-code invariant

All three channels use the **same portable application code from the same canonical source revision**. No channel may carry its own feature fork. Differences are limited to deployment policy, approved runtime/provider configuration, data classification, and mutable external state.

Separate repositories exist for onboarding and distribution boundaries, not because they are separate products.

## Audit boundary

The canonical Personal-Production repository is the source of truth and its CI performs the full reachable-history public-source audit with `scripts/audit_public_source.py . --history`.

Generated distribution repositories do **not** reinterpret their own pre-promotion Git history as release payload. Their CI audits the **current generated tree** with `scripts/audit_public_source.py .`, validates the immutable `DEPLOYMENT_CHANNEL.json` hash manifest, and verifies that the tree is pinned to one exact canonical source revision. That source revision has already passed the canonical full-history audit before promotion.

This split is deliberate. Renamed or previously bootstrapped distribution repositories may contain historical commits that are not part of the generated release. Rewriting that history would violate the no-force-push release contract and would provide no additional protection for the immutable current payload. Any current-tree leak, payload drift, wrong source revision, or manifest mismatch still fails distribution CI.

## Promotion transaction

1. Make and test a coherent change in Personal-Production.
2. Commit and push it without force.
3. Require canonical CI, including the reachable-history audit, to be green.
4. Build each distribution from that exact 40-character source commit.
5. Run generated-tree source/privacy audits and distribution validation before publishing.
6. Publish the exact generated trees without manual drift.
7. Perform remote readback of repository identity, visibility, `main` head, manifest, and source revision.
8. Require each distribution's current-tree CI to be green before calling promotion complete.

**Green CI is required at both the canonical-source and generated-distribution boundaries before a release is complete.**

Never treat a generated distribution as an independent source of truth. Fix the canonical source and promote again.

## Data boundary

Public Git contains portable source, policy, schemas, migrations, synthetic fixtures, and non-secret configuration only. It contains no PHI/PII, credentials, private provider evidence, or mutable operational state. Regulated or private data may exist only in the exact approved runtime and storage for that purpose.
