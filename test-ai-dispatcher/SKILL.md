---
name: test-ai-dispatcher
description: Use when the user wants to smoke-test all AI Dispatcher workflow types, validate dispatcher responses, or run a health check across all dispatcher endpoints on local, staging, or production.
---

# Test AI Dispatcher

Run all 8 dispatcher workflow types against a target environment and produce a validation report with pass/fail status, response shape checks, and timing.

## Quick Start

```bash
source mastra/scripts/debug/.venv/bin/activate && python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py
```

Defaults to **mastra-staging** with the built-in member ID.

## Targets

| Target | Flag |
|--------|------|
| Mastra staging (default) | `--target mastra-staging` |
| Mastra production | `--target mastra-prod` |
| Mastra local dev | `--target mastra-local` |
| n8n | `--target n8n` |

### Running against `mastra-local`

1. Follow the `starting-local-dev` skill so `mastra dev` is running on port 3001.
2. If you plan to hit `initial-engagement`, start the Steward SSM tunnel on `localhost:15432` — `fetchCoreMemberData()` needs it and the other 7 types do not. Example:
   ```bash
   aws ssm start-session \
     --profile eng-prod \
     --region us-east-2 \
     --target i-0c5720bfcb7002667 \
     --document-name AWS-StartPortForwardingSessionToRemoteHost \
     --parameters '{"host":["waywardappstack-postgresprimaryreadreplica3ab5f7f3-vygfk3ev5vop.cmo4fxfp0btp.us-east-2.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["15432"]}'
   ```
3. Run the suite:
   ```bash
   source mastra/scripts/debug/.venv/bin/activate \
     && python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py \
          --target mastra-local --force-refresh --no-open
   ```

Note: `mastra dev` binds IPv6-only on `[::1]:3001` when `MASTRA_HOST=localhost` (the default in `mastra/.env`). The client now defaults `mastra-local` to `http://localhost:3001` so hostname resolution picks `::1` automatically — no `--base-url` override needed. If you set `MASTRA_HOST=127.0.0.1` or `0.0.0.0` instead, this still works.

## Examples

```bash
source mastra/scripts/debug/.venv/bin/activate

# All types against staging (default)
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py

# Production, verbose
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --target mastra-prod -v

# Local dev (requires Mastra dev server running; see "Running against mastra-local")
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --target mastra-local --force-refresh

# Subset of types only
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py -t ie -t wc -t snapshot

# Custom member, force refresh, save full responses
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py -m <uuid> --force-refresh --full-output results.json
```

## Output

Creates a timestamped folder under `mastra/scripts/debug/results/` (e.g. `results/test-dispatcher-20260312-203500/`) containing:

- **`index.html`** — interactive report with pass/fail table, collapsible response previews, and links to JSON files. Auto-opens in the browser (suppress with `--no-open`).
- **`<type>.json`** — one pretty-printed JSON file per workflow type (metadata + full response)

A plain-text summary is also printed to stdout.

## Validation Checks

Each response is validated for:
- `success` field is `true`
- `timestamp` field is a string
- `data.response` object exists
- `data.response.text` is a non-empty string

## Options

| Flag | Description |
|------|-------------|
| `--target` | Backend: mastra-local, mastra-staging, mastra-prod, n8n (default: mastra-staging) |
| `-m, --member-id` | Member UUID (has built-in default) |
| `-t, --type` | Run specific types only (repeatable, accepts aliases) |
| `-o, --output` | Output directory path (default: `mastra/scripts/debug/results/test-dispatcher-<ts>/`) |
| `--force-refresh` | Bypass cache |
| `--timeout` | Per-call timeout in seconds (default: 120) |
| `--no-open` | Don't auto-open the HTML report in the browser |
| `-v, --verbose` | Verbose stderr output |

## Agent Execution Notes

**IMPORTANT:** Always pass `--no-open` when running the script, then open the HTML report manually with a separate `open <path>/index.html` command. The script's `webbrowser.open()` call does not work from Cursor's background shell because it lacks the desktop session context to launch the browser.

## Dependencies

**REQUIRED:** Uses the same Python environment and clients as `call-ai-dispatcher`. Env vars loaded from `mastra/scripts/debug/.env`.
