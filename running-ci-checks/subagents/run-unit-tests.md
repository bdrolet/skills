---
name: run-unit-tests
description: Run Vitest unit tests in the mastra directory and report pass/fail.
model: fast
---

# Run Unit Tests

Run the unit tests and report the result.

## Steps

1. Run the unit tests:
   ```
   npm run test:unit
   ```
   Working directory: `mastra/`

2. Wait for the command to complete.

## Output

Return exactly:
- **Check**: unit-tests
- **Result**: PASS or FAIL
- **Error output** (only on FAIL): the last 80 lines of output from the command
