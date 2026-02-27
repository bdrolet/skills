---
name: pr-post
description: Post Comment to PR
disable-model-invocation: true
---

# Post Comment to PR

## Overview

Automate the workflow: verify the current branch is associated with an open PR, summarize the response from the current prompt, gather commands and output from the current response only, and post a formatted comment to the PR using GitHub CLI.

## Steps

1. **Verify current branch has an open PR:**
   - Get the current branch name: `git branch --show-current`.
   - Check if there's an open PR for this branch: `gh pr list --head <branch-name> --state open`.
   - Extract the PR number from the output (e.g., `gh pr view --json number --jq '.number'`).
   - If no open PR is found, stop execution and inform the user that the command requires an open PR.
   - If an open PR exists, proceed to the next step.

2. **Summarize the response from the current prompt:**
   - Review only the current prompt and its response to understand what was accomplished.
   - Create a concise summary that captures the main points of this specific response.
   - Focus on key changes, decisions, or outcomes from the current interaction.
   - If the context is unclear, ask the user for a brief summary.
   - **Security**: Do NOT include any sensitive data (API keys, passwords, secrets, tokens, credentials) in the summary.

3. **Gather commands and output from the current response:**
   - Review only the current response to identify any commands that were executed in this specific interaction.
   - Extract command outputs, error messages, or important results from the current response only.
   - Do NOT include commands or outputs from previous conversation turns.
   - **Security**: Before including any commands or outputs, sanitize and remove any sensitive data such as API keys, passwords, secrets, tokens, credentials, or authentication information. Redact or omit sensitive portions of command outputs.
   - Format commands and outputs in code blocks for readability.
   - Include relevant file paths, line numbers, or other contextual information from the current response.
   - Format code references for GitHub: use GitHub's markdown syntax to create links to files and specific line numbers (e.g., `[filename.ext:12-15](link-to-file#L12-L15)` or use GitHub's automatic linking format).
   - When referencing code, prefer GitHub permalinks or relative file paths that will render as clickable links in the PR comment.

4. **Format and post the comment:**
   - Create a well-formatted markdown comment with:
     - A summary section at the top
     - A section for commands executed (if any)
     - A section for outputs/results (if any)
     - Use appropriate markdown formatting (headers, code blocks, lists)
   - **Security**: Perform a final review to ensure no sensitive data (API keys, passwords, secrets, tokens, credentials) is included in any part of the comment before posting.
   - Post the comment to the PR: `gh pr comment <pr-number> --body "<formatted-comment>"`.
   - Ensure the comment body is properly escaped for shell execution.

## Requirements

- `git` installed and configured.
- `gh` CLI installed and authenticated.
- Must be in a git repository with write access.
- Current branch must be associated with an open PR.

