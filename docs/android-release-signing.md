# Android release signing

## What signing means

Android requires application packages to carry a cryptographic signature. For updates, the installed app and the new app must prove the same signing identity.

The release private key is therefore MIRA's permanent Android identity. It is not a customer password and it is not an API token.

- The private key must never be committed to Git.
- The same release identity must be retained for future updates.
- Losing the key can make existing sideloaded installations impossible to update normally.
- Leaking the key can allow an attacker to impersonate the application signature.

## Repository workflow

The Android workflow expects four GitHub Actions secrets:

- `MIRA_ANDROID_KEYSTORE_BASE64`
- `MIRA_ANDROID_KEYSTORE_PASSWORD`
- `MIRA_ANDROID_KEY_ALIAS`
- `MIRA_ANDROID_KEY_PASSWORD`

The workflow decodes the keystore only into the temporary GitHub runner, builds the release APK, and verifies the result with Android `apksigner`.

The repository contains no private signing key material.

## Pilot versus production

A debug APK is convenient for engineering tests but uses a development identity.

An unsigned release artifact proves that release compilation works, but it is not an updateable production release.

A customer release is eligible to ship only after:

1. the permanent signing secrets are installed in the repository's Actions secrets;
2. the exact release SHA produces a release APK;
3. `apksigner` verifies the resulting package;
4. the signing certificate fingerprint matches the retained release identity;
5. the package is exercised on representative Android hardware.

## Distribution

For managed-store distribution, the store's signing/update model must be configured deliberately. For direct/sideload distribution, retain the same private release identity for every future update.

MIRA must never silently generate a fresh signing key per release.
