# Red Hat / SELinux deployment security

MIRA // MIRROR supports two distinct Linux roles and they must not be confused.

## Desktop client

The native desktop client is packaged as AppImage, Debian `.deb`, and RPM.

- Ubuntu/Debian: native Tauri desktop target.
- RHEL 9 and compatible desktop distributions: RPM target, subject to final package/install testing with the required WebKitGTK runtime.
- RHEL 10: **do not advertise the current native Tauri GUI as supported.** RHEL 10 removed WebKitGTK, which the current Tauri Linux webview depends on. The MIRROR server remains a valid RHEL 10 target; a future RHEL 10 native GUI requires a different supported webview strategy.

## MIRROR server on RHEL

Prefer rootless Podman for a single-node or pilot server.

Security baseline:

1. Run the MIRROR container as a non-root application user. The shipped image uses UID 10001 and must not be changed to root merely to fix permissions.
2. Run the container rootless where practical. Do not use `--privileged`.
3. Keep persistent state in a dedicated host directory or volume. With SELinux enforcing, use a private SELinux container relabel such as `:Z` for a host bind mount that belongs only to this container. Do not disable SELinux to make the mount work.
4. Publish only the MIRROR listener that is actually required. Do not expose the SQLite database file or evidence directory over a file share as an API substitute.
5. Put TLS in front of remote deployments. The starter's plain HTTP localhost examples are not an internet deployment design.
6. Keep `MIRROR_ACCESS_TOKEN`, OAuth credentials, signing material, provider refresh tokens, and future GitHub App private keys out of Git and out of container images. Supply them through a secret mechanism appropriate to the deployment.
7. Keep `MIRROR_AUTH_MODE=required` in customer deployments. `development` or `disabled` is for isolated development only.
8. Keep outbound provider access explicit. Google, Microsoft, Home Assistant, GitHub, update feeds, and future enrichment providers should be individually configurable rather than granting the service arbitrary host access.
9. Keep the host firewall enabled and restrict administrative access separately from ordinary client access.
10. Back up canonical state and evidence together. Verify restore/readback using immutable UUID relationships rather than treating a copied SQLite file as sufficient proof.

## SELinux

SELinux is a security boundary, not an installation bug.

- Use container-aware labels for bind-mounted state.
- Prefer a private `:Z` relabel when only MIRROR should use the directory.
- Do not tell customers to run `setenforce 0` or permanently disable SELinux.
- If a production deployment needs host resources outside normal container policy, create the smallest explicit policy needed and audit the denial. Do not widen the entire host policy to make one integration convenient.
- Enterprise deployments may use a generated/custom SELinux policy after representative workload testing, but that policy must be source-controlled and reviewed separately from mutable runtime data.

## Container example

A production installer or deployment manager should generate the exact command/config rather than asking a nontechnical user to type it. Conceptually the deployment is equivalent to a rootless container with a dedicated persistent data mount, the private SELinux label, required secrets, and one published HTTPS-fronted service port.

## Update security

Binary updating and source reconciliation are separate controls.

- Customer binaries/packages must come from a verified release channel.
- Package/update signing keys must never be stored in the public repository.
- A GitHub source update must pass the repository's tests and reconciliation gates before it becomes a binary release.
- A custom-feature collision fails closed and requires review. It is never resolved by discarding the user's branch or policy.

## Pilot exit criteria

Before advertising Red Hat support to customers, prove at minimum:

- RPM builds in CI.
- Install/start/uninstall on a representative RHEL 9-family desktop.
- Rootless Podman MIRROR server start, health, persistence, restart, backup, restore, OAuth callback, and client read/write/readback with SELinux enforcing.
- No requirement for `--privileged`, SELinux disablement, or world-writable state directories.
- RHEL 10 server deployment separately from the currently unsupported RHEL 10 native Tauri GUI.
