---
name: test-log-snapshot
description: Verify that AI Dispatcher snapshot call logging is working correctly by calling the dispatcher and checking nav_gpt.snapshot_calls for the expected row. Use when the user wants to verify snapshot logging, check snapshot_calls writes, test reportSnapshotCall, or validate snapshot DB entries after dispatcher calls.
---

# Test Log Snapshot

Run AI Dispatcher calls and verify that `nav_gpt.snapshot_calls` rows are written with the correct `snapshot_id`, `snapshot_name`, `member_id`, and `from_cache` values.

## Quick Start

```bash
source mastra/scripts/debug/.venv/bin/activate && python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --check-snapshot-db --target mastra-prod
```

This calls all 8 dispatcher types against production and verifies a snapshot row appears in the database after each call.

## How It Works

For each dispatcher call, the test:
1. Records the current UTC time before calling
2. Calls the dispatcher endpoint
3. Queries `nav_gpt.snapshot_calls` for a row matching `member_id`, expected `snapshot_id`, and `created_at >= call_time`
4. Validates `snapshot_name` matches the expected value

Results appear in a **Snapshot** column in both the terminal summary and HTML report.

## Expected Snapshot IDs

Each dispatcher type maps to a specific `snapshot_id` and `snapshot_name` (mirroring `SNAPSHOT_REGISTRY` in `mastra/src/lib/constants.ts`):

| Dispatcher Type | snapshot_id | snapshot_name |
|----------------|-------------|---------------|
| initial-engagement | `ADm8nPVjVE7fH7u4` | Initial Engagement |
| welcome-call | `mTXE4vaX8qnSoX8G` | Welcome Call |
| toc-admit | `RWaEMxEYmoIVRYno` | TOC Admit |
| toc-discharge | `zrI0G6J5F4OugdDu` | TOC Discharge |
| general-member-snapshot | `X7LZzdStXFp0wqRl` | General Member |
| chronic-heart-failure | `jwPRHCCI7hNO7H9D` | CHF Failure |
| new-stew-member-benefits | `JoI3gUAdJDpXPF8U` | New Stew Member Benefits |
| otc-benefits | `JoI3gUAdJDpXPF8U` | OTC Benefits |

## Examples

```bash
source mastra/scripts/debug/.venv/bin/activate

# All types against production with snapshot verification
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --check-snapshot-db --target mastra-prod

# Single type, verbose
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --check-snapshot-db --target mastra-prod -t ie -v

# Subset of types
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --check-snapshot-db --target mastra-prod -t ie -t wc -t snapshot

# Via n8n (n8n also writes to snapshot_calls)
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --check-snapshot-db --target n8n

# Don't auto-open browser report
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py --check-snapshot-db --target mastra-prod --no-open
```

## Requirements

- `DATABASE_URL_NAV_GPT` must be set in `mastra/scripts/debug/.env` (PostgreSQL connection string to the `n8n_workflow_data` database)
- `psycopg2-binary` must be installed in the venv (`pip install psycopg2-binary`)
- Network access to the n8n-prod RDS instance

## Database

The snapshot rows are written to:
- **Database:** `n8n_workflow_data` (on the n8n-prod RDS)
- **Table:** `nav_gpt.snapshot_calls`
- **Columns:** `id`, `snapshot_id`, `snapshot_name`, `member_id`, `from_cache`, `created_at`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `DATABASE_URL_NAV_GPT env var is required` | Add the connection string to `mastra/scripts/debug/.env` |
| `psycopg2 is required` | Run `pip install psycopg2-binary` in the venv |
| `No snapshot_calls row found` | The dispatcher may not have written the row yet (timing) or the feature is not deployed to the target environment |
| Snapshot FAIL but response PASS | The dispatcher returned a response but did not write to `snapshot_calls` -- check that `reportSnapshotCall` is wired correctly for that type |
