---
name: annotating-pr-code
description: Use when the PR author wants to add inline explanatory comments to their own pull request, annotate a PR with context about why code was written, or explain their changes to reviewers — especially after an AI-assisted coding session
---

# Annotating PR Code

Add inline comments to a PR explaining the reasoning, decisions, and tradeoffs behind each change. Focus on "why", not "what".

Read each agent's instruction file from `agents/` before spawning it.

## Phase 1: Identify the PR (fast model)

Spawn **identify-pr** (`agents/identify-pr.md`). Pass any PR URL or number the user provided, plus the current working directory as `repo_path`.

If the subagent returns an error (no PR found), ask the user for the PR URL or number, then re-run.

## Phase 2: Gather diff (fast model, parallel with Phase 3)

Spawn **gather-diff** (`agents/gather-diff.md`). Pass `owner`, `repo`, `pr_number` from Phase 1.

## Phase 3: Summarize conversation context (default model, parallel with Phase 2)

Before spawning, extract raw conversation notes yourself from the session history — bullet points covering: what the user asked for, key decisions and reasoning, tradeoffs considered, technical choices ("used X instead of Y because..."), and anything flagged as non-obvious.

Spawn **summarize-context** (`agents/summarize-context.md`). Pass notes as `raw_conversation_notes`.

**Spawn Phases 2 and 3 in parallel** — they are independent.

## Phase 4: Generate explanations (default model)

Wait for both Phase 2 and Phase 3 to complete.

Spawn **generate-explanations** (`agents/generate-explanations.md`). Pass:

- `diff` — the full diff from Phase 2
- `pr_title` and `pr_body` — from Phase 2 metadata
- `files` — the list of changed files from Phase 2
- `context_summary` — the structured summary from Phase 3
- `head_branch` — from Phase 2 metadata

## Phase 5: Present to author (orchestrator)

Show proposed comments to the user (file, line, body for each). Wait for confirmation — the user may approve, remove, edit, or request additions. Proceed to Phase 6 only after confirmation.

## Phase 6: Post comments (fast model)

Spawn **post-comments** (`agents/post-comments.md`). Pass:

- `owner`, `repo`, `pr_number` from Phase 1
- `commit_sha` — the `headRefOid` from Phase 2 metadata
- `comments` — the final list of comments (after user edits in Phase 5)

Share the review URL with the user when done.

## Error handling

| Problem | Fix |
|---|---|
| No PR detected | Ask user for PR URL or number |
| `gh` not authenticated | Run `gh auth status`, report the issue |
| Diff >2000 lines | Warn that annotations may not cover every file |
| Thin conversation context | Proceed with diff/metadata only; warn comments may be less specific |
| Phase 6 drops comments | Report dropped comments so user can post manually |
