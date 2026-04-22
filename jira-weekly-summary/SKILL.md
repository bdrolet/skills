---
name: jira-weekly-summary
description: Use when generating a weekly summary of completed Jira tickets, or when asked for a weekly update from Jira
disable-model-invocation: true
---

# Jira Weekly Summary

Fetch all Jira tickets completed in the last 7 days for a given project and write individual ticket Markdown files plus a summary index.

## Prerequisites

- `JIRA_USER` and `JIRA_API_TOKEN` env vars set (or `~/.jira.d/config.yml` with endpoint/user)
- Jira endpoint: `https://homewardhealth.atlassian.net`
- Network access to Jira REST API v3

## Steps

1. **Resolve inputs**
   - `PROJECT`: Jira project key (default: `GENAI`)
   - `OUTPUT_DIR`: output directory (default: `homeward/projects/ai-planning/weekly_updates`)
   - `DAYS`: lookback window (default: `7`)

2. **Run the generation script**

   ```bash
   python3 <skill_dir>/scripts/gen_weekly_summary.py \
     --project "$PROJECT" \
     --output-dir "$OUTPUT_DIR" \
     --days "$DAYS"
   ```

   The script:
   - Queries `POST /rest/api/3/search/jql` for `status = Done AND statusCategoryChangedDate >= -${DAYS}d`
   - Converts Atlassian Document Format (ADF) descriptions to Markdown
   - Writes one `jira-<KEY>.md` per ticket with metadata table, description, and comments
   - Writes `weekly-summary-<YYYY-MM-DD>.md` index with a table of all tickets

3. **Report results**
   - Show count of tickets written and the summary file path
   - If zero tickets found, inform the user — no files are written

## Notes

- The `jira list` CLI command is broken due to API v2 deprecation; this skill uses the REST API directly via `curl` + Python.
- ADF conversion handles: paragraphs, headings, lists, task lists, code blocks, blockquotes, inline cards, mentions, tables, and panels.
