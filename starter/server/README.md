# mirror service

The mirror service is the provider-neutral server boundary used by the web, Windows, Linux, Android and CLI clients.

## Deployment choices

- **Google Workspace default**: Google Sheets is the structured-state authority and Google Drive is the evidence store. The service owns OAuth and provider tokens; clients never receive Google refresh tokens.
- **PostgreSQL**: set `MIRROR_STATE_BACKEND=postgres` and provide `MIRROR_POSTGRES_DSN`. Evidence can remain in the selected evidence adapter.
- **Docker**: `docker compose -f starter/server/compose.yaml up --build`. Docker is a deployment option, not a feature fork.
- **Cloud native**: the same container can run behind an HTTPS reverse proxy/load balancer with an external PostgreSQL/object store.

The service intentionally owns business behavior. Clients are interchangeable projections.

## Google OAuth

Google is the default provider lane. Configure a Google OAuth Web application with redirect URI:

`<MIRROR_PUBLIC_BASE_URL>/auth/google/callback`

The first browser sign-in requests only the scopes needed for profile, Sheets and Drive. Calendar/Gmail remain separate capabilities and should be added by a later incremental-consent transaction only when a feature requires them.

After OAuth, mirror provisions one Google spreadsheet and one Drive evidence folder if the owner approves provisioning. The resulting stable resource IDs are stored in the local encrypted metadata registry.

## Device pairing

Native clients never ask the owner to paste bearer tokens. They request a short-lived device code from `/v1/auth/device/start`. The owner opens the verification URL in a browser, signs in to mirror, and approves the named device. The device polls `/v1/auth/device/poll/{device_code}` and receives a scoped client token exactly once.

## Compatibility

`GET /v1/health` returns the API version, server version, minimum supported client version and capability list. All clients must refuse incompatible API major versions and may continue across additive capability changes.

## Security notes

- Google/provider refresh tokens are encrypted at rest using `MIRROR_TOKEN_ENCRYPTION_KEY`.
- Remote deployments require HTTPS.
- The service stores only hashes of long-lived client tokens.
- Clients never receive database credentials.
- The personal server is single-owner by default; multi-user tenancy is a separate deployment profile and is not inferred.
