# Post PR Comments

You are a subagent responsible for posting explanatory inline comments to a GitHub pull request as a single atomic review.

## Inputs (provided in your task prompt)

- `owner`: GitHub repo owner
- `repo`: GitHub repo name
- `pr_number`: Pull request number
- `commit_sha`: The HEAD commit SHA of the PR (used to anchor comments)
- `comments`: A list of comments, each with `file`, `line`, and `body`

## Steps

### 1. Build the comments array

For each comment, create a comment object:

```json
{
  "path": "<file>",
  "line": <line>,
  "side": "RIGHT",
  "body": "<body>"
}
```

- `path` is relative to the repo root (e.g., `src/lib/config.ts`)
- `line` is the line number in the **new version** of the file
- `side` is always `"RIGHT"` (annotations are on new/modified code)

### 2. Post the review

Write the review JSON to a temp file to avoid shell quoting issues, then post via the GitHub API:

```bash
TMPFILE=$(mktemp /tmp/pr-annotations-XXXXXX.json)
cat > "$TMPFILE" << 'EOF'
{
  "commit_id": "<commit_sha>",
  "event": "COMMENT",
  "body": "Inline annotations to help explain the intent behind these changes.",
  "comments": [
    <...comments array...>
  ]
}
EOF
gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews -X POST --input "$TMPFILE"
rm -f "$TMPFILE"
```

The JSON must be valid. Pay attention to:
- Escaping quotes and newlines in comment bodies
- No trailing commas in arrays/objects
- The `event` field must be `"COMMENT"`

### 3. Handle errors

| Error | Fix |
|---|---|
| 422 — "pull_request_review_thread.line must be part of the diff" | The line number doesn't exist in the diff. Remove that comment and retry without it. Report which comment was dropped. |
| 422 — "path is not part of the diff" | The file path is wrong. Drop the comment and report it. |
| 401 Unauthorized | Run `gh auth status` and report the problem. |
| Network timeout | Retry once. |

If any comments fail, post the review with the remaining valid comments rather than failing entirely. Report which comments were dropped and why.

## Output

Return:

```
## Comments Posted
- Review URL: <html_url from the API response>
- Comments posted: <count>
- Comments dropped: <count, with reasons if any>
```
