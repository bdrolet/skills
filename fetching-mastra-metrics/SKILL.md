---
name: fetching-mastra-metrics
description: Use when querying Mastra StatsD metrics from Datadog, checking dispatcher volume, snapshot latency, cache hit rates, error rates, or migration progress between n8n and Mastra.
---

# Fetching Mastra Metrics

Query Mastra application metrics via the Datadog MCP. MCP server: `plugin-datadog-datadog`.

## Available Metrics

| Namespace | Metrics | What it measures |
|-----------|---------|-----------------|
| `mastra.dispatcher.*` | `request`, `success`, `error`, `cache_hit`, `duration_ms.*` | AI Dispatcher (all snapshot types). Tags: `type`, `route` |
| `mastra.snapshot.*` | `request`, `success`, `error`, `duration_ms.*` | Generic snapshot step. Tags: `source` (cache/generated) |
| `mastra.snapshot.ie.*` | `request`, `success`, `cache_hit`, `cache_miss`, `duration_ms.*`, `generation_ms.*` | IE-specific. `generation_ms` = agent.generate() time only |
| `mastra.request.*` | `count`, `error_count`, `duration_ms.*` | HTTP request-level |

Duration metrics include `.avg`, `.median`, `.95percentile`, `.max`, `.count` variants.

Data available from approximately March 19, 2026 onward.

## Discover metrics

```json
CallMcpTool: plugin-datadog-datadog / search_datadog_metrics
{ "name_filter": "mastra.*", "from": "now-2w" }
```

## Query patterns

**Daily dispatch volume by snapshot type (last 7 days):**
```json
CallMcpTool: plugin-datadog-datadog / get_datadog_metric
{
  "queries": ["sum:mastra.dispatcher.request{*} by {type}.rollup(sum, 86400)"],
  "from": "now-7d", "to": "now"
}
```

**IE latency (avg + p95, daily):**
```json
{
  "queries": [
    "avg:mastra.snapshot.ie.duration_ms.avg{*}.rollup(avg, 86400)",
    "avg:mastra.snapshot.ie.duration_ms.95percentile{*}.rollup(avg, 86400)"
  ],
  "from": "now-7d", "to": "now"
}
```

**IE generation time vs total duration:**
```json
{
  "queries": [
    "avg:mastra.snapshot.ie.generation_ms.avg{*}.rollup(avg, 86400)",
    "avg:mastra.snapshot.ie.duration_ms.avg{*}.rollup(avg, 86400)"
  ],
  "from": "now-7d", "to": "now"
}
```

**Cache hit rate:**
```json
{
  "queries": [
    "sum:mastra.snapshot.ie.cache_hit{*}.rollup(sum, 86400)",
    "sum:mastra.snapshot.ie.cache_miss{*}.rollup(sum, 86400)"
  ],
  "from": "now-7d", "to": "now"
}
```

**Error rate by type:**
```json
{
  "queries": ["sum:mastra.dispatcher.error{*} by {type}.rollup(sum, 86400)"],
  "from": "now-7d", "to": "now"
}
```

**Hourly granularity (last 24h):**
```json
{
  "queries": ["sum:mastra.dispatcher.request{*} by {type}.rollup(sum, 3600)"],
  "from": "now-24h", "to": "now"
}
```

## Tips

- Use `.rollup(sum, 86400)` for daily totals, `.rollup(sum, 3600)` for hourly.
- Filter by type: `{type:initial-engagement}`, `{type:welcome-call}`, etc.
- Compare success vs request to get failure count: `request - success = failures`.
- `generation_ms` is the LLM call time; `duration_ms` includes cache check + generation + caching.
- Set `max_tokens: 10000` for large responses with many types/days.
