---
name: fetch-mastra-logs
description: Fetch and analyze Mastra service logs from Datadog using the Logs Search API v2. Use when the user asks about Mastra logs, Datadog logs, service errors, log streaming, or wants to debug issues in staging or production.
compatibility: Requires Python 3 venv at mastra/scripts/debug/.venv and Datadog API keys (DD_API_KEY, DD_APP_KEY) in mastra/scripts/debug/.env.
---

# Fetch Mastra Logs

Fetch Mastra logs from Datadog. For full documentation (prerequisites, all flags, how it works, subagents), read [fetch-service-logs/SKILL.md](../fetch-service-logs/SKILL.md).

## Service Config

| Key | Value |
|-----|-------|
| Script | `mastra/scripts/debug/scripts/fetch_mastra_logs.py` |
| Default query | `service:mastra` |
| Env tag | `@dd.env` |

## Quick Examples

```bash
# Errors in the last hour
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_mastra_logs.py --since 1h --query "service:mastra status:error" --pretty

# Last 15 minutes, pretty output
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_mastra_logs.py --pretty

# Staging errors
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_mastra_logs.py --env stg --since 1h --query "service:mastra status:error" --pretty

# Production logs
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_mastra_logs.py --env prod --pretty

# Filter by workflow
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_mastra_logs.py --query "service:mastra @workflow:initial-engagement" --limit 50 --pretty
```
