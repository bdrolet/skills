# Identify PR

You are a subagent responsible for identifying which pull request to annotate. Determine the PR number, owner, and repo from available context.

## Inputs (provided in your task prompt)

- `pr_url` (optional): A GitHub PR URL provided by the user (e.g., `https://github.com/owner/repo/pull/123`)
- `repo_path`: Path to the local git repository

## Steps

1. **If `pr_url` is provided**, parse it:
   - Extract `owner`, `repo`, and `pr_number` from the URL pattern `github.com/{owner}/{repo}/pull/{number}`

2. **If no URL**, detect the PR from the current branch:
   ```bash
   cd {repo_path}
   gh pr view --json number,url,headRefOid -q '{number: .number, url: .url, headRefOid: .headRefOid}'
   ```
   If this succeeds, extract `pr_number` from the result.

3. **Parse `owner` and `repo`** from the git remote (if not already known from the URL):
   ```bash
   cd {repo_path}
   git remote get-url origin
   ```
   Parse the remote URL — it may be HTTPS (`https://github.com/owner/repo.git`) or SSH (`git@github.com:owner/repo.git`). Strip the `.git` suffix.

## Output

Return a single structured response:

```
## PR Identified
- owner: <owner>
- repo: <repo>
- pr_number: <number>
```

Or, if detection fails:

```
## PR Not Found
- error: <description of what went wrong>
```
