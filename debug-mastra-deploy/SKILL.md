---
name: debug-mastra-deploy
description: Check GitHub Actions workflow status for the Mastra CI/CD pipeline stages (CI, Build, Staging, Production). Use when the user asks about deploy status, workflow failures, build status, CI results, or wants to debug a failed GitHub Actions run.
---

# Debug Mastra Deploy

Check the latest GitHub Actions run for any Mastra pipeline stage, see if it passed or failed, and retrieve failure logs.

## Prerequisites

- `GITHUB_TOKEN` must be set in `mastra/scripts/debug/.env` (PAT with `actions:read` scope)
- Python dependencies installed: `pip install -r mastra/scripts/debug/requirements.txt`

## Usage

Run from the project root:

```bash
python3 mastra/scripts/debug/scripts/check_gha_workflow.py <stage>
```

## Available stages

| Stage | Aliases | Workflow file |
|-------|---------|---------------|
| `ci` | `1` | `mastra-1-ci.yml` |
| `build` | `2` | `mastra-2-build.yml` |
| `staging` | `3`, `stg` | `mastra-3-staging.yml` |
| `production` | `4`, `prod` | `mastra-4-production.yml` |

## Examples

```bash
# Check CI
python3 mastra/scripts/debug/scripts/check_gha_workflow.py ci

# Check production deploy
python3 mastra/scripts/debug/scripts/check_gha_workflow.py prod

# Check staging, only main branch, more log lines
python3 mastra/scripts/debug/scripts/check_gha_workflow.py staging --branch main --tail 500

# Check build, only show a specific job's logs
python3 mastra/scripts/debug/scripts/check_gha_workflow.py build --job "Build and Push"

# Quick pass/fail check without downloading logs
python3 mastra/scripts/debug/scripts/check_gha_workflow.py production --no-logs
```

## Useful flags

| Flag | Description |
|------|-------------|
| `--branch`, `-b` | Filter to runs on a specific branch |
| `--tail N`, `-t N` | Last N lines per log file (default 200, `0` = full) |
| `--job NAME`, `-j NAME` | Only show logs matching this job name |
| `--no-logs` | Skip log download, just show job/step failure summary |
| `--repo OWNER/REPO` | Override the GitHub repo |
| `--list`, `-l` | List all stages and aliases |

## What the script does

1. Fetches the latest run for the chosen workflow
2. Prints a summary: run ID, status, conclusion, branch, commit, trigger, timestamp, URL
3. If still running, reports status and exits
4. If succeeded, confirms and exits (exit code 0)
5. If failed, shows which jobs and steps failed, then downloads and prints the logs (exit code 1)
