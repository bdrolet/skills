---
name: pr-update-description
description: Update PR Description
disable-model-invocation: true
---

# Update PR Description

## Overview

Update the pull request description so other engineers can understand what was changed and why. Use chat context, documentation links, reasoning, and a full view of the diff to produce a clear, engineer-focused description.

## Steps

1. **Gather context**
   - Review the current chat: decisions made, problems solved, tradeoffs discussed.
   - Run `git diff` (or `git diff main...HEAD` / `git diff <base-branch>...HEAD`) to see all changes in the PR.
   - Optionally run `git diff --stat` for a high-level summary of touched files.

2. **Structure the description**
   - **Summary**: 1–2 sentences on the goal of the PR.
   - **What changed**: Bullet list of main changes (features, fixes, refactors) with brief "why" where it helps.
   - **Reasoning**: Short explanation of approach, alternatives considered, and any caveats.
   - **Documentation**: Add links to external docs, specs, or references used (e.g. Datadog, framework docs, RFCs).
   - **Testing / verification**: How to validate the change (commands, manual steps, or test coverage).

3. **Write for engineers**
   - Use clear, technical language; avoid marketing speak.
   - Call out breaking changes, config/env changes, and migration steps.
   - Mention file or area names when they clarify scope (e.g. "Logger and Datadog integration in `src/lib/`").

4. **Output**
   - Provide the full PR description text (markdown) ready to paste into GitHub/GitLab.
   - Provide a short PR title.

5. **Update the PR with GitHub CLI**
   - After the description and title are finalized, update the PR using `gh`:
     - **Title**: `gh pr edit --title "Your PR title here"`
     - **Body**: Write the description to a temp file (e.g. `pr-description.md`), then run:
       `gh pr edit --body-file pr-description.md`
     - **Both at once**: `gh pr edit --title "Your PR title" --body-file pr-description.md`
   - If the current branch has an associated PR, `gh pr edit` with no number applies to it. To target a specific PR: `gh pr edit <number> --title "..." --body-file ...`
   - Confirm success with `gh pr view` (optionally `gh pr view --web` to open in browser).
   - Remove the temp body file after the edit if one was created.

## Requirements

- Git available; run from repo root or branch that represents the PR.
- [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated (`gh auth status`). The branch must have an open PR, or pass the PR number explicitly.
- Access to chat history and (if needed) key docs so links and reasoning are accurate.

## Checklist

- [ ] Chat context and reasoning reflected in the description
- [ ] Git diff reviewed so nothing important is missing from "What changed"
- [ ] External documentation links included where relevant
- [ ] Description is understandable by engineers who didn't work on the PR
- [ ] Breaking changes, config, and migration steps called out if any
- [ ] PR title and description updated via `gh pr edit`
