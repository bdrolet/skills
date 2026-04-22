---
name: creating-datadog-dashboards
description: >
  Use when creating or modifying a Datadog dashboard via Terraform, adding
  widgets or metrics to a datadog_dashboard resource, setting metric metadata
  units, or debugging why a Datadog dashboard shows no data.
---

# Creating Datadog Dashboards via Terraform

## Provider & Pattern

Dashboards live as `datadog_dashboard` resources in environment stacks (e.g., `environments/production/mastra/`). No shared modules -- inline HCL. Provider: `DataDog/datadog ~> 3.46`, site: `api.us5.datadoghq.com`.

## Dashboard Resource Structure

Use `layout_type = "ordered"`, a `template_variable` for `$env` (prefix `env`, defaults `["production"]`), and `tags` restricted to org-allowed keys. See existing `datadog_dashboard` resources in this repo for the full skeleton.

## Gotchas (ordered by how likely you'll hit them)

### 1. Dashboard tags are restricted
Datadog orgs can restrict which tag keys are allowed on dashboards. This org allows `team` and `ai` only. Tags like `service:*` or `feature:*` will fail with `400 Bad Request: Invalid tag format`. Check existing dashboards for precedent.

### 2. Never set `live_span` on timeseries widgets
Setting `live_span` on individual widgets **overrides the global time picker** at the top of the dashboard. Users lose the ability to change the time range. Only set `live_span` on `query_value_definition` widgets that show fixed-window summaries (e.g., "Request Count (4h)").

### 3. Query syntax: `by {tag}` goes BEFORE `.as_count()`
```
CORRECT:  sum:metric{*} by {error_type}.as_count()
WRONG:    sum:metric{*}.as_count() by {error_type}
```
The wrong form produces a Datadog API parse error.

### 4. Timing metrics auto-generate aggregations — but not all of them
DogStatsD `timing` metrics create: `.avg`, `.median`, `.95percentile`, `.max`, `.count`. There is **no `.99percentile`** unless you explicitly enable percentile aggregations in Datadog metric config. Use `search_datadog_metrics` with `name_filter` to confirm which aggregations exist before writing queries.

### 5. Register `datadog_metric_metadata` for every duration aggregation
Without metadata, Y-axes render as raw numbers instead of formatted time. Use `datadog_metric_metadata` with `unit = "millisecond"` for each aggregation (`.avg`, `.median`, `.95percentile`, `.max`). Use `for_each` over a locals list. Always add `lifecycle { ignore_changes = [type, statsd_interval] }` to prevent Terraform from fighting Datadog's auto-detected values. Also add `custom_unit = "ms"` to `query_value_definition` widgets. See existing dashboards for the pattern.

### 6. Template variables filter globally
A `template_variable` with a `prefix` applies that filter to **all** widget queries automatically. You don't need to add `$env.value` to each query -- but the metrics must actually have that tag or everything returns empty.

### 7. Use `-target` during apply to avoid drift
Other resources in the same stack may have drift. Use `-target` on the `datadog_dashboard` and `datadog_metric_metadata` resources to apply only your changes without picking up unrelated diffs.

## Widget Patterns

Use `group_definition` per row. Always include `style {}` on every request, `metadata { expression, alias_name }` on multi-series charts, and `yaxis { include_zero = true }` on all timeseries.

## Debugging "No Data"

1. **Check the time window.** The global picker defaults to "Past 1 Hour." Sparse traffic may not appear. Widen to 4h+.
2. **Verify metrics exist:** `search_datadog_metrics` with `name_filter`.
3. **Verify tag values:** `get_datadog_metric` with `by {tag}` to see actual tag values.
4. **Test the exact query via API:** `get_datadog_metric` with the dashboard query string to confirm data flows.
5. **Check template variable filtering.** If `$env` defaults to `production` but the metric lacks an `env` tag, all queries return empty.
