# Gather PR Context

You are a subagent responsible for fetching all the data needed to review a pull request. Run all the commands below and return their outputs in a structured format.

## Inputs (provided in your task prompt)

- `owner`: GitHub repo owner (e.g., `homeward-health`)
- `repo`: GitHub repo name (e.g., `ai-platform-images`)
- `pr_number`: Pull request number

## Steps

1. **Fetch PR metadata:**
   ```bash
   gh pr view {pr_number} --json title,body,author,state,additions,deletions,files,headRefName,baseRefName,headRefOid
   ```

2. **Fetch the full diff:**
   ```bash
   gh pr diff {pr_number}
   ```
   If output exceeds ~15000 characters (truncation likely), also save to a temp file and report that it was truncated:
   ```bash
   gh pr diff {pr_number} > /tmp/pr{pr_number}.diff
   ```
   Then read the diff in sections (first half, second half) so nothing is missed.

3. **Fetch existing review comments** (to avoid duplicating feedback):
   ```bash
   gh api repos/{owner}/{repo}/pulls/{pr_number}/comments --jq '.[] | {id: .id, user: .user.login, path: .path, line: .line, body: .body}'
   ```

4. **Fetch existing reviews** (to see if there are prior approvals or requests for changes):
   ```bash
   gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews --jq '.[] | {id: .id, user: .user.login, state: .state, body: .body}'
   ```

5. **For files where the diff was truncated**, fetch the full file contents from the PR branch:
   ```bash
   gh api "repos/{owner}/{repo}/contents/{filepath}?ref={headRefName}" --jq '.content' | base64 -d
   ```
   Only do this for files that appeared in the diff but whose hunks were cut off.

## Output

Return a single structured response with these clearly labeled sections:

```
## PR Metadata
<JSON output from step 1>

## Head Commit SHA
<headRefOid value extracted from metadata>

## Head Branch
<headRefName value extracted from metadata>

## Diff
<full diff output, or if it was split into sections, all sections concatenated>

## Diff Truncated
<yes/no — whether the diff needed to be fetched in sections>

## Existing Review Comments
<output from step 3, or "None">

## Existing Reviews
<output from step 4, or "None">

## Supplemental File Contents
<any full file contents fetched in step 5, each prefixed with its filepath, or "None">
```
