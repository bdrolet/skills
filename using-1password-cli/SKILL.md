---
name: using-1password-cli
description: Use when reading secrets, credentials, or config values from 1Password via the CLI (`op`), injecting secrets into scripts or env vars, looking up vault items, or automating access to stored credentials.
---

# Using 1Password CLI

## Authentication

### Service Account (preferred for Claude Code / automation)

A service account token is set in `~/.zshrc` via `/Users/ben/src/scripts/zsh/config/.secrets`:

```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_..."
```

When `OP_SERVICE_ACCOUNT_TOKEN` is set, `op` authenticates silently — no prompts, no biometric dialogs. **Always specify `--vault` explicitly**, as service accounts require it:

```bash
op item get "Item Name" --vault "VaultName" --fields label=username
```

The service account "claude-code" has `read_items` access to the **Sales** and **Services** vaults. It cannot access Personal or Private vaults.

### Desktop App Integration (interactive use)

For interactive terminal use outside Claude Code, the desktop app integration uses biometrics:

- Enable: **Settings → Developer → Integrate with 1Password CLI**
- Auth sessions are **per terminal window**, expire after **10 minutes of inactivity**, **12 hours total**, or when 1Password locks
- There is no permanent authorization option — this is by design
- Each new subprocess (e.g. spawned by VS Code/Claude Code) counts as a new session, which is why it prompts so frequently in that context

```bash
op whoami   # check auth status
```

### Creating a Service Account

Service accounts have no UI on Family plans but work via CLI:

```bash
op service-account create "name" \
  --vault "Sales:read_items" \
  --vault "Services:read_items" \
  --raw
```

Save the token immediately — it's only shown once. Add to `.secrets`:

```bash
export OP_SERVICE_ACCOUNT_TOKEN="ops_..."
```

Note: service accounts cannot access Personal or Private vaults.

## Reading Secrets

**With service account (vault required):**
```bash
op item get "Item Name" --vault "VaultName" --fields label=username,label=password
op read "op://VaultName/Item/field"
```

**With desktop integration (vault optional):**
```bash
op item get "Item Name" --fields label=password
op read "op://Personal/GitHub/credential"
```

**Secret reference format:** `op://[vault]/[item]/[field]`
- Field defaults to `password` if omitted

## Listing Vaults and Items

```bash
op vault list
op item list                          # all items (desktop auth only)
op item list --vault "Vault Name"     # filtered by vault
op item list --categories Login       # filtered by category
```

## Injecting Secrets into Scripts

**Inline substitution in a command:**
```bash
op run -- some-command --token op://Vault/Item/credential
```

**Populate env vars from a dotenv-style file with `op://` references:**
```bash
# .env.tpl
# DB_PASSWORD=op://Production/Database/password
# API_KEY=op://Production/API/key

op run --env-file=.env.tpl -- node server.js
```

**Export to shell:**
```bash
export MY_SECRET=$(op read "op://Vault/Item/password")
```

## Common Patterns in Scripts

Use `--format json` when parsing output programmatically:
```bash
op item get "SSH Key" --vault "VaultName" --format json | jq '.fields[] | select(.label=="private key") | .value'
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Prompt on every command in VS Code | Use `OP_SERVICE_ACCOUNT_TOKEN` — desktop auth is per-process, not per-user |
| `a vault query must be provided` | Add `--vault "VaultName"` — required when using service account token |
| `[ERROR] 401: Unauthorized` | Run `eval $(op signin)` or check `OP_SERVICE_ACCOUNT_TOKEN` is set |
| `[ERROR] 403` on an item | Check vault membership or service account vault scope |
| `op: command not found` | `brew install --cask 1password-cli` |
| Biometric not prompting | Ensure desktop integration is on: **Settings → Developer → CLI** |
