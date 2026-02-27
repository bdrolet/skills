# Gather Repo Info

You are a subagent responsible for extracting repository metadata needed to build GitHub file links in the PR description.

## Inputs (provided in your task prompt)

- `repo_dir`: Path to the git repository
- `feature_branch`: The feature branch name

## Steps

1. **Get the remote URL and parse owner/repo:**
   ```bash
   git remote get-url origin
   ```
   Parse the owner and repo name from the URL. Handles both formats:
   - `https://github.com/owner/repo.git` → owner: `owner`, repo: `repo`
   - `git@github.com:owner/repo.git` → owner: `owner`, repo: `repo`

   Strip any trailing `.git` suffix.

2. **Determine the head ref.** This is the feature branch name that will appear in GitHub URLs. Use the `feature_branch` input directly. If it starts with `origin/`, strip that prefix.

## Output

Return a single response with these fields:

```
- Owner: <owner>
- Repo: <repo_name>
- Head Ref: <branch name>
```
