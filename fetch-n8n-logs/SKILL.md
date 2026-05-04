---
name: fetch-n8n-logs
description: Fetch and analyze n8n service logs from Datadog using the Logs Search API v2. Use when the user asks about n8n logs, Datadog logs for n8n, n8n service errors, or wants to debug n8n issues in staging or production.
compatibility: Requires Python 3 venv at mastra/scripts/debug/.venv and Datadog API keys (DD_API_KEY, DD_APP_KEY) in mastra/scripts/debug/.env.
---

# Fetch n8n Logs

Fetch n8n logs from Datadog. JSON-encoded message strings are automatically parsed into structured objects. For full documentation (prerequisites, all flags, how it works, subagents), read [fetch-service-logs/SKILL.md](../fetch-service-logs/SKILL.md).

## Service Config

| Key | Value |
|-----|-------|
| Script | `mastra/scripts/debug/scripts/fetch_n8n_logs.py` |
| Default query | `service:n8n` |
| Env tag | _(none -- n8n logs have no env tag, so `--env` is not available)_ |

## Quick Examples

```bash
# Errors in the last hour
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_n8n_logs.py --since 1h --query "service:n8n status:error" --pretty

# Last 15 minutes, pretty output
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_n8n_logs.py --pretty

# Last 24 hours, save to file
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_n8n_logs.py --since 24h -o logs/n8n-logs.json --pretty

# Timeouts and 504s
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_n8n_logs.py --since 24h --query "service:n8n (*timeout* OR *504*)" --pretty

# Custom query with limit
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_n8n_logs.py --query "service:n8n status:error" --limit 50 --pretty
```
