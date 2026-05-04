---
name: release-mastra-api
description: Use when releasing, publishing, or versioning the @homeward-health/mastra-api package, or when the user wants to bump the mastra-api version and push a release tag
---

# Release @homeward-health/mastra-api

Bump the version in `packages/mastra-api/package.json`, commit, create a `mastra-api/vX.Y.Z` tag, and push to trigger the `Mastra API Publish` GitHub Actions workflow.

## Steps

1. **Validate environment:**
   - Confirm clean working tree and on `main` branch.
   - From repo root: `cd packages/mastra-api`.

2. **Run the release:**
   - Interactive (choose patch/minor/major): `npm run release`
   - Patch only: `npm run release:patch`
   - Minor: `npm run release:minor`
   - Major: `npm run release:major`
   - Preview only: `npm run release:dry-run`

3. **Confirm publish triggered:**
   - Verify the tag `mastra-api/vX.Y.Z` exists on the remote: `git ls-remote --tags origin 'mastra-api/v*'`
   - Check the `Mastra API Publish` workflow run: `gh run list --workflow=mastra-api-publish.yml --limit 3`

## Requirements

- `git` installed and configured with push access to `origin`.
- `npm` and `release-it` (devDependency in `packages/mastra-api`).
- Must be on `main` with a clean working directory.
