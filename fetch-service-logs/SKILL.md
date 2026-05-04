---
name: fetch-service-logs
description: Fetch and analyze service logs from Datadog using the Logs Search API v2. Supports Mastra, Steward, and n8n services. Use when the user asks about service logs, Datadog logs, log streaming, or wants to debug issues in staging or production for any supported service.
compatibility: Requires Python 3 venv at mastra/scripts/debug/.venv and Datadog API keys (DD_API_KEY, DD_APP_KEY) in mastra/scripts/debug/.env.
---

# Fetch Service Logs

Fetch logs from Datadog via the Logs Search API v2 for any supported service. Default: last 15 minutes, slim JSON (id, message, timestamp, status) to stdout.

## Service Registry

| Service | Script | Default Query | Env Tag | Notes |
|---------|--------|---------------|---------|-------|
| mastra | `fetch_mastra_logs.py` | `service:mastra` | `@dd.env` | |
| steward | `fetch_steward_logs.py` | `service:steward` | `@app.env` | |
| n8n | `fetch_n8n_logs.py` | `service:n8n` | _(none)_ | n8n logs have no env tag; `--env` flag is not available |

All scripts live in `mastra/scripts/debug/scripts/`.

## Prerequisites

- Python venv at `mastra/scripts/debug/.venv` with dependencies installed (`pip install -r mastra/scripts/debug/requirements.txt`)
- `DD_API_KEY` and `DD_APP_KEY` set in `mastra/scripts/debug/.env` (loaded automatically by the script via `python-dotenv`)
- The Application Key must have the **Logs Read Data** scope

## Usage

Always activate the venv before running a script. Substitute `<service>` with the service name from the registry:

```bash
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_<service>_logs.py [flags]
```

## Available flags

| Flag | Description |
|------|-------------|
| `--since` | Time window (e.g. `15m`, `1h`, `1d`, or a number = minutes). Default: `15m` |
| `--query` | Datadog log search query. Default: per-service (see registry) |
| `--limit N` | Max number of log events (0 = no limit). Default: `0` |
| `--output FILE`, `-o FILE` | Write logs to FILE as JSON array. Default: stdout |
| `--pretty` | Pretty-print JSON output |
| `--env ENV` | Filter by environment (`staging`/`stg` or `production`/`prod`). Appends the service's env tag to the query. Only available for services that have an env tag (see registry) |
| `--full` | Output full Datadog log objects instead of slim (id, message, timestamp, status) |
| `--stream` | Stream logs continuously until Ctrl+C |
| `--stream-interval SECS` | Seconds between polls when streaming. Default: `5.0` |

## What the script does

1. Loads env vars from `mastra/scripts/debug/.env` automatically
2. Queries Datadog Logs Search API v2 with the given query and time window
3. Paginates through all results (or up to `--limit`)
4. Outputs slim JSON per log by default (id, message, timestamp, status, and details if present)
5. For steward and n8n, automatically parses JSON-encoded message strings into structured objects
6. With `--stream`, polls continuously and emits only new logs each interval
7. Prints fetch count and elapsed time to stderr

## Subagents

This skill includes two subagent definitions for automated log debugging:

- [subagents/fetch-service-logs.md](subagents/fetch-service-logs.md) -- Fetches logs for any supported service and saves to a timestamped file. Runs on `model: fast`.
- [subagents/analyze-service-logs.md](subagents/analyze-service-logs.md) -- Reads a log file and produces a structured analysis report with per-service guidance.
