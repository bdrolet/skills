---
name: reviewing-pr-code
description: Review a GitHub pull request for code quality, bugs, security issues, and style. Use when the user wants to review a PR, do a code review, analyze PR changes, check a pull request for issues, leave review comments on a PR, or asks about reviewing code in a GitHub pull request — even if they just paste a PR URL or say "review this".
---

# Reviewing PR Code

Review the code in a GitHub pull request and post inline review comments via the GitHub API.

Read each agent's instruction file from `agents/` before spawning it.

## Phase 1: Identify the PR

Determine the PR number, owner, and repo. In order of preference:

1. User provides a PR URL or number directly — parse owner/repo/number from the URL
2. Current branch has an open PR — detect with `gh pr view --json number,url -q '.number'`
3. Ask the user

Parse `owner` and `repo` from `git remote get-url origin` if not already known.

## Phase 2: Gather context (fast model)

Spawn **gather-context** (`agents/gather-context.md`). Pass `owner`, `repo`, `pr_number`.

It returns: PR metadata (including `headRefOid` and `headRefName`), the full diff, existing review comments, existing reviews, and any supplemental file contents for truncated diffs.

## Phase 3: Analyze the code (default model)

Spawn **analyze-code** (`agents/analyze-code.md`). Pass it everything from Phase 2:

- `pr_title` and `pr_body` from the metadata
- `diff` — the full diff
- `files` — the list of changed files with addition/deletion counts
- `existing_comments` — prior review comments (so it doesn't duplicate feedback)
- `existing_reviews` — prior review submissions
- `supplemental_files` — full file contents for any truncated diffs
- `head_branch` — the PR's head branch name
- `owner` and `repo` — for any additional file fetches it might need
- `tone` — the user's tone preference (default: `"supportive"`)

It returns: a summary, a list of findings (each with file, line, severity, category, comment body), and a list of any files it skipped.

Present the analysis to the user before posting. This gives them a chance to adjust, remove findings they disagree with, or add their own observations. Proceed to Phase 4 only when the user confirms (or if they asked you to post directly without review).

## Phase 4: Post the review (fast model)

Spawn **post-review** (`agents/post-review.md`). Pass:

- `owner`, `repo`, `pr_number`
- `commit_sha` — the `headRefOid` from Phase 2 metadata
- `summary` — the overall review summary from Phase 3
- `findings` — the list of findings from Phase 3 (after any user edits)

It posts the review atomically via the GitHub API and returns the review URL and counts of posted/dropped comments.

Share the review URL with the user when done.

## Tone

The default tone is supportive and constructive. If the user requests a different tone, pass it through to the analyze-code agent:

- **supportive** (default): Acknowledge what's good, frame suggestions as improvements
- **direct**: Professional and concise, no padding
- **thorough**: Extra detail on every finding with code examples

## Error handling

- If **gather-context** fails, check `gh auth status` and retry.
- If **analyze-code** returns no findings, still post a review with just the summary (a clean review is useful signal).
- If **post-review** drops comments due to line number errors, report which ones were dropped so the user can post them manually if needed.
- If the diff is very large (>2000 lines), **analyze-code** may skip some files — it will report which ones. Mention this to the user so they know the review isn't exhaustive.
