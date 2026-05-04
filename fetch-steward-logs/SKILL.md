---
name: fetch-steward-logs
description: Fetch and analyze Steward service logs from Datadog using the Logs Search API v2. Use when the user asks about Steward logs, Datadog logs for steward, steward service errors, or wants to debug steward issues in staging or production.
compatibility: Requires Python 3 venv at mastra/scripts/debug/.venv and Datadog API keys (DD_API_KEY, DD_APP_KEY) in mastra/scripts/debug/.env.
---

# Fetch Steward Logs

Fetch Steward logs from Datadog. JSON-encoded message strings are automatically parsed into structured objects. For full documentation (prerequisites, all flags, how it works, subagents), read [fetch-service-logs/SKILL.md](../fetch-service-logs/SKILL.md).

## Service Config

| Key | Value |
|-----|-------|
| Script | `mastra/scripts/debug/scripts/fetch_steward_logs.py` |
| Default query | `service:steward` |
| Env tag | `@app.env` |

## Quick Examples

```bash
# Errors in the last hour
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_steward_logs.py --since 1h --query "service:steward status:error" --pretty

# Last 15 minutes, pretty output
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_steward_logs.py --pretty

# Staging errors
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_steward_logs.py --env stg --since 1h --query "service:steward status:error" --pretty

# Production logs
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_steward_logs.py --env prod --pretty

# Custom query with limit
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_steward_logs.py --query "service:steward @app.env:staging" --limit 50 --pretty
```
