# OAuth and AI connections, in normal-human language

## OAuth is not something the customer installs

OAuth is the permission handshake behind a button such as **Continue with Google**.

1. MIRA sends the user to Google.
2. Google signs the user in and shows exactly which permissions MIRA is requesting.
3. The user approves or declines.
4. Google sends MIRROR a revocable permission credential.
5. MIRROR stores that credential encrypted on the server.
6. MIRA uses only the approved Google APIs. The user's Google password never enters MIRA.

The same general pattern applies to Microsoft 365.

## Why the current self-hosted build asks for Google client configuration

Google needs to know which application is requesting access and which callback URL is legitimate. A self-hosted MIRROR server can have a different hostname from every other installation, so the starter deployment supports operator-owned Google OAuth credentials.

That is acceptable for an engineering or self-hosted pilot. It is not the desired retail onboarding experience.

## Desired retail onboarding

A commercial MIRA distribution should use a verified MIRA Google integration so a customer sees a branded Google consent screen and clicks **Continue with Google**. The exact deployment can use either a managed connector/broker or another verified redirect architecture. That is a deployment/service concern, not a reason to put Google passwords or OAuth secrets in the clients.

## Normal permissions versus migration permissions

Normal operation asks incrementally for the capabilities a user turns on. For example, Drive evidence does not imply Gmail access.

Importing an existing Google estate is intentionally separate. The Migration workspace can request read-only Drive/Sheets scopes, discover spreadsheets, and stage snapshots. Staging does not overwrite MIRROR. Mapping and apply happen only after the source schema is understood.

## ChatGPT Plus is not an API key

A ChatGPT subscription and OpenAI API billing are separate products. MIRA therefore does not claim that ChatGPT Plus can be embedded as an external model backend.

The no-API-bill companion architecture is:

**ChatGPT conversation -> MIRA/MIRROR ChatGPT app or MCP tool bridge -> MIRROR scoped tools -> Git/provider adapters**

The conversation stays in ChatGPT. MIRROR exposes bounded tools and data. No OpenAI API key is required by the standalone MIRA client for that companion mode.

Sign in with ChatGPT may be used for identity where supported, but identity login is not permission to consume ChatGPT model compute from an external application.
