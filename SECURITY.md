# Security and privacy

This repository contains executable policy and sanitized examples only.

Never commit:

- Gmail message bodies, message IDs, thread IDs, or attachment contents;
- live Google Sheet rows or rendered personal briefs;
- calendar event details;
- addresses, account numbers, tracking history, or credentials;
- OAuth tokens, API keys, cookies, or local connector configuration.

Use `config/ops.local.json` for local spreadsheet identifiers. It is ignored by Git. If live data is committed accidentally, rotate affected secrets when applicable and rewrite repository history; a normal deletion commit is insufficient.

