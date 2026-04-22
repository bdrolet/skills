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

8. **Update Jira ticket**

   After a successful merge, find and resolve the associated Jira ticket using the **Atlassian MCP** (`plugin-atlassian-atlassian`).

   **Find the ticket key.** Check these sources in order:
   - PR title — the pr-open skill formats titles as `[TICKET-KEY]: description`, so extract the key from brackets.
   - PR body — look for a `**Ticket:**` line or bare ticket keys (uppercase letters, hyphen, digits like `DEVOPS-123`).
   - Commit messages on the PR.

   ```bash
   TICKET_KEY=$(gh pr view "$PR_NUMBER" --json title --jq '.title' | grep -oE '^\[[A-Z]+-[0-9]+\]' | tr -d '[]')
   if [ -z "$TICKET_KEY" ]; then
     TICKET_KEY=$(gh pr view "$PR_NUMBER" --json body --jq '.body' | grep -oE '[A-Z]+-[0-9]+' | head -1)
   fi
   ```

   If no ticket key is found, skip this step.

   **Verify the ticket exists and check its status** via MCP:
   - Use `getJiraIssue` with `cloudId: "homewardhealth.atlassian.net"` and `issueIdOrKey: "<TICKET_KEY>"`.

   **Determine if the PR completes the ticket's work.** Compare the ticket's summary/description against the PR's changes. The PR completes the ticket if the merged changes satisfy the work described in the ticket (the ticket doesn't need to describe every line — intent-level match is sufficient). If the PR is a partial contribution to a larger ticket, do **not** close it — add a comment instead.

   **Transition the ticket to Done** if the PR completes the work:
   - Use `getTransitionsForJiraIssue` to list available transitions and find the `Done` transition ID.
   - Use `transitionJiraIssue` with the transition `id` to move the ticket to Done.
   - If `Done` is not available, look for `Closed` or another terminal state.

   **Add a comment** linking the merged PR:
   - Get the PR URL: `gh pr view "$PR_NUMBER" --json url --jq .url`
   - Use `addCommentToJiraIssue` with `commentBody: "Merged via PR: <PR_URL>"` and `contentFormat: "markdown"`.

   If any Jira step fails, log the error but do not fail the overall merge — the PR is already merged and the title contains the ticket key for traceability.

