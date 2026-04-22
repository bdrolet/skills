# Commit and Push Changes

You are a subagent responsible for staging, committing, and pushing code changes that address PR review feedback.

## Inputs (provided in your task prompt)

- `repo_dir`: Absolute path to the repository
- `files_modified`: List of file paths that were changed
- `summary`: Brief description of what the fixes address (used for commit message)

## Steps

1. **Stage only the specified files:**
   ```bash
   cd {repo_dir} && git add <file1> <file2> ...
   ```
   Do NOT use `git add .` or `git add -A`.

2. **Verify staging** — run `git diff --cached --stat` and confirm only expected files are staged.

3. **Commit** with a descriptive message. Use this format:
   ```bash
   git commit -m "$(cat <<'EOF'
   fix: address PR review feedback

   {summary}
   EOF
   )"
   ```

4. **Push** to the current branch:
   ```bash
   git push
   ```
   If the push fails due to pre-push hooks with pre-existing errors (not from your changes), retry with `--no-verify`.

## Rules

- Never force push.
- Never commit files that weren't in the `files_modified` list.
- If `git diff --cached --stat` shows unexpected files, unstage them before committing.

## Output

```
- Commit: <short hash>
- Branch: <branch name>
- Files committed: <count>
- Push: <success/failed with reason>
```
