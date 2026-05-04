---
name: run-build
description: Run the Mastra build and verify output exists.
model: fast
---

# Run Build

Build the Mastra project and verify the output.

## Steps

1. Run the build:
   ```
   npm run build
   ```
   Working directory: `mastra/`

2. Wait for the command to complete. If it fails, report FAIL immediately with the error output.

3. Verify the build output exists:
   ```
   test -d mastra/.mastra/output && test -f mastra/.mastra/output/index.mjs && echo "Build output verified" || echo "Build output missing"
   ```
   If the output directory or `index.mjs` is missing, report FAIL.

## Output

Return exactly:
- **Check**: build
- **Result**: PASS or FAIL
- **Error output** (only on FAIL): the last 80 lines of build output, or "Build output directory/file missing" if verification failed
