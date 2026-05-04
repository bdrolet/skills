---
name: run-lint
description: Run ESLint in the mastra directory and report pass/fail.
model: fast
---

# Run Lint

Run the linter and report the result.

## Steps

1. Run the linter:
   ```
   npm run lint
   ```
   Working directory: `mastra/`

2. Wait for the command to complete.

## Output

Return exactly:
- **Check**: lint
- **Result**: PASS or FAIL
- **Error output** (only on FAIL): the last 80 lines of output from the command
