---
name: jira-ticket-read
description: Jira Ticket Read (jira-ticket-read)
disable-model-invocation: true
---

# Jira Ticket Read (jira-ticket-read)

## Overview

Read an existing Jira ticket by key (e.g., `DEVOPS-123`) and optionally save its content to a Markdown file.
**Try the Atlassian MCP first.** If unavailable or unauthenticated, fall back to the `jira` CLI.

title: "Jira Ticket Read"
command: "jira-ticket-read"
description: "Read a Jira ticket by key; optionally save to a *.md file."

arguments:
  - name: ticketKey
    description: "Jira ticket key to read (e.g., DEVOPS-123)."

---

## MCP vs CLI Strategy

**Always try MCP first.**

### Check if MCP is available

The Atlassian MCP (`plugin-atlassian-atlassian`) is authenticated when it exposes tools beyond `mcp_auth`. If only `mcp_auth` is listed, fall back to the CLI.

---

## Path A — Atlassian MCP (preferred)

Use `getJiraIssue` with:
- `cloudId`: `"homewardhealth.atlassian.net"`
- `issueIdOrKey`: the ticket key (e.g., `GENAI-253`)

The MCP returns the full issue object including summary, description, status, assignee, labels, and comments. Extract what you need from the response directly.

If saving to a file is required, write the MCP response fields as markdown using the Write tool.

---

## Path B — jira CLI fallback

Use when the MCP is unavailable or unauthenticated.

### 1. Prereqs

- Ensure `jira` CLI is installed and authenticated: `jira session`
- Verify endpoint/user env vars if needed (`JIRA_API_TOKEN`, `JIRA_USER`, `JIRA_BASE_URL`)

### 2. Gather input

- Ticket key (argument: `ticketKey`, e.g., `DEVOPS-123`)
- Optional: output path/filename (default: `jira-<KEY>.md` in current or specified directory)

### 3. Fetch ticket

```bash
jira view ${ticketKey}
```

Capture: summary, description, status, assignee, labels, URL, and comments.

For structured JSON output (easier to parse):
```bash
JIRA_USER="ben.drolet@homewardhealth.com"
JIRA_TOKEN=$(security find-generic-password -s "jira" -w)
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/api/2/issue/${ticketKey}" \
  | python3 -c "
import json, sys
d = json.load(sys.stdin)
f = d['fields']
print('Summary:', f['summary'])
print('Status:', f['status']['name'])
print('Type:', f['issuetype']['name'])
print('Assignee:', (f.get('assignee') or {}).get('displayName', 'Unassigned'))
print('Description:', (f.get('description') or '')[:500])
"
```

### 4. Compose Markdown file

Write a `.md` file with a clear structure:

```markdown
# <TICKET_KEY>: <summary>

**Status:** <status>
**Type:** <issue type>
**Assignee:** <assignee>
**Link:** https://homewardhealth.atlassian.net/browse/<TICKET_KEY>

## Description

<description with bullets/formatting preserved>

## Labels

<labels>

## Comments

<comments if relevant>
```

### 5. Save file

Write to the chosen path (e.g., `jira-${ticketKey}.md`). Ensure the parent directory exists.

### 6. Verify

Confirm the file was written and spot-check the content.
Optionally open in browser: `jira browse ${ticketKey}`

---

## Requirements

- Atlassian MCP authenticated **or** `jira` CLI installed and authenticated (`jira session`)
- Ticket key available
- Network access to Jira endpoint

## Tips

- Use a consistent naming convention (e.g., `jira-DEVOPS-123.md`) so tickets are easy to find.
- The REST API approach (curl) gives richer structured output than `jira view` for scripting.
