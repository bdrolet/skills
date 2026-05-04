---
name: diagnose-failure
description: Analyze CI check error output, identify root cause, and propose a concrete fix.
---

# Diagnose CI Failure

Given error output from a failing CI check, identify the root cause and propose a specific fix.

## Inputs

You will be provided:
- **Check name**: which check failed (typecheck, lint, unit-tests, or build)
- **Error output**: the stderr/stdout from the failing command
- **Changed files**: the list of files modified in the current conversation

## Steps

1. Parse the error output to identify the failing file(s) and error message(s).
2. Read the failing file(s) to understand the context around the error.
3. Cross-reference with the list of changed files -- the issue is most likely in a recently changed file.
4. Determine the root cause and formulate a fix.

## Output

Return exactly:

- **Check**: the check name that failed
- **Root cause**: 1-2 sentence summary of why the check failed
- **Confidence**: high, medium, or low
  - **high**: the fix is straightforward and unambiguous (e.g., missing import, typo, unused variable)
  - **medium**: the fix is likely correct but touches logic or has minor ambiguity
  - **low**: multiple possible fixes exist, or the change could affect behavior in non-obvious ways
- **Fix**: for each file that needs changing, provide:
  - File path
  - The exact string to find (old_string)
  - The exact replacement string (new_string)
