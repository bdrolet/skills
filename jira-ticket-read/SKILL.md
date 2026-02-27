---
name: jira-ticket-read
description: Jira Ticket Read (jira-ticket-read)
disable-model-invocation: true
---

# Jira Ticket Read (jira-ticket-read)

## Overview

Read an existing Jira ticket by key (e.g., `DEVOPS-123`) via the `jira` CLI and save its content to a Markdown file. Use when you need a local copy of the ticket for reference, notes, or offline work.

title: "Jira Ticket Read"
command: "jira-ticket-read"
description: "Read a Jira ticket by key and save it to a *.md file."

arguments:
  - name: ticketKey
    description: "Jira ticket key to read (e.g., DEVOPS-123)."

## Steps

1. **Prereqs**
   - Ensure `jira` CLI is installed and authenticated: `jira session`
   - Verify endpoint/user env vars if needed (`JIRA_API_TOKEN`, `JIRA_USER`, `JIRA_BASE_URL`)

2. **Gather input**
   - Ticket key (argument: `ticketKey`, e.g., `DEVOPS-123`)
   - Optional: output path/filename (default: e.g. `jira-<KEY>.md` in current or specified directory)

3. **Fetch ticket**
   - Get full ticket details: `jira view ${ticketKey}` (or equivalent JSON/details if available)
   - Capture: summary, description, status, assignee, labels, link, and any other useful fields

4. **Compose Markdown**
   - Write a `.md` file with a clear structure, for example:
     - Title: ticket key + summary
     - Metadata: status, assignee, link (e.g. `jira browse ${ticketKey}`)
     - Description (with bullets/formatting preserved)
     - Optional: labels, components, comments if easily available
   - Preserve line breaks and bullets from the ticket description.

5. **Save file**
   - Write to the chosen path (e.g. `jira-${ticketKey}.md` or user-specified `*.md`).
   - Ensure parent directory exists.

6. **Verify**
   - Confirm file was written and open or `cat` to check content.
   - Optionally open in browser: `jira browse ${ticketKey}`

## Requirements

- `jira` CLI installed and authenticated
- Ticket key available
- Write access to the target directory for the output `.md` file
- Network access to Jira endpoint

## Tips

- Use a consistent naming convention (e.g. `jira-DEVOPS-123.md`) so tickets are easy to find.
- If the CLI supports JSON output (`jira view --format json` or similar), use it to reliably parse description and fields for the Markdown file.
