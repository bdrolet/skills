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

3. **Compose description (example for Mastra prod DNS)**
   ```
   Request: add DNS entry for Mastra production service.

   Details:
   - Hostname: mastra.ai-platform.internal (internal service)
   - Target ALB ARN: arn:aws:elasticloadbalancing:us-east-2:427286316823:loadbalancer/app/n8n-alb/02f0fd3467d2c130
   - ALB rule: host-header mastra.ai-platform.internal -> mastra target group

   Acceptance Criteria:
   - DNS entry created and resolves to the ALB (or appropriate target)
   - curl/health check succeeds using the hostname
   ```

4. **Create the ticket (run now, non-interactive)**
   - Execute the command immediately with `projectKey` (e.g., `DEVOPS`, `GENAI`):
   ```
   jira create \
     --project ${projectKey} \
     --issuetype Task \
     --summary "Add DNS entry for Mastra prod" \
     --noedit \
     --override description=$'Request: add DNS entry for Mastra production service.\n\nDetails:\n- Hostname: mastra.ai-platform.internal (internal service)\n- Target ALB ARN: arn:aws:elasticloadbalancing:us-east-2:427286316823:loadbalancer/app/n8n-alb/02f0fd3467d2c130\n- ALB rule: host-header mastra.ai-platform.internal -> mastra target group\n\nAcceptance Criteria:\n- DNS entry created and resolves to the ALB (or appropriate target)\n- curl/health check succeeds using the hostname'
   ```
   - Do not just print instructions; run the command non-interactively. If interactive editing is preferred, drop `--noedit` and omit `--override`.

5. **Verify ticket**
   - Confirm the CLI returns `OK <KEY> <URL>`.
   - Open in browser: `jira browse <KEY>` or the returned URL.
   - Ensure description renders bullets/newlines correctly.

6. **If description formatting is off**
   - Re-run `jira edit <KEY> --noedit --override description=$'<new text with \\n>'`.
   - Use `$'..'` literal for embedded newlines; avoid `--file` (not supported).

## Requirements

- `jira` CLI installed and authenticated
- Project key and issue type available
- Summary and description prepared with bullets/line breaks
- Network access to Jira endpoint
