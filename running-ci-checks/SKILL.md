---
name: running-ci-checks
description: Use when committing changes to a PR, running CI checks locally, verifying typecheck/lint/test/build pass, or pre-flight checking before push.
---

# Running CI Checks

Run the same checks as the GitHub Actions CI pipeline (`.github/workflows/mastra-1-ci.yml`) locally before committing to a PR.

## Checks

| Check | Command | Working Directory |
|-------|---------|-------------------|
| Type Check | `npm run typecheck` | `mastra/` |
| Lint | `npm run lint` | `mastra/` |
| Unit Tests | `npm run test:unit` | `mastra/` |
| Build | `npm run build` | `mastra/` |

## Prerequisites

Both `packages/mastra-api` and `mastra/` must have dependencies installed. If `node_modules` is missing or stale, run:

```bash
npm ci --prefix packages/mastra-api && npm ci --prefix mastra
```

## Workflow

### Step 1: Run all checks in parallel

Launch 4 subagents simultaneously via the Task tool in a **single message** (one tool call per check):

- [subagents/run-typecheck.md](subagents/run-typecheck.md) -- `subagent_type: shell`, `model: fast`
- [subagents/run-lint.md](subagents/run-lint.md) -- `subagent_type: shell`, `model: fast`
- [subagents/run-unit-tests.md](subagents/run-unit-tests.md) -- `subagent_type: shell`, `model: fast`
- [subagents/run-build.md](subagents/run-build.md) -- `subagent_type: shell`, `model: fast`

Each subagent returns: check name, pass/fail, and error output (last 80 lines) on failure.

### Step 2: Report results

Summarize pass/fail for all 4 checks. If all pass, proceed to commit.

### Step 3: Diagnose and fix failures

For each failing check, launch a [subagents/diagnose-failure.md](subagents/diagnose-failure.md) subagent (use the default model, not `fast`). Pass it:
- The check name that failed
- The error output from the runner subagent
- The list of files changed in the current conversation

If multiple checks failed, launch one diagnose-failure subagent per failing check in parallel.

The subagent returns a root cause summary, proposed fix (file paths + changes), and confidence level. If confidence is **low**, ask the user before applying the fix.

### Step 4: Apply fixes and re-run

Apply the proposed fixes, then re-run only the previously-failing check subagent(s). Repeat from Step 2 until all checks pass or the agent cannot resolve the issue (escalate to the user).

### Step 5: Commit and push

Once all checks pass, if any fixes were applied during Step 3-4:

1. Stage the fixed files with `git add`.
2. Commit with a message describing the fixes (e.g., `fix: resolve typecheck and lint errors`).
3. Push to the remote branch: `git push origin <current-branch>`.

If no fixes were needed (all checks passed on the first run), skip this step -- the caller (e.g., the pr-commit skill) handles the commit.
