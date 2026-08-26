# OAuth and AI connections, in normal-human language

## OAuth is not something the customer installs

OAuth is the permission handshake behind a button such as **Continue with Google**.

1. MIRA sends the user to Google's real sign-in/permission screen.
2. Google signs the user in and shows exactly which permissions MIRA is requesting.
3. The user approves or declines.
4. Google returns a revocable permission credential to the approved MIRA surface.
5. That surface uses only the approved Google APIs. The user's Google password never enters MIRA.

The same general pattern applies to Microsoft 365.

## MIRA has more than one approved authorization transport

A normal user must not need to understand this distinction, but the implementation does.

### ChatGPT + Google-native MIRA

The primary MIRA initialization interview happens in ChatGPT. ChatGPT uses the user's approved Google connections/capabilities to read and write the Google-backed MIRROR authority.

The MIRA app is optional. If installed, its first-boot wizard connects that device/app to the same MIRROR profile. A Google-native app client must use an approved native/web Google authorization flow and must not require a separately configured Linux or hosted MIRROR server merely to make **Continue with Google** work.

Platform credentials belong in platform-secure storage or the provider's supported credential system. Do not expose reusable Google credentials to ordinary JavaScript, logs, screenshots, Git, or user-facing settings.

### Self-hosted MIRROR

A self-hosted MIRROR server may use server-side OAuth. Google needs to know which application is requesting access and which callback URL is legitimate, so a self-hosted installation can require operator-owned Google OAuth configuration or a supported managed authorization design.

Server-side credentials are encrypted at rest and never committed to source control.

## The app wizard and the ChatGPT interview are both real

- **ChatGPT initialization interview:** primary system/account interview. It creates or updates the shared MIRROR profile and selected life domains.
- **MIRA app first boot:** device/app wizard. It connects the device, requests device permissions, confirms shared settings and teaches capture/display workflows.
- If the app is installed first, it may establish the initial shared settings and ChatGPT later continues/refines them.
- If ChatGPT was initialized first, the app must reuse that profile rather than invent a second one.
- The MIRA app is optional. Core MIRA must never assume it is installed.

## Desired retail onboarding

A production MIRA distribution should use verified MIRA Google registrations so a customer sees a branded Google consent screen and clicks **Continue with Google**.

A visible account/provider button has exactly three acceptable outcomes:

1. open the real provider authorization flow;
2. navigate to the exact prerequisite needed first; or
3. show a plain-English blocker explaining what is not configured.

A click that silently does nothing is a release-blocking defect.

## Normal permissions versus migration permissions

Normal operation asks incrementally for the capabilities a user turns on. Drive evidence does not imply Gmail access.

Importing an existing Google estate is intentionally separate. Migration can request read-only Drive/Sheets access, discover spreadsheets, and stage snapshots. Staging does not overwrite MIRROR. Mapping and apply happen only after the source schema is understood.

## ChatGPT Plus is not an API key

A ChatGPT subscription and OpenAI API billing are separate products. MIRA therefore does not claim that ChatGPT Plus can be embedded as an external model backend.

The no-API-bill companion architecture is:

**ChatGPT conversation -> MIRA's approved ChatGPT integration -> scoped MIRROR/Google capabilities**

The conversation stays in ChatGPT. MIRA can answer directly in chat, write approved structured results into MIRROR for another surface such as the MIRA app to display, or do both.

No OpenAI API key is required by the standalone MIRA client for that companion mode.
