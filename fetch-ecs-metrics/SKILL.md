# Fetch ECS Metrics

Fetch ECS service metrics from AWS CloudWatch. Supports standard ECS metrics (CPU/Memory utilization) and Container Insights metrics (task counts, network I/O, storage, reserved vs utilized CPU/memory).

## Prerequisites

- Python venv at `mastra/scripts/debug/.venv` with dependencies installed (`pip install -r mastra/scripts/debug/requirements.txt`)
- AWS credentials configured via standard boto3 chain (env vars, `~/.aws/credentials`, IAM role, etc.)

## Service Registry

| Service | Description |
|---------|-------------|
| `n8n-service` | n8n main service |
| `n8n-worker-service` | n8n worker / task runner |
| `mastra-service` | Mastra AI service |
| `redis-service` | ElastiCache Redis |
| `langfuse-service` | Langfuse observability |
| `litellm-prod-service` | LiteLLM proxy |
| `clickhouse-service` | ClickHouse analytics |
| `warp-endpoint-service` | Warp endpoint |

Run the script with no arguments to list all available services dynamically.

## Quick Examples

```bash
# List available services
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py

# Last hour summary for n8n
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py n8n-service --summary

# Last 6 hours for mastra, save to file
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py mastra-service --since 6h --pretty -o mastra/scripts/debug/logs/mastra-metrics.json

# Specific time window (e.g. investigating an incident)
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py n8n-worker-service --start 2026-03-17T21:00:00Z --end 2026-03-17T22:00:00Z --summary

# Only CPU/Memory utilization (faster)
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py n8n-service --since 1h --ecs-only --summary

# Only Container Insights (task counts, network, storage)
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py n8n-service --since 1h --insights-only --summary

# Specific metrics only
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py n8n-service --metrics CPUUtilization MemoryUtilization --summary
```

## Available Flags

| Flag | Description |
|------|-------------|
| `service` | ECS service name (positional). Omit to list available services. |
| `--since` | Time window (e.g. `15m`, `1h`, `6h`, `1d`). Default: `1h` |
| `--start` | Absolute start time (ISO 8601). Overrides `--since`. |
| `--end` | Absolute end time (ISO 8601). Defaults to now if `--start` is set. |
| `--cluster` | ECS cluster name. Default: `n8n-cluster` |
| `--region` | AWS region. Default: `us-east-2` |
| `--metrics` | Specific metric names to fetch (space-separated). |
| `--ecs-only` | Only fetch standard ECS metrics (CPUUtilization, MemoryUtilization). |
| `--insights-only` | Only fetch Container Insights metrics. |
| `--output FILE`, `-o FILE` | Write output to FILE as JSON. Default: stdout. |
| `--pretty` | Pretty-print JSON output. |
| `--summary` | Print human-readable summary table instead of JSON. |

## Available Metrics

### Standard ECS (`--ecs-only`)
- `CPUUtilization` -- percentage of CPU used
- `MemoryUtilization` -- percentage of memory used

### Container Insights (`--insights-only`)
- `CpuUtilized` / `CpuReserved` -- CPU units utilized vs reserved
- `MemoryUtilized` / `MemoryReserved` -- MB of memory utilized vs reserved
- `RunningTaskCount` / `DesiredTaskCount` / `PendingTaskCount` -- task counts
- `NetworkRxBytes` / `NetworkTxBytes` -- network I/O bytes
- `EphemeralStorageUtilized` / `EphemeralStorageReserved` -- ephemeral storage GB
- `StorageReadBytes` / `StorageWriteBytes` -- storage I/O bytes

## What the Script Does

1. Connects to AWS CloudWatch via boto3 (standard credential chain)
2. Queries the `AWS/ECS` and/or `ECS/ContainerInsights` namespaces
3. Auto-selects period based on time range (60s for <=1h, 300s for <=24h, 3600s for >24h)
4. Returns Average, Maximum, Minimum (and Sum for Insights) statistics per datapoint
5. In `--summary` mode, shows min/max/mean of each statistic plus the peak timestamp

## Common Debugging Patterns

### Correlating with log errors
Pair with log fetcher scripts to investigate incidents:
```bash
# 1. Fetch error logs
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_n8n_logs.py --since 1h --query "service:n8n status:error" --pretty

# 2. Check metrics around the error time window
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py n8n-service --start <error_start> --end <error_end> --summary
```

### Checking for OOM or CPU saturation
```bash
# Check if memory approached the reserved limit
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py <service> --since 6h --metrics MemoryUtilized MemoryReserved --summary

# Check CPU saturation
source mastra/scripts/debug/.venv/bin/activate && python mastra/scripts/debug/scripts/fetch_ecs_metrics.py <service> --since 6h --metrics CpuUtilized CpuReserved --summary
```
