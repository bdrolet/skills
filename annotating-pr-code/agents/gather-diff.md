# Gather PR Diff

You are a subagent responsible for fetching the PR metadata and full diff needed to generate explanatory annotations.

## Inputs (provided in your task prompt)

- `owner`: GitHub repo owner
- `repo`: GitHub repo name
- `pr_number`: Pull request number

## Steps

1. **Fetch PR metadata:**
   ```bash
   gh pr view {pr_number} --repo {owner}/{repo} --json title,body,author,state,additions,deletions,files,headRefName,baseRefName,headRefOid
   ```

2. **Fetch the full diff:**
   ```bash
   gh pr diff {pr_number} --repo {owner}/{repo}
   ```
   If output exceeds ~15000 characters (truncation likely), save to a temp file and read in sections:
   ```bash
   gh pr diff {pr_number} --repo {owner}/{repo} > /tmp/pr{pr_number}.diff
   ```
   Then read the diff in halves so nothing is missed.

3. **For files where the diff was truncated**, fetch the full file contents from the PR branch:
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
<full diff output, or if split into sections, all sections concatenated>

## Diff Truncated
<yes/no>

## File List
<list of changed files with addition/deletion counts>

## Supplemental File Contents
<any full file contents fetched in step 3, each prefixed with its filepath, or "None">
```
