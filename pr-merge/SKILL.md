---
name: pr-merge
description: PR Merge (pr-merge)
disable-model-invocation: true
---

# PR Merge (pr-merge)

## Overview

Guide to squash-merge the PR for the current branch with a clear, PR-linked commit message that ends with `(#<PR_NUMBER>)`. GitHub links the commit to the PR when the subject line ends with `(#[PR])` per GitHub merge commit conventions.

## Steps

1. **Prep environment**
   - Start from repo root; ensure no staged/modified tracked files that would block merge (untracked files are fine).
   - `git status` should show nothing to commit for tracked files; `git pull` to refresh.

2. **Check required tools**
   - GitHub CLI: `gh --version` (must be authenticated).
   - Git: `git --version`.

3. **Identify PR for current branch**
   - `BRANCH=$(git branch --show-current)`
   - `PR_NUMBER=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number')`
   - If empty, fall back: `PR_NUMBER=$(gh pr view --json number --jq .number)`; stop if still empty.

4. **Collect context for summary**
   - Review PR details: `gh pr view "$PR_NUMBER" --json title,body,comments,files --jq '{title,body,comments:[.comments[].body],files:[.files[].path]}'`
   - Review diff if needed: `gh pr diff "$PR_NUMBER" | less`
   - Skim recent PR comments for highlights/risk areas.

5. **Draft commit message**
   - Write a one-line subject summarizing the merged changes; keep <= 72 chars.
   - **Suffix the subject with `(#$PR_NUMBER)`** so GitHub links the commit to the PR.
   - Example: `SUBJECT="Harden mastra prod ALB rule and SG ingress (#$PR_NUMBER)"`
   - Optional body: short bullets of key changes/risks/tests (omit if not needed).

6. **Merge with squash**
   - Run with custom subject/body:
     - `gh pr merge "$PR_NUMBER" --squash --subject "$SUBJECT" --body "$BODY"`
   - If no body, you can pass `--body ""` to avoid reusing the PR body.

7. **Post-merge checks**
   - Verify merge success: `gh pr view "$PR_NUMBER" --json state --jq .state` should be `MERGED`.
   - Confirm branch cleanup if desired: `gh pr merge ... --delete-branch` (optional) or `git branch -d "$BRANCH"` after pulling.
   - If merge failed, capture error output and retry after resolving blockers.

