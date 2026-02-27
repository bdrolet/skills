---
name: pr-open
description: Open PR (main)
disable-model-invocation: true
---

# Open PR

Automate the full workflow: pull latest from the base branch, create a feature branch named from the conversation context, commit changes, push, and open a PR with a rich description.

## Security

Before staging, committing, or writing PR content, verify that no sensitive data (API keys, passwords, secrets, tokens, credentials) appears in:
- File contents being staged
- Commit messages
- PR title or description

If sensitive data is found, stop and alert the user.

## Phase 1: Understand the changes

Review the conversation history to understand what was done. Extract:
- A **short title** for the PR (e.g., "Add RDS instance for production", "Fix security group rules")
- A **summary** of what changed and why (2–4 sentences)
- The **list of files** that were modified or created in this session

If the context is unclear, ask the user for a brief description before continuing.

## Phase 2: Determine the base branch

Default to `main`. If the repo doesn't have a `main` branch, detect the default:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
```

If that fails, fall back to `master`. If the user specifies a different base branch, use that.

## Phase 3: Stage files

Only stage files that were actually changed in the current conversation session.

- Use `git add <file>` for each changed file individually — do not use `git add .` or `git add -A`.
- Skip files matched by `.gitignore` (e.g., `*.tfvars`, `.terraform/`, lockfiles). Never force-add ignored files.
- Skip temporary/generated files like `.tfplan`, `.bak`, `PERMISSIONS_REQUEST.md`, `PR_summary.md`.

After staging, run `git diff --cached --stat` and confirm the staged files look right before proceeding.

## Phase 4: Create branch and commit

1. **Stash any unstaged work** so the checkout doesn't fail:
   ```bash
   git stash --include-untracked
   ```

2. **Checkout and pull the base branch**:
   ```bash
   git checkout <base> && git pull origin <base>
   ```

3. **Create the feature branch**. Sanitize the title: lowercase, replace spaces/special chars with hyphens, strip leading/trailing hyphens, limit to 50 chars.
   ```bash
   git checkout -b feature/<sanitized-title>
   ```
   If the branch already exists, append a numeric suffix (`-2`, `-3`, etc.) until you find one that doesn't.

4. **Pop the stash** to restore staged changes:
   ```bash
   git stash pop
   ```

5. **Commit**:
   ```bash
   git commit -m "feat: <title>"
   ```

## Phase 5: Build the PR description

Before pushing or creating the PR, build a rich description by spawning subagents. Read each agent's instruction file from `agents/` in this skill directory before spawning it.

### Step 1 — Gather context (spawn in parallel)

Spawn these two subagents at the same time since they're independent:

- **gather-diff-summary** (`agents/gather-diff-summary.md`): Pass it the repo path, base branch, and feature branch. It returns the diff stat, diff patch, and a written summary of the changes.
- **gather-repo-info** (`agents/gather-repo-info.md`): Pass it the repo path and feature branch. It returns the repo owner, repo name, and head ref needed for building GitHub file links.

### Step 2 — Write the description (sequential)

Spawn **write-description** (`agents/write-description.md`). Pass it:
- The changes summary from step 1
- The user description / summary from Phase 1

It returns the PR description body in markdown.

### Step 3 — Diagram and Jira ticket (spawn in parallel)

These two are independent of each other and can run at the same time:

- **create-mermaid-diagram** (`agents/create-mermaid-diagram.md`): Pass it the diff stat and diff patch from step 1, and the PR description from step 2. It decides whether a diagram adds value and either returns Mermaid code or `SKIP`.
- **ensure-jira-ticket** (`agents/ensure-jira-ticket.md`): Pass it the conversation context (the user's message and relevant chat history), the changes summary from step 1, the PR description from step 2, and the default Jira project key. It checks whether a ticket is already referenced, validates it if so, and creates one if not. It returns the ticket key and URL.

After both complete:
- If the diagram agent returned Mermaid code, insert a "Diagram" section into the PR body containing the Mermaid code block — place it before "**What changed**" if that heading exists, otherwise append it to the end. If it returned `SKIP`, leave the body as-is.
- If the Jira agent returned a ticket, add a line at the top of the PR body linking to it (e.g., `**Ticket:** [DEVOPS-123](https://...)`).

### Step 4 — Format the body (sequential)

Spawn **format-pr-body** (`agents/format-pr-body.md`). Pass it:
- The PR body (with diagram and Jira link inserted)
- The repo owner, repo name, and head ref from step 1

It returns the final formatted markdown body ready to use in `gh pr create`.

## Phase 6: Push and open the PR

1. **Push the branch**:
   ```bash
   git push -u origin feature/<sanitized-title>
   ```

2. **Build the PR title.** If the ensure-jira-ticket agent returned a ticket key in Phase 5, prepend it to the title in brackets:
   ```
   [TICKET-KEY]: <title>
   ```
   For example: `[HWTK-2445]: new category migration for Clinical Goals`

   If no Jira ticket was found or created, use the title as-is.

3. **Create the PR.** Write the enhanced body from Phase 5 to a temp file to avoid shell quoting issues:
   ```bash
   TMPFILE=$(mktemp /tmp/pr-body-XXXXXX.md)
   cat > "$TMPFILE" << 'BODY_EOF'
   <formatted body from Phase 5>
   BODY_EOF

   gh pr create \
     --base <base> \
     --head feature/<sanitized-title> \
     --title "[TICKET-KEY]: <title>" \
     --body-file "$TMPFILE"

   rm -f "$TMPFILE"
   ```

   If Phase 5 failed or was skipped, fall back to a basic body:
   ```bash
   gh pr create \
     --base <base> \
     --head feature/<sanitized-title> \
     --title "[TICKET-KEY]: <title>" \
     --body "## Summary

   <summary from Phase 1>

   ## Changes

   - <list of changed files with one-line descriptions>"
   ```

## Phase 7: Link the PR to the Jira ticket

If a Jira ticket was found or created in Phase 5, add the PR URL as a comment on the ticket so the two are cross-linked:

```bash
jira comment add <TICKET-KEY> $'PR opened: <PR-URL>'
```

Get the PR URL from the `gh pr create` output, or:
```bash
gh pr view --json url -q .url
```

If this step fails, it's non-critical — the PR title already contains the ticket key, so traceability isn't lost.

## Error recovery

| Problem | Fix |
|---|---|
| `git checkout` fails due to uncommitted changes | `git stash --include-untracked`, then retry |
| Branch name already exists | Append `-2`, `-3`, etc. |
| `gh` not authenticated | Run `gh auth login` and retry |
| `git pull` has merge conflicts | Abort the pull (`git merge --abort`), alert the user |
| Push is rejected | Pull with rebase (`git pull --rebase origin <base>`), then retry push |
| Phase 5 subagent fails | Skip the remaining enhancement steps — Phase 6 falls back to a basic PR body |

## Requirements

- `git` installed and configured
- `gh` CLI installed and authenticated (`gh auth status`)
- Write access to the repository
- For Phase 5: Subagent spawning capability (Task tool)
