---
name: batch-ai-dispatcher
description: Batch-call the Mastra AI Dispatcher for a list of member IDs and save response texts to a file. Defaults to staging. Use when the user wants to run a dispatcher workflow for multiple members, batch test initial engagement, or collect dispatcher responses for a list of member IDs.
---

# Batch AI Dispatcher

Run the AI Dispatcher for multiple member IDs and save `response.text` for each to a file.
Defaults to **Mastra staging** (`http://mastra.staging.internal`).

## Quick Start

```bash
cd mastra/scripts/debug
python3 scripts/batch_dispatcher.py <id1> <id2> <id3>
```

## Input Methods

```bash
# Positional args
python3 scripts/batch_dispatcher.py abc-123 def-456 ghi-789

# From file (one ID per line, # comments ok, extra columns ignored)
python3 scripts/batch_dispatcher.py --file member_ids.txt

# Piped via stdin
cat member_ids.txt | python3 scripts/batch_dispatcher.py
```

## Environments

Default: `--target staging`. Use `--target prod` for production. Aliases: `stg`, `stage`, `production`.

## Examples

```bash
# Staging (default), initial-engagement (default)
python3 scripts/batch_dispatcher.py abc-123 def-456

# Production, welcome-call type
python3 scripts/batch_dispatcher.py --file ids.txt --target prod --type welcome-call

# Custom output path, verbose
python3 scripts/batch_dispatcher.py abc-123 -o results.txt -v

# Force refresh, longer timeout
python3 scripts/batch_dispatcher.py --file ids.txt --force-refresh --timeout 180
```

## Output

Results are saved to `<type>-results-<timestamp>.txt` (or `--output` path):

```
=== <memberId> ===
<response.text>

=== <memberId> ===
ERROR: <error message>
```

## Options

| Flag | Description |
|------|-------------|
| `--file, -f FILE` | Read member IDs from file |
| `--type, -t TYPE` | Dispatch type (default: `initial-engagement`) |
| `--target TARGET` | Environment: staging, prod (default: staging) |
| `--base-url URL` | Override base URL |
| `--bearer-token TOKEN` | Override bearer token for target env |
| `--output, -o PATH` | Output file path |
| `--force-refresh` | Bypass cache |
| `--timeout SECONDS` | Per-call timeout (default: 120) |
| `-v, --verbose` | Verbose stderr output |

## Environment

Requires per-environment env vars in `mastra/scripts/debug/.env`:
- Staging: `MASTRA_BASE_URL_STAGING`, `AUtH_BEARER_TOKEN_STAGING`
- Prod: `MASTRA_BASE_URL_PROD`, `AUtH_BEARER_TOKEN_PROD`
