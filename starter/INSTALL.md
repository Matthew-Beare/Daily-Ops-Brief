# Install Personal Ops Planner — No Command Prompt

This is the default browser-only setup path for a non-technical user. It is done in GitHub and ChatGPT/Codex in a web browser. Do **not** open Command Prompt, PowerShell, Terminal, Git Bash, or a code editor. Do **not** install Git or GitHub CLI. Do **not** copy commands, tokens, SSH keys, or passwords.

The one-time setup has three separate jobs:

1. GitHub creates a private personal copy of the public starter.
2. The ChatGPT GitHub app receives read access to that personal repository.
3. Codex receives repository access so it can validate, commit, and push lasting source changes.

The ordinary ChatGPT GitHub app is read-only. A read connection is useful, but it is **not** proof that Codex can commit or push.

## Before you begin

You need:

- a web browser;
- a ChatGPT account with the GitHub app and Codex available in the product experience you use;
- a free GitHub account with a verified email address; and
- about ten minutes.

If a workplace owns your GitHub account, an administrator may need to approve ChatGPT/Codex repository access. That is an account-policy issue, not a reason to use a command line.

## Step 1 — Create or sign in to GitHub

If you already have a personal GitHub account, sign in and continue to Step 2.

If not:

1. Open [GitHub sign-up](https://github.com/signup).
2. Follow GitHub's prompts and verify your email address.
3. Configure two-factor authentication when GitHub offers it.

GitHub requires a verified email for basic actions such as creating a repository. See [GitHub's account instructions](https://docs.github.com/en/account-and-profile/how-tos/account-management/creating-an-account-on-github).

Never give an assistant your GitHub password, verification code, recovery code, token, or SSH key.

## Step 2 — Make your private personal repository

This first repository is created once by the user on GitHub's website. The current assistant integration can update an existing authorized repository, but it cannot create the user's first GitHub repository.

1. Open [Create your private copy](https://github.com/Matthew-Beare/Daily-Ops-Brief/generate). If GitHub instead shows the public starter, select **Use this template** and then **Create a new repository**.
2. Choose your own GitHub account as **Owner**.
3. Give it a neutral personal name, such as `personal-organizer`.
4. Select **Private**.
5. Leave **Include all branches** off. The default branch is the audited starter.
6. Select **Create repository from template**.

GitHub documents this browser workflow in [Creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

If **Use this template** is missing, stop and report: `Starter blocked — upstream is not enabled as a GitHub template.` Do not substitute a fork, Codespace, download, local copy, or command-line clone.

When GitHub finishes, copy only the non-secret repository name shown near the top, in this form:

```text
your-github-name/personal-organizer
```

Give that `owner/repository` name to the onboarding assistant. The assistant must read it back and verify the owner, private visibility, default branch, and current commit before continuing. It must never copy the reference deployment's personal data, schedules, accounts, or authority IDs.

## Step 3 — Give ChatGPT read access

1. In ChatGPT, open **Settings → Apps**.
2. Find **GitHub** and select **Connect**.
3. GitHub will ask you to authorize the ChatGPT app. Select only your new personal repository unless you deliberately want broader access.
4. Return to ChatGPT.

If GitHub was already connected, open **Settings → Apps → GitHub → Choose repositories** (the wording may also be **Configure Repositories on GitHub**) and add the new repository.

New or private repositories can take about five minutes to appear. Wait once, then use the GitHub app's repository configuration page to confirm the exact repository is allowed. An organization-owned repository may show **Request** and require an administrator. See [OpenAI's GitHub connection instructions](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt).

This step proves read access only. It does not authorize commits or pushes.

## Step 4 — Give Codex write access

1. Open **Codex** from ChatGPT's navigation.
2. Select **Connect to GitHub** if it is shown, and authorize the exact personal repository.
3. Create or select a Codex environment for that repository if the product asks for one.
4. Return to this onboarding conversation and provide the same `owner/repository` name.

Availability and wording can vary by ChatGPT plan or workspace. If Codex or repository authorization is unavailable, report:

```text
Source setup blocked — ChatGPT can read the repository, but no verified Codex GitHub write capability is available.
```

Do not claim installation succeeded. Do not send the user to Command Prompt as a fallback. Onboarding questions may continue, but lasting source changes remain blocked until a write-capable Codex connection is available.

## Step 5 — Required verification

Before asking life-planning questions, the assistant must show this short readback:

```text
Repository: owner/name
Visibility: private
Default branch: main (or the observed default)
Starter commit: observed commit ID
ChatGPT read: verified / blocked
Codex write: verified / blocked
Local command line required: no
```

`Verified` means observed through the relevant connection. The existence of a button, an authorization screen, a local file, or a read-only search result is not proof of write access.

The first coherent personal configuration write requires the user's bounded provisioning approval. After writing, Codex must run the repository's validation and privacy gates, commit, push, read the remote commit back, and confirm CI. A failed check remains failed; it is never renamed as success.

## Step 6 — Start the personal interview

Only after the repository capability readback, open [`START_HERE.md`](START_HERE.md) and paste its first-boot prompt into the same Codex/ChatGPT project that has access to the personal repository.

The interview explicitly covers meal planning and household routines. Examples include laundry, moving a load from washer to dryer, folding/putting away, and picking up dry-cleaning, tailoring, repairs, or other dropped-off items. Those become canonical routines/tasks or Calendar reminders—not one separate ChatGPT automation per chore.

## Developer-only alternative

Local Git and command-line setup may be documented for developers elsewhere, but it is never offered during default onboarding. It may be used only after the user explicitly says they want developer/command-line mode.
