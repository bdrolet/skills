---
name: pr-commit
description: Commit and Push to PR Branch
disable-model-invocation: true
---

# Commit and Push to PR Branch

## Overview

Automate the workflow: verify the current branch is associated with an open PR, stage files changed in the conversation, commit with an appropriate message, and push to the remote branch.

## Steps

1. **Verify current branch has an open PR:**
   - Get the current branch name: `git branch --show-current`.
   - Check if there's an open PR for this branch: `gh pr list --head <branch-name> --state open`.
   - If no open PR is found, stop execution and inform the user that the command requires an open PR.
   - If an open PR exists, proceed to the next step.

2. **Identify and stage only files changed in this conversation:**
   - Review the conversation to identify which specific files were modified or created.
   - Only stage files that were actually changed in the current chat session.
   - Use `git add <file>` for each file that was changed.
   - Do NOT stage files that were not modified in this conversation (even if they show as uncommitted).
   - Do NOT stage files that are ignored by `.gitignore` (e.g., `*.tfvars`, `.terraform/`, lockfiles) even via force-add.
   - Do NOT stage temporary files like `.tfplan`, `.bak`, or documentation files like `PERMISSIONS_REQUEST.md`, `PR_summary.md`.

3. **Commit staged changes:**
   - **Extract commit message from conversation context:**
     - Review the conversation history to understand what changes were made.
     - Create a concise commit message that follows conventional commit format (e.g., "feat: add new RDS instance", "fix: update ECS task definition", "chore: update security group rules").
     - If the context is unclear, ask the user for a brief commit message.
   - **Commit changes**: `git commit -m "commit-message"`.

4. **Push to remote branch:**
   - Push the committed changes: `git push origin <branch-name>`.

## Requirements

- `git` installed and configured.
- `gh` CLI installed and authenticated.
- Must be in a git repository with write access.
- Current branch must be associated with an open PR.

