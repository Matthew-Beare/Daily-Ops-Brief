# Start MIRA | MIRROR

This is the normal setup page for a non-technical user.

**MIRROR is your private life system. MIRA is the assistant you talk to.**

You do not need to know programming. You do not need a command prompt. You do not need to type Git commands.

## What Git and GitHub mean

**Git is version history.** It keeps a record of changes to the rules and code so a bad change can be traced or rolled back.

**GitHub is the website that stores those versioned files.** Think of it as the filing cabinet for MIRROR's instructions, not the place where all of your private life data must live.

Your changing personal facts belong in the private state provider selected during setup, such as Google Sheets/Drive or an approved Microsoft equivalent. Passwords, tokens, medical records, private email bodies, receipts, and other sensitive operational data do not belong in the public source template.

## Personal browser setup

### 1. Sign in to GitHub

Use a normal web browser. If you do not have a personal GitHub account, create one at GitHub and verify the email address.

Never give MIRA your GitHub password, verification code, recovery code, token, or SSH key.

### 2. Make your private MIRROR source copy

Open:

`https://github.com/Matthew-Beare/Daily-Ops-Brief/generate`

On the page:

1. Choose **your own GitHub account** as Owner.
2. Give the repository a neutral name such as `my-mirror`.
3. Choose **Private**.
4. Leave **Include all branches** off.
5. Select **Create repository from template**.

If the template button is missing, stop. Do not substitute a fork, Codespace, download, or local command-line copy.

### 3. Give ChatGPT read access

In ChatGPT, open **Settings → Apps → GitHub** and connect the exact private repository you just created.

This proves read access only.

### 4. Give Codex write access

Open Codex in ChatGPT and authorize that same private repository.

The ordinary ChatGPT GitHub app is read-only. Codex write access is a separate capability and must be proven by an actual bounded write plus remote readback before setup is called complete.

### 5. Give MIRA the repository name

Send only the non-secret repository name in this form:

`your-name/your-repository`

MIRA must verify:

- owner;
- private visibility;
- default branch;
- current commit;
- ChatGPT read access; and
- Codex write/readback capability.

No Command Prompt is required.

### 6. Let MIRA finish setup

The installed package is still named `life-planner` internally for compatibility. That is an implementation ID, not the product name.

MIRA installs and validates `starter/life-planner`, verifies the selected state/evidence provider, then starts first boot.

The defaults are already settled:

- System: **MIRROR**
- Assistant: **MIRA**
- Ask the user to invent a system name: **No**

If a legacy onboarding document asks “What should the system be called?”, MIRA resolves that item to **MIRROR** automatically unless the user explicitly asks for a private alias.

## Corporate, government, health-care, or locked-down devices

Do not create personal GitHub, cloud, or AI accounts to bypass workplace policy. Start with [`ENTERPRISE_PILOT.md`](ENTERPRISE_PILOT.md). Approved organization Git or a managed central source may replace personal GitHub.

## If something goes wrong

Use [`INSTALL.md`](INSTALL.md) for the detailed browser-only troubleshooting path and capability readback fields. Do **not** open Command Prompt, PowerShell, Terminal, Git Bash, or install Git/GitHub CLI as a fallback for normal onboarding.

If anything asks you to paste a password, one-time code, recovery code, token, or SSH key into chat, stop.
