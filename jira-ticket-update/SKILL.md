---
name: jira-ticket-update
description: Jira Ticket Update (jira-ticket-update)
disable-model-invocation: true
---

# Jira Ticket Update (jira-ticket-update)

## Overview

Update an existing Jira ticket (identified by key like `DEVOPS-123`) — add comments, change fields, or transition status.
**Try the Atlassian MCP first.** If unavailable or unauthenticated, fall back to the `jira` CLI and Jira REST API.
Default to appending via comment to avoid overwriting existing content. Only update summary/description if explicitly intended.

title: "Jira Ticket Update"
command: "jira-ticket-update"
description: "Update an existing Jira ticket by key (comment, fields, status transition) via MCP or jira CLI."

arguments:
  - name: ticketKey
    description: "Jira ticket key to update (e.g., DEVOPS-123)."

---

## MCP vs CLI Strategy

**Always try MCP first.**

### Check if MCP is available

The Atlassian MCP (`plugin-atlassian-atlassian`) is authenticated when it exposes tools beyond `mcp_auth`. If only `mcp_auth` is listed, fall back to the CLI.

---

## Path A — Atlassian MCP (preferred)

Use the appropriate MCP tool for each operation:

| Operation | MCP Tool | Key params |
|---|---|---|
| Add comment | `addCommentToJiraIssue` | `cloudId`, `issueIdOrKey`, `commentBody` (markdown), `contentFormat: "markdown"` |
| Update fields | `updateJiraIssue` | `cloudId`, `issueIdOrKey`, fields to update |
| Transition status | `getTransitionsForJiraIssue` → `transitionJiraIssue` | `cloudId`, `issueIdOrKey`, `transitionId` |

All MCP calls use `cloudId: "homewardhealth.atlassian.net"`.

**Transition workflow (MCP):**
1. Call `getTransitionsForJiraIssue` to list available transitions and their IDs.
2. Find the target transition (e.g., `Done`, `In Progress`).
3. Call `transitionJiraIssue` with the `transitionId`.

---

## Path B — jira CLI + REST API fallback

Use when the MCP is unavailable or unauthenticated.

### 1. Prereqs

- Ensure `jira` CLI is installed and authenticated: `jira session`
- Verify endpoint/user env vars if needed (`JIRA_API_TOKEN`, `JIRA_USER`, `JIRA_BASE_URL`)

### 2. Inputs to gather

- Ticket key (argument: `ticketKey`, e.g., `DEVOPS-123`)
- New summary (if changing)
- New description with bullets/acceptance criteria (if changing)
- Labels/components to add/remove (optional)
- Desired status transition (optional, e.g., `"In Progress"`, `"Done"`)
- Sprint to assign to (optional)

### 3. Add a comment (preferred — non-destructive)

Use `--comment` flag (not `--override`):

```bash
jira comment ${ticketKey} \
  --noedit \
  --comment "$(cat <<'EOF'
Update: adjusted DNS entry target for Mastra production.

Details:
- New target: arn:aws:elasticloadbalancing:us-east-2:...
- Health check passes on new target
EOF
)"
```

> **Note:** `jira comment` uses `--comment`, not `--override`. The `--override` flag is only for `jira edit` (field overrides).

### 4. Update fields (destructive — overwrites)

Use `jira edit` with `--override` and a heredoc for multi-line descriptions:

```bash
jira edit ${ticketKey} \
  --noedit \
  --override summary="Adjust Mastra prod DNS target" \
  --override description="$(cat <<'EOF'
Update: adjust DNS entry target for Mastra production.

h3. Details

* Hostname: {{mastra.ai-platform.internal}}
* New target: {{arn:aws:elasticloadbalancing:us-east-2:...}}

h3. Acceptance Criteria

* DNS points to new ALB target
* Health check passes on new target
EOF
)"
```

> **Note:** `jira edit --override` uses Jira wiki markup (not markdown). See `jira-ticket-create` for syntax reference.

### 5. Transition status (REST API — more reliable than CLI)

The `jira` CLI's `jira transition` command takes a positional argument `jira transition <TRANSITION_NAME> <ISSUE>` but available names vary by workflow. Using the REST API directly is more reliable.

```bash
JIRA_USER="ben.drolet@homewardhealth.com"
JIRA_TOKEN=$(security find-generic-password -s "jira" -w)

# a. List available transitions (get IDs)
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/api/2/issue/${ticketKey}/transitions" \
  | python3 -c "import json,sys; [print(f\"{t['id']}  {t['name']}\") for t in json.load(sys.stdin).get('transitions',[])]"

# b. Execute transition (HTTP 204 = success)
curl -s -o /dev/null -w "%{http_code}" -X POST -u "$JIRA_USER:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transition":{"id":"<TRANSITION_ID>"}}' \
  "https://homewardhealth.atlassian.net/rest/api/2/issue/${ticketKey}/transitions"
```

### 6. (Optional) Assign to a sprint

The `jira` CLI does not support sprint assignment. Use the REST API:

```bash
JIRA_USER="ben.drolet@homewardhealth.com"
JIRA_TOKEN=$(security find-generic-password -s "jira" -w)
PROJECT_KEY=$(echo "${ticketKey}" | cut -d- -f1)
```

**a. Find the scrum board ID:**
```bash
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/agile/1.0/board?projectKeyOrId=$PROJECT_KEY&type=scrum" \
  | python3 -c "import json,sys; [print(f\"{v['id']}  {v['name']}\") for v in json.load(sys.stdin).get('values',[])]"
```

**b. List active/future sprints:**
```bash
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/agile/1.0/board/<BOARD_ID>/sprint?state=active,future" \
  | python3 -c "import json,sys; [print(f\"{s['id']}  {s['state']:<8}  {s['name']}\") for s in json.load(sys.stdin).get('values',[])]"
```

**c. Move the issue to the sprint (HTTP 204 = success):**
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST -u "$JIRA_USER:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"issues":["'${ticketKey}'""]}' \
  "https://homewardhealth.atlassian.net/rest/agile/1.0/sprint/<SPRINT_ID>/issue"
```

**d. Verify:**
```bash
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/api/2/issue/${ticketKey}?fields=customfield_10020" \
  | python3 -c "import json,sys; [print(f\"Sprint: {s.get('name')} ({s.get('state')})\") for s in (json.load(sys.stdin).get('fields',{}).get('customfield_10020') or [])]"
```

**Known board IDs:**
| Project | Board Name | Board ID | Type |
|---------|-----------|----------|------|
| GENAI | AI Dev- Ex/Ops Sprint | 1700 | scrum |

### 7. Verify ticket

Confirm CLI/API success and inspect ticket:
```bash
jira view ${ticketKey}
# or
jira browse ${ticketKey}
```

---

## Requirements

- Atlassian MCP authenticated **or** `jira` CLI installed and authenticated (`jira session`)
- Ticket key available
- Network access to Jira endpoint
