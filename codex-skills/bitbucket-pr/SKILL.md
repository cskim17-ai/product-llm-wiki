---
name: bitbucket-pr
description: Use when creating, inspecting, or merging Bitbucket Cloud pull requests from Codex without using the browser. Uses the bundled REST API CLI with environment variables or macOS Keychain authentication.
---

# Bitbucket PR Skill

Use this skill when the user asks Codex to create, inspect, or merge a Bitbucket Cloud pull request without using the browser UI.

## Tool

Use the bundled CLI from this skill directory:

```bash
python3 scripts/bitbucket_pr.py --help
```

When executing from another working directory, resolve `scripts/bitbucket_pr.py` relative to the directory containing this `SKILL.md`. Do not hardcode a user's personal local path in shared skill instructions.

## Authentication

Do not store credentials in the repository or in this skill.

Supported authentication sources, in priority order:

1. Environment variables
   - `BITBUCKET_OAUTH_TOKEN`
   - or `BITBUCKET_USERNAME` + `BITBUCKET_APP_PASSWORD`
   - or `BITBUCKET_USERNAME` + `BITBUCKET_API_TOKEN`
2. macOS Keychain + local config
   - config file: `~/.codex/bitbucket-pr/config.json`
   - Keychain service default: `codex-bitbucket-app-password`

Prefer macOS Keychain for repeated local use. Store only non-secret metadata such as username, auth type, and Keychain service name in the config file.

Keychain setup example:

```bash
mkdir -p ~/.codex/bitbucket-pr
printf '{"auth_type":"api_token_basic","username":"your-email@example.com","keychain_service":"codex-bitbucket-app-password"}\n' > ~/.codex/bitbucket-pr/config.json
chmod 600 ~/.codex/bitbucket-pr/config.json
security add-generic-password \
  -a 'your-email@example.com' \
  -s 'codex-bitbucket-app-password' \
  -w 'BITBUCKET_API_TOKEN' \
  -U
```

After setup, commands can run without passing credentials each time.

### Sandbox / Keychain Access

Codex sandboxed shell commands commonly cannot read macOS Keychain items even when the token is configured correctly. Symptoms include:

- `Missing authentication` from `bitbucket_pr.py`
- `security find-generic-password ...` returning item not found inside the default sandbox

If this local installation uses Keychain authentication, run `bitbucket_pr.py` create/get/merge commands with escalated sandbox permissions (`sandbox_permissions="require_escalated"`) from the first attempt. If environment-variable authentication is configured in the shell, sandboxed execution may succeed.

Do not print the secret value. Use `security find-generic-password` without `-w` for existence checks, and let `bitbucket_pr.py` read the token internally.

The Keychain service name may contain legacy wording such as `codex-bitbucket-app-password`; this is only the local Keychain service label. With `auth_type=api_token_basic`, the stored secret is a Bitbucket API token used as the Basic Auth password.

## Common Commands

Create a pull request:

```bash
python3 scripts/bitbucket_pr.py create \
  --repo workspace/repo_slug \
  --source feature/branch \
  --target main \
  --title "Pull request title" \
  --description "Pull request description."
```

Show a pull request:

```bash
python3 scripts/bitbucket_pr.py get \
  --repo workspace/repo_slug \
  --pr 8
```

Merge a pull request:

```bash
python3 scripts/bitbucket_pr.py merge \
  --repo workspace/repo_slug \
  --pr 8
```

## Safety

- Creating PRs changes remote Bitbucket state. Proceed when the user asked for it.
- Merging PRs changes the target branch. Confirm intent unless the user explicitly says to merge.
- Never print credentials.
- Never read `.secrets`.
- If authentication is missing, ask the user to configure environment variables or a Keychain-backed local config.
