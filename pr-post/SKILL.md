---
name: pr-post
description: Post Comment to PR
disable-model-invocation: true
---

# Post Comment to PR

## Overview

Automate the workflow: verify the current branch is associated with an open PR, summarize the response from the current prompt, gather commands and output from the current response only, and post a formatted comment to the PR using GitHub CLI.

## ⚠️ CRITICAL: PHI and Security Review (Do This Before Every Post)

**This is a non-negotiable gate. Do NOT post until every check below passes.**

### PHI (Protected Health Information) — MUST be removed or masked

PHI includes any data that could identify a real patient. Before posting, scan all content for:

| PHI Type | Examples | Action |
|----------|---------|--------|
| Full names | "Karen Attwater", "John Smith" | Replace with `[MEMBER NAME]` |
| Dates of birth | "DOB: 01/15/1952" | Replace with `[DOB]` |
| Addresses | "123 Main St, Columbus OH" | Replace with `[ADDRESS]` |
| Phone/fax numbers | "(614) 555-1234" | Replace with `[PHONE]` |
| Email addresses (member/patient) | "patient@email.com" | Replace with `[EMAIL]` |
| Insurance / member plan IDs | "INS-00123456" | Replace with `[PLAN ID]` |
| Athena IDs / EHR identifiers | "athenaId: 98765" | Replace with `[EHR ID]` |
| MRNs / claim numbers | | Replace with `[MRN]` / `[CLAIM ID]` |
| Clinical notes or diagnoses | Response text from AI dispatcher containing health info | Summarize at high level or omit |
| MNS scores tied to a named member | "MNS score of 4 for Karen Attwater" | Remove the name; score alone is OK |
| Any AI-generated response text that contains member health narrative | Engagement Call Snapshots, clinical summaries | Do NOT paste verbatim — describe the shape/length only |

**Key rule for AI dispatcher response text:** Never paste the full or partial text of an AI-generated member summary into a PR comment. Instead, describe it structurally (e.g., "response contained a 4,027-character engagement snapshot with visit scheduling goals and clinical context sections").

### Credentials and Secrets — MUST be removed

- API keys, tokens, bearer tokens
- Database passwords or connection strings
- AWS credentials, session tokens
- Any value from `.env` files

---

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
   - **PHI**: Do NOT include any PHI — names, dates, IDs, health information, or AI-generated member narratives.

3. **Gather commands and output from the current response:**
   - Review only the current response to identify any commands that were executed in this specific interaction.
   - Extract command outputs, error messages, or important results from the current response only.
   - Do NOT include commands or outputs from previous conversation turns.
   - **Security**: Before including any commands or outputs, sanitize and remove any sensitive data such as API keys, passwords, secrets, tokens, credentials, or authentication information. Redact or omit sensitive portions of command outputs.
   - **PHI**: Before including any output, apply the PHI review table above. Replace all PHI with the appropriate placeholder. Never include raw AI dispatcher response text — describe it structurally instead.
   - Format commands and outputs in code blocks for readability.
   - Include relevant file paths, line numbers, or other contextual information from the current response.
   - Format code references for GitHub: use GitHub's markdown syntax to create links to files and specific line numbers (e.g., `[filename.ext:12-15](link-to-file#L12-L15)` or use GitHub's automatic linking format).
   - When referencing code, prefer GitHub permalinks or relative file paths that will render as clickable links in the PR comment.

4. **Final PHI + security gate before posting:**
   - Read the full draft comment one more time top to bottom.
   - Confirm: no real member names, no health narratives, no EHR/insurance IDs, no credentials.
   - If any PHI or credential is found at this stage, remove or mask it before proceeding.
   - Only after this review passes, post the comment.

5. **Format and post the comment:**
   - Create a well-formatted markdown comment with:
     - A summary section at the top
     - A section for commands executed (if any)
     - A section for outputs/results (if any)
     - Use appropriate markdown formatting (headers, code blocks, lists)
   - Post the comment to the PR: `gh pr comment <pr-number> --body "<formatted-comment>"`.
   - Ensure the comment body is properly escaped for shell execution.

## Requirements

- `git` installed and configured.
- `gh` CLI installed and authenticated.
- Must be in a git repository with write access.
- Current branch must be associated with an open PR.
