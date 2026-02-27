---
name: jira-ticket-update
description: Jira Ticket Update (jira-ticket-update)
disable-model-invocation: true
---

# Jira Ticket Update (jira-ticket-update)

## Overview

Update an existing Jira ticket (identified by key like `DEVOPS-123`) via the `jira` CLI. This command should run the update directly (non-interactive by default), appending via comment by default (to avoid overwriting), and optionally transition status. Only override summary/description if explicitly intended.

title: "Jira Ticket Update"

command: "jira-ticket-update"

description: "Update an existing Jira ticket by key (summary, description, labels), and optionally transition status, via the jira CLI."

arguments:
  - name: ticketKey
    description: "Jira ticket key to update (e.g., DEVOPS-123)."

## Steps

1. **Prereqs**
   - Ensure `jira` CLI is installed and authenticated: `jira session`
   - Verify endpoint/user env vars if needed (`JIRA_API_TOKEN`, `JIRA_USER`, `JIRA_BASE_URL`)

2. **Inputs to gather**
   - Ticket key (argument: `ticketKey`, e.g., `DEVOPS-123`)
   - New summary (if changing)
   - New description with bullets/acceptance criteria (if changing)
   - Labels/components to add/remove (optional)
   - Desired status transition (optional, e.g., `"In Progress"`, `"Done"`)

3. **Compose update text (example)**
   ```
   Update: adjust DNS entry target for Mastra production.

   Details:
   - Hostname: mastra.ai-platform.internal
   - New target: arn:aws:elasticloadbalancing:us-east-2:427286316823:loadbalancer/app/new-alb/abc123

   Acceptance Criteria:
   - DNS points to new ALB target
   - Health check passes on new target
   ```

4. **Append to the ticket (run now, non-interactive)**
   - Preferred (append without overwriting): add a comment
   ```
   jira comment ${ticketKey} \
     --noedit \
     --comment $'Update: adjust DNS entry target for Mastra production.\n\nDetails:\n- Hostname: mastra.ai-platform.internal\n- New target: arn:aws:elasticloadbalancing:us-east-2:427286316823:loadbalancer/app/new-alb/abc123\n\nAcceptance Criteria:\n- DNS points to new ALB target\n- Health check passes on new target'
   ```
   - If you must change fields, use `jira edit` (be careful: this overwrites fields):
   ```
   jira edit ${ticketKey} \
     --noedit \
     --override summary="Adjust Mastra prod DNS target" \
     --override description=$'Update: adjust DNS entry target for Mastra production.\n\nDetails:\n- Hostname: mastra.ai-platform.internal\n- New target: arn:aws:elasticloadbalancing:us-east-2:427286316823:loadbalancer/app/new-alb/abc123\n\nAcceptance Criteria:\n- DNS points to new ALB target\n- Health check passes on new target' \
     --override labels="dns,mastra"
   ```
   - If you prefer interactive editing, drop `--noedit` and omit `--override`.

5. **(Optional) Transition status**
   - To move status (e.g., to In Progress):
   ```
   jira transition ${ticketKey} --transition "In Progress"
   ```

6. **Verify ticket**
   - Confirm CLI success and inspect ticket: `jira view ${ticketKey}` or `jira browse ${ticketKey}`
   - Ensure bullets/newlines render correctly.

7. **If formatting is off**
   - Re-run `jira edit ${ticketKey} --noedit --override description=$'<new text with \\n>'`.

## Requirements

- `jira` CLI installed and authenticated
- Ticket key available
- New summary/description/labels prepared with bullets/line breaks
- Network access to Jira endpoint
