# MIRA // MIRROR 1.0 security review

## Status

This document records the internal engineering security review and the evidence required before customer pilot and general availability.

**Independent external security review is not complete.** The system must never label an internal model/developer review as an external penetration test.

## Runtime boundaries

### ChatGPT + Google native

Normal users do not expose a MIRROR server. MIRA operates inside ChatGPT using user-approved Google Workspace surfaces and user-owned Google authority files. Security depends on Google/ChatGPT account security, granted connector permissions, authority-file ACLs, provenance rules, and MIRA's scoped workflow contract.

### Hosted/native clients

A remotely reachable MIRROR service must:
- sit behind HTTPS;
- keep port 8765 private to the container network;
- use a bootstrap admin secret only for administration/enrollment;
- issue per-device revocable credentials after one-time enrollment;
- never persist plaintext device tokens in the database;
- encrypt provider OAuth tokens at rest;
- restrict CORS to configured official origins;
- use signed short-lived links for protected evidence/labels;
- preserve idempotency/readback on canonical writes;
- run non-root with capabilities dropped and no-new-privileges;
- keep SELinux enforcing on RHEL deployments.

## Update threat model

Threats: malicious release asset, compromised mirror, stale vulnerable client, downgrade, update/source collision, stolen signing key.

Controls:
- source updates reconcile through Git and normal CI rather than rewriting user code in place;
- conflicts fail closed and preserve current source;
- production Windows/Linux desktop updater uses Tauri signature verification, which cannot be disabled;
- Windows installer/application uses Authenticode when production secrets are present;
- Android APK/AAB production signatures are verified in the release workflow;
- Linux release artifacts have a signed SHA-256 manifest in addition to Tauri AppImage update signatures;
- production publication refuses to run when required signing identities are absent;
- updater endpoint is HTTPS-only;
- private signing keys are GitHub secrets and are never committed.

Key compromise requires release-key rotation/recovery planning before GA. Keep offline backups of production private keys in an access-controlled recovery location.

## Inventory / receipt threat model

External product/retailer results are untrusted candidate evidence. They never become canonical solely because a page or search result contains similar words. Receipt reconciliation auto-applies only unique high-confidence matches from an official retailer/manufacturer source. Identity collisions, ambiguous lines and total mismatches remain open.

Serials, GTINs, retailer SKUs, QR values and RFID aliases never replace immutable asset UUID identity.

## Physical-radio privacy

NFC/HF enrollment is user-initiated foreground reading. Passive UHF observations from external readers are presence evidence and do not silently relocate assets. BLE proximity is opt-in and should prefer stable advertised service/manufacturer identifiers rather than rotating MAC addresses. UWB is opt-in precise ranging, not passive inventory magic.

## Automated evidence

Required on release candidate:
- canonical unit/contract tests;
- Docker end-to-end smoke;
- Android build/signature-status validation;
- Windows/Linux package builds;
- Visual QA screenshots and responsive assertions;
- Python dependency audit;
- Python high-severity static security scan;
- Rust advisory audit;
- Node tooling dependency audit;
- private-key and token-literal checks;
- repository privacy/public-source audit.

## Independent external review blocker

Before MIRA // MIRROR is represented as GA/customer-production hardened, commission an independent review covering at least:
1. OAuth and account-linking flows.
2. Device enrollment/revocation and credential storage.
3. Authorization boundaries and IDOR tests for assets/evidence/receipts.
4. Signed update channel and signing-key compromise scenarios.
5. SSRF/URL handling in provider and retailer enrichment paths.
6. File upload/media handling and content-type confusion.
7. SQLite/PostgreSQL migration and transaction integrity.
8. GitHub App permission scope and update-conflict workflow.
9. Google-native authority ACL/provenance and malicious spreadsheet/receipt input.
10. Android WebView/JavaScript bridge, NFC/BLE permission boundaries and exported components.

Any Critical/High finding blocks GA. Medium findings require remediation or a documented time-bounded acceptance by the product owner. Re-test fixes before closing the external-review gate.
