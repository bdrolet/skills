---
name: jira-ticket-create
description: Jira Ticket Create (jira-ticket-create)
disable-model-invocation: true
---

# Jira Ticket Create (jira-ticket-create)

## Overview

Create a well-formatted Jira ticket in a specified Jira project/space (e.g., DEVOPS, GENAI).
**Try the Atlassian MCP first.** If the MCP is unavailable or unauthenticated, fall back to the `jira` CLI.
Execute non-interactively — do not just print instructions.

title: "Jira Ticket Create"
command: "jira-ticket-create"
description: "Create a Jira ticket in the given project (e.g., DEVOPS, GENAI) with summary/description and acceptance criteria."

arguments:
  - name: projectKey
    description: "Target Jira project/space key (e.g., DEVOPS, GENAI)."
    default: "DEVOPS"

---

## MCP vs CLI Strategy

**Always try MCP first.** The MCP is preferred because it supports markdown natively and doesn't require wiki-markup conversion.

### Check if MCP is available

The Atlassian MCP (`plugin-atlassian-atlassian`) is authenticated when it exposes tools beyond `mcp_auth` (e.g., `createJiraIssue`). If only `mcp_auth` is listed, it is not authenticated — skip to the CLI fallback.

Quick auth check: attempt `getJiraIssue` with a known key. If it returns a result, MCP is live. If it errors with an auth/OAuth message, fall back to CLI.

---

## Path A — Atlassian MCP (preferred)

Use `createJiraIssue` with:
- `cloudId`: `"homewardhealth.atlassian.net"`
- `projectKey`: the target project key
- `issueType`: `"Task"` or `"Bug"`
- `summary`: concise title (≤ 80 chars)
- `description`: full description in **markdown** (headings `##`, bullets `-`, code fences)
- `contentFormat`: `"markdown"`

After creation, capture the returned issue key and URL, then follow steps 5–6 below (sprint assignment, verification).

---

## Path B — jira CLI fallback

Use when the MCP is unavailable or unauthenticated.

### 1. Prereqs

- Ensure `jira` CLI is installed and authenticated: `jira session`
- Verify endpoint/user env vars if needed (`JIRA_API_TOKEN`, `JIRA_USER`, `JIRA_BASE_URL`).

### 2. Inputs to gather

- Project key (argument: `projectKey`, e.g., `DEVOPS`, `GENAI`)
- Issue type (e.g., `Task`, `Bug`)
- Summary (short title)
- Description with bullets and acceptance criteria
- Any labels/components (optional)
- Sprint name (optional, e.g., `"C3:26 - Sprint 2"`)

### 3. Compose description in Jira wiki markup

The `jira` CLI sends wiki markup, NOT markdown. Key syntax:
- Headings: `h2.` / `h3.` (not `##` / `###`)
- Bullets: `*` at line start (not `-`)
- Numbered lists: `#` at line start
- Bold: `*text*`
- Inline code: `{{code}}`
- Code blocks: `{code:lang}...{code}`
- Links: `[text|url]`

Example description:
```
Request: add DNS entry for Mastra production service.

h3. Details

* Hostname: {{mastra.ai-platform.internal}} (internal service)
* Target ALB ARN: {{arn:aws:elasticloadbalancing:us-east-2:...}}

h3. Acceptance Criteria

* DNS entry created and resolves to the ALB
* curl/health check succeeds using the hostname
```

### 4. Create the ticket (non-interactive)

Use a heredoc with `"$(cat <<'EOF' ... EOF)"` to preserve real newlines.
**Do NOT use `$'...\n...'`** — it produces broken formatting on Jira Cloud.

```bash
jira create \
  --project ${projectKey} \
  --issuetype Task \
  --summary "Add DNS entry for Mastra prod" \
  --noedit \
  --override description="$(cat <<'EOF'
Request: add DNS entry for Mastra production service.

h3. Details

* Hostname: {{mastra.ai-platform.internal}} (internal service)
* Target ALB ARN: {{arn:aws:elasticloadbalancing:us-east-2:...}}

h3. Acceptance Criteria

* DNS entry created and resolves to the ALB
* curl/health check succeeds using the hostname
EOF
)"
```

The CLI returns `OK <KEY> <URL>` on success. Capture the key for the next step.

---

## 5. (Optional) Assign to a sprint

The `jira` CLI does not support sprint assignment. Use the Jira Agile REST API via `curl`.

```bash
JIRA_USER="ben.drolet@homewardhealth.com"
JIRA_TOKEN=$(security find-generic-password -s "jira" -w)
```

**a. Find the scrum board ID for the project:**
```bash
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/agile/1.0/board?projectKeyOrId=${projectKey}&type=scrum" \
  | python3 -c "import json,sys; [print(f\"{v['id']}  {v['name']}\") for v in json.load(sys.stdin).get('values',[])]"
```

**b. List active/future sprints on that board:**
```bash
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/agile/1.0/board/<BOARD_ID>/sprint?state=active,future" \
  | python3 -c "import json,sys; [print(f\"{s['id']}  {s['state']:<8}  {s['name']}\") for s in json.load(sys.stdin).get('values',[])]"
```

**c. Move the issue to the sprint (HTTP 204 = success):**
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST -u "$JIRA_USER:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"issues":["<TICKET_KEY>"]}' \
  "https://homewardhealth.atlassian.net/rest/agile/1.0/sprint/<SPRINT_ID>/issue"
```

**d. Verify:**
```bash
curl -s -u "$JIRA_USER:$JIRA_TOKEN" \
  "https://homewardhealth.atlassian.net/rest/api/2/issue/<TICKET_KEY>?fields=customfield_10020" \
  | python3 -c "import json,sys; [print(f\"Sprint: {s.get('name')} ({s.get('state')})\") for s in (json.load(sys.stdin).get('fields',{}).get('customfield_10020') or [])]"
```

**Known board IDs:**
| Project | Board Name | Board ID | Type |
|---------|-----------|----------|------|
| GENAI | AI Dev- Ex/Ops Sprint | 1700 | scrum |

---

## 6. Verify ticket

- Confirm the CLI returns `OK <KEY> <URL>` (or MCP returns the issue key).
- Open in browser: `jira browse <KEY>` or the returned URL.
- Ensure description renders headings, bullets, and code blocks correctly.

## 7. If description formatting is off (CLI path only)

Re-run with the same heredoc pattern:
```bash
jira edit <KEY> --noedit --override description="$(cat <<'EOF'
<fixed description with wiki markup>
EOF
)"
```

---

## Requirements

- Atlassian MCP authenticated **or** `jira` CLI installed and authenticated (`jira session`)
- Project key and issue type available
- Network access to Jira endpoint
