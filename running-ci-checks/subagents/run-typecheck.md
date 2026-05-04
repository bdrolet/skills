---
name: run-typecheck
description: Run TypeScript type checking in the mastra directory and report pass/fail.
model: fast
---

# Run TypeScript Type Check

Run the TypeScript type check and report the result.

## Steps

1. Run the type check:
   ```
   npm run typecheck
   ```
   Working directory: `mastra/`

2. Wait for the command to complete.

## Output

Return exactly:
- **Check**: typecheck
- **Result**: PASS or FAIL
- **Error output** (only on FAIL): the last 80 lines of output from the command
