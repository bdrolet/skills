---
name: reviewing-pr-comments
description: Use when the user wants to read, review, summarize, or address PR comments, code review feedback, or review suggestions on a GitHub pull request
---

# Reviewing PR Comments

Fetch, summarize, and optionally address review comments on a GitHub pull request.

Read each agent's instruction file from `agents/` before spawning it.

## Phase 1: Identify the PR

Determine the PR number, owner, and repo. In order of preference:

1. User provides a PR URL or number directly
2. Current branch has an open PR — detect with `gh pr view --json number,url -q '.number'`
3. Ask the user

Parse `owner` and `repo` from `git remote get-url origin`.

## Phase 2: Fetch and categorize (sequential)

### Step 1 — Fetch comments (fast model)

Spawn **fetch-comments** (`agents/fetch-comments.md`). Pass `owner`, `repo`, `pr_number`.

### Step 2 — Categorize (default model)

Spawn **categorize-comments** (`agents/categorize-comments.md`). Pass the three output sections from step 1.

Present the categorized summary to the user. Stop here unless the user requests fixes.

## Phase 3: Address comments (user-initiated)

When the user selects which comments to fix:

### Step 3 — Fix code (default model)

Spawn **fix-code** (`agents/fix-code.md`). Pass `repo_dir` and the list of actionable comments the user selected, each with `file`, `line`, `request`, and `comment_id`.

### Step 4 — Commit and reply (parallel, fast model)

After fixes are applied, spawn these two in parallel:

- **commit-and-push** (`agents/commit-and-push.md`): Pass `repo_dir`, `files_modified` from step 3, and a summary of the fixes.
- **reply-to-comments** (`agents/reply-to-comments.md`): Pass `owner`, `repo`, `pr_number`, and for each fixed comment its `comment_id` and `fix_description` from step 3.

If step 3 skipped any comments, include those in the reply list with the skip reason.

## Error handling

- If **fetch-comments** fails, check `gh auth status` and retry.
- If **fix-code** fails or skips all items, still run **reply-to-comments** to explain what happened.
- If **commit-and-push** fails on pre-push hooks, retry with `--no-verify` if the errors are pre-existing.
