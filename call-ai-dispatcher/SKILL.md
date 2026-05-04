---
name: call-ai-dispatcher
description: Call the Mastra AI Dispatcher for any workflow type (initial-engagement, welcome-call, toc-admit, etc.) via n8n or Mastra backends. Use when the user wants to test a dispatcher workflow, call the AI dispatcher, run initial engagement, test a snapshot workflow, or debug dispatcher responses.
---

# Call AI Dispatcher

Run any AI Dispatcher workflow type from `mastra/scripts/debug/`.

## Quick Start

Always activate the venv before running:

```bash
source mastra/scripts/debug/.venv/bin/activate && python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py <type> [options]
```

## Available Types

| Type | Aliases | Description |
|------|---------|-------------|
| `initial-engagement` | `ie` | Initial Engagement |
| `welcome-call` | `wc` | Welcome Call |
| `toc-admit` | `toc-a` | TOC Admit |
| `toc-discharge` | `toc-d` | TOC Discharge |
| `general-member-snapshot` | `snapshot`, `gms` | General Member Snapshot |
| `chronic-heart-failure` | `chf` | CHF Failure or Intervention |
| `new-stew-member-benefits` | | New Stew Member Benefits |
| `otc-benefits` | `otc` | OTC Benefits |

These mirror the `WORKFLOW_REGISTRY` in `mastra/src/mastra/workflows/ai-dispatcher.ts`.

## Targets

| Target | Flag | Backend | Required Env Vars |
|--------|------|---------|-------------------|
| n8n (default) | `--target n8n` | `N8N_BASE_URL/webhook/mastra-ai-dispatcher` | `N8N_BASE_URL`, `JWT_SHARED_SECRET` or `N8N_BEARER_TOKEN` |
| Mastra staging | `--target mastra-staging` | `MASTRA_BASE_URL_STAGING/ai-dispatcher` | `MASTRA_BASE_URL_STAGING`, `AUtH_BEARER_TOKEN_STAGING` |
| Mastra prod | `--target mastra-prod` | `MASTRA_BASE_URL_PROD/ai-dispatcher` | `MASTRA_BASE_URL_PROD`, `AUtH_BEARER_TOKEN_PROD` |
| Mastra local dev | `--target local` | `http://localhost:3001/ai-dispatcher` | none (auth optional; `MASTRA_BASE_URL_LOCAL` / `AUTH_BEARER_TOKEN_LOCAL` override defaults) |

## Examples

All examples assume the venv is activated first:

```bash
source mastra/scripts/debug/.venv/bin/activate
```

```bash
# Default: call via n8n with default member ID
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py ie -v

# Call via Mastra staging
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py ie --target mastra-staging -v

# Call via Mastra prod
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py ie --target mastra-prod -v

# Call against local Mastra dev (requires `mastra dev` running; initial-engagement
# also needs the Steward SSM tunnel on localhost:15432)
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py ie --target local --force-refresh -v

# Specific member, force refresh
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py welcome-call -m <uuid> --force-refresh -v

# With extra data payload
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py toc-admit -m <uuid> -d '{"snapshotId":"TOC_ADMIT"}'

# List all types
python3 mastra/scripts/debug/scripts/call_ai_dispatcher.py --list
```

## Options

| Flag | Description |
|------|-------------|
| `--target {n8n,mastra-staging,mastra-prod,local}` | Backend (default: mastra) |
| `-m, --member-id UUID` | Member UUID (default: `b80d4da0-...`) |
| `-d, --data JSON` | Extra JSON data; use `@file.json` to read from file |
| `--force-refresh` | Bypass cache |
| `--base-url URL` | Override backend base URL |
| `--auth-token TOKEN` | Override bearer token (Mastra target) |
| `--timeout SECONDS` | HTTP timeout (default: 120) |
| `-v, --verbose` | Print request/response details to stderr |

## Environment

Env vars are loaded from `mastra/scripts/debug/.env`. Ensure required vars are set before calling.

## Architecture

```
scripts/call_ai_dispatcher.py     # CLI entry point (type registry, aliases, arg parsing)
  -> services/ai_dispatcher_service.py  # Routing layer (n8n vs mastra)
    -> clients/n8n_client.py            # n8n webhook client (JWT/bearer auth, HMAC, retries)
    -> clients/mastra_client.py         # Mastra client (bearer auth, retries)
```

## Related Scripts

- `scripts/call_n8n_workflow.py` — calls individual n8n workflow webhooks directly (bypasses the dispatcher)
- `clients/mastra_client.py` — can also be run standalone: `python3 clients/mastra_client.py <type> -m <uuid>`
