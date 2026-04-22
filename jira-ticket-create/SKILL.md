---
name: jira-ticket-create
description: Jira Ticket Create (jira-ticket-create)
disable-model-invocation: true
---

# Jira Ticket Create (jira-ticket-create)

## Overview

Create a well-formatted Jira ticket in a specified Jira project/space (e.g., DEVOPS, GENAI) via the `jira` CLI. When this command is invoked, execute the `jira create` call directly (non-interactive) instead of only printing instructions. Include host/target details and acceptance criteria with clean bullets and line breaks.

title: "Jira Ticket Create"

command: "jira-ticket-create"

description: "Create a Jira ticket in the given project (e.g., DEVOPS, GENAI) with summary/description and acceptance criteria via jira CLI."

arguments:
  - name: projectKey
    description: "Target Jira project/space key (e.g., DEVOPS, GENAI)."
    default: "DEVOPS"

## Steps

1. **Prereqs**
   - Ensure `jira` CLI is installed and authenticated: `jira session`
   - Verify endpoint and user env vars if needed (`JIRA_API_TOKEN`, `JIRA_USER`, `JIRA_BASE_URL`).

2. **Inputs to gather**
   - Project key (argument: `projectKey`, e.g., `DEVOPS`, `GENAI`)
   - Issue type (e.g., `Task`)
   - Summary (short title)
   - Description with bullets and acceptance criteria
   - Any labels/components (optional)
   - Sprint name (optional, e.g., `"C2:26 Sprint 2"`)

3. **Compose description in Jira wiki markup**

   Jira Cloud uses wiki markup, NOT markdown. Key syntax:
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
   * ALB rule: host-header {{mastra.ai-platform.internal}} -> mastra target group

   h3. Acceptance Criteria

   * DNS entry created and resolves to the ALB (or appropriate target)
   * curl/health check succeeds using the hostname
   ```

4. **Create the ticket (run now, non-interactive)**
   - Use a heredoc with `"$(cat <<'EOF' ... EOF)"` to preserve real newlines. Do NOT use `$'...\n...'` — it produces broken formatting on Jira Cloud.
   - Execute the command immediately with `projectKey`:
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
   * ALB rule: host-header {{mastra.ai-platform.internal}} -> mastra target group

   h3. Acceptance Criteria

   * DNS entry created and resolves to the ALB (or appropriate target)
   * curl/health check succeeds using the hostname
   EOF
   )"
   ```
   - Do not just print instructions; run the command non-interactively.

5. **(Optional) Assign to a sprint**

   The `jira` CLI does not support sprint assignment. Use the Jira Agile REST API via `curl` instead. Auth uses the same credentials as the CLI (user + API token from the macOS keyring).

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

   **c. Move the issue to the sprint:**
   ```bash
   curl -s -X POST -u "$JIRA_USER:$JIRA_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"issues":["<TICKET_KEY>"]}' \
     "https://homewardhealth.atlassian.net/rest/agile/1.0/sprint/<SPRINT_ID>/issue"
   ```
   An empty response (HTTP 204) means success.

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

6. **Verify ticket**
   - Confirm the CLI returns `OK <KEY> <URL>`.
   - Open in browser: `jira browse <KEY>` or the returned URL.
   - Ensure description renders headings, bullets, and code blocks correctly.

7. **If description formatting is off**
   - Re-run with the same heredoc pattern:
   ```bash
   jira edit <KEY> --noedit --override description="$(cat <<'EOF'
   <fixed description with wiki markup>
   EOF
   )"
   ```

## Requirements

- `jira` CLI installed and authenticated
- Project key and issue type available
- Summary and description prepared with bullets/line breaks
- Network access to Jira endpoint
