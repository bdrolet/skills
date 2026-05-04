---
name: measure-n8n-errors
description: Measure the error rate of n8n webhook calls from Mastra (e.g. /webhook/mastra-get-member-data). Use when computing or reconciling n8n webhook error rates, investigating reports about Mastra-to-n8n failures, comparing Mastra metrics against n8n logs, or producing a steady-state error rate for any n8n webhook path.
---

# Measure n8n Error Rate

Compute the **technical** and **user-perceived** error rate for any Mastra → n8n webhook call. Mastra emits metrics at three layers, and n8n itself emits logs that capture failures invisible to Mastra. Use all four sources together — none alone is complete.

## Quick start

1. Pick the webhook path (see [`mastra/src/lib/constants.ts`](../../../mastra/src/lib/constants.ts), e.g. `N8N_DEFAULTS.GET_MEMBER_DATA_WEBHOOK_PATH = '/webhook/mastra-get-member-data'`).
2. Query Mastra `n8n_webhook` metrics for **request** and **error** counts (primary source — see Layer 3 below).
3. Cross-check against n8n logs and **divide n8n log counts by 2** (Datadog forwarder duplication, see "Critical pitfalls").
4. Search n8n logs for **soft rejections** (HTTP 200 with refusal body — invisible to Mastra metrics).
5. Compute three rates: hard / soft / combined user-perceived. Report all three.

## The four data sources

| # | Source | What it measures | Reliability |
|---|---|---|---|
| 1 | `mastra.tool.*` metric | Tool-level errors (e.g. `tool:get-member-data`) | **Stopped emitting after Apr 15, 2026** — do not rely on |
| 2 | `mastra.snapshot.*` metric | Workflow step error per snapshot type (`type:chf`, `type:toc-admit`, …) | Good for workflow-level rates, splits by `type` |
| 3 | `mastra.n8n_webhook.*` metric | All webhook calls by `path`, after internal HTTP retries | **Primary source.** One emit per logical call |
| 4 | n8n service logs (`service:n8n`) | n8n's own view: HTTP failures **and** soft rejections | Captures what Mastra metrics miss |

Source code references:
- Layer 3 emit point: [`mastra/src/clients/n8n-client.ts:221-227`](../../../mastra/src/clients/n8n-client.ts)
- Internal retry logic (executes before metric is emitted): [`mastra/src/clients/n8n-client.ts:192-199`](../../../mastra/src/clients/n8n-client.ts)
- Error classifier: [`mastra/src/lib/metrics.ts`](../../../mastra/src/lib/metrics.ts) (`classifyErrorType`)

## Critical pitfalls

1. **n8n logs are double-logged**. Each n8n error appears **twice** in CloudWatch (same timestamp + same internal `id`, different `event_id`). This is a Datadog Forwarder Lambda artifact, not a real duplicate. **Always divide raw n8n log counts by 2.**
2. **Mastra `n8n_webhook.*` is post-retry**. The client retries failed `fetch()` calls before the metric fires, so `n8n_webhook.error` counts logical failures, not HTTP attempts. Don't multiply by retry count.
3. **Soft rejections look like successes**. n8n can return **HTTP 200 with a rejection message in the body** (e.g. `"Only Aetna and BCBSMI members are supported by Homeward AI at this time."`). These increment `n8n_webhook.success`, **not** `n8n_webhook.error`. They only appear in n8n service logs.
4. **`mastra.tool.*` is dead after Apr 15, 2026**. Do not use it for recent data; if you see it referenced, switch to `mastra.snapshot.*` or `mastra.n8n_webhook.*`.
5. **Beware Apr 9, 2026 outage**. ~47.5% error rate for one day (n8n service-wide). Exclude this day when computing steady-state numbers.

## Query recipes

MCP server: `plugin-datadog-datadog`. Replace `$PATH` with the webhook path (e.g. `/webhook/mastra-get-member-data`) and `$RANGE` with a window like `now-14d` → `now`.

### A. Total calls (primary source)

```json
CallMcpTool: get_datadog_metric
{
  "queries": ["sum:mastra.n8n_webhook.request{path:$PATH}.as_count()"],
  "from": "$FROM", "to": "$TO", "interval": 86400
}
```

### B. Hard errors (HTTP failure after retries)

```json
CallMcpTool: get_datadog_metric
{
  "queries": [
    "sum:mastra.n8n_webhook.request{path:$PATH}.as_count()",
    "sum:mastra.n8n_webhook.error{path:$PATH}.as_count()",
    "sum:mastra.n8n_webhook.error{path:$PATH} by {error_type}.as_count()"
  ],
  "from": "$FROM", "to": "$TO", "interval": 86400
}
```

`error_type` values: `webhook_error` (n8n returned non-2xx), `timeout`, `network`, `auth`, `validation`, `unknown`.

### C. Workflow-level errors split by snapshot type

```json
CallMcpTool: get_datadog_metric
{
  "queries": [
    "sum:mastra.snapshot.error{workflow:get-member-data} by {type}.as_count()"
  ],
  "from": "$FROM", "to": "$TO", "interval": 86400
}
```

### D. n8n hard-error logs (cross-check)

```json
CallMcpTool: analyze_datadog_logs
{
  "filter": "service:n8n status:error \"$PATH_BASENAME\"",
  "from": "$FROM", "to": "$TO",
  "sql_query": "SELECT DATE_TRUNC('day', timestamp) AS day, count(*) AS c FROM logs GROUP BY DATE_TRUNC('day', timestamp) ORDER BY day"
}
```

`$PATH_BASENAME` is the last segment, e.g. `mastra-get-member-data`. **Divide the resulting count by 2** to dedupe forwarder duplicates. The deduped count should match Mastra Layer 3 `n8n_webhook.error` within ~5%.

### E. Soft rejections (invisible to Mastra)

Top error message clusters from n8n in the period:

```json
CallMcpTool: analyze_datadog_logs
{
  "filter": "service:n8n status:error",
  "from": "$FROM", "to": "$TO",
  "sql_query": "SELECT message, count(*) AS c FROM logs GROUP BY message ORDER BY c DESC LIMIT 30"
}
```

Look for messages that are **business-rule rejections rather than HTTP failures**. Known patterns:

| Message | Source file in n8n logs | Notes |
|---|---|---|
| `Only Aetna and BCBSMI members are supported by Homeward AI at this time.` | `error-reporter.js` | Worker-level; returns 200 to caller |
| `SQL compilation error: Object 'GEN_AI.PUBLIC.WC_LAST_ENGAGEMENT' does not exist...` | snowflake node | Different workflow, broken table |
| `Request failed with status code 431` | community-nodes fetch | Headers too large; not member-facing |

For each candidate pattern, count its frequency and divide by 2:

```json
CallMcpTool: analyze_datadog_logs
{
  "filter": "service:n8n \"Only Aetna and BCBSMI\"",
  "from": "$FROM", "to": "$TO",
  "sql_query": "SELECT DATE_TRUNC('day', timestamp) AS day, count(*) AS c FROM logs GROUP BY DATE_TRUNC('day', timestamp) ORDER BY day"
}
```

## Computing the rates

After running A, B, D, E:

```
hard_errors      = n8n_webhook.error                       # Layer 3, post-retry
soft_rejections  = (n8n_log_rejections_raw) / 2            # forwarder dedup
total_requests   = n8n_webhook.request

hard_error_rate           = hard_errors      / total_requests
soft_rejection_rate       = soft_rejections  / total_requests
user_perceived_error_rate = (hard_errors + soft_rejections) / total_requests
```

**Always report all three numbers**, plus the breakdown of `error_type` from query B and the top message clusters from query E.

## Validation checklist

Before quoting a final number:

- [ ] Excluded known incident days (e.g. Apr 9, 2026 n8n outage)
- [ ] Divided every n8n log count by 2 (forwarder dedup)
- [ ] Confirmed Mastra Layer 3 errors ≈ deduped n8n hard-error logs (within 5%) — if not, investigate before reporting
- [ ] Checked for soft-rejection patterns in n8n logs (query E) and decided with product whether they count as failures
- [ ] Used Layer 3 (`n8n_webhook`) as the source-of-truth for total call volume and hard errors, not Layer 1 (`mastra.tool.*`)
- [ ] Stated the time window explicitly in the answer

## Reference: known steady-state rates (as of Apr 27, 2026)

For `/webhook/mastra-get-member-data` over Apr 14–27 (~38,700 calls, excluding Apr 9 outage):

| Rate | Value |
|---|---:|
| Hard error rate (HTTP failures) | ~0.5–0.6% |
| Soft rejection rate ("Only Aetna/BCBSMI") | ~0.7–0.8% |
| User-perceived error rate (combined) | ~1.3–1.5% |

Use these as sanity-check baselines; if a fresh measurement deviates significantly, dig into the breakdowns.

## Related skills

- [`fetching-mastra-metrics`](../fetching-mastra-metrics/SKILL.md) — general Datadog metric queries
- [`fetch-n8n-logs`](../fetch-n8n-logs/SKILL.md) — fetch n8n logs via the Python helper script
- [`fetch-mastra-logs`](../fetch-mastra-logs/SKILL.md) — fetch Mastra logs
