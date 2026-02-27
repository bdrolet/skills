---
name: chat-document
description: Chat: Create Narrative Document
disable-model-invocation: true
---

# Chat: Create Narrative Document

## Overview

Summarize the current chat into a working summary, logs, and a stakeholder-ready narrative, and write them to a specified directory.


title: "Chat: Create Narrative Document"

command: "chat-document"

description: "Summarize the current chat into a working summary, logs, and a stakeholder-ready narrative, and write them to a specified directory."

arguments:

  - name: outputDir

    description: "Final directory where the narrative, summary, and log files should be written."

    default: "./chat-docs"

---

You are an assistant running inside Cursor.

Your job is to:

1. Read the entire current chat (all user + assistant messages). Do not limit to recent turns; process from the first user prompt through the latest message.

2. Generate a **chat ID** and **timestamp**.

3. Create three files in `$TMPDIR`.

4. Copy those three files into the final directory `{{outputDir}}`.

5. Return the contents of the final narrative file as your response, plus a short list of created files.

6. When the chat references GitHub artifacts (PRs, PR comments, commits, files, workflow runs, etc.), use the GitHub CLI (`gh`) to fetch canonical links and include them when helpful.
   - Link shapes: PR `https://github.com/<owner>/<repo>/pull/123`, commit `https://github.com/<owner>/<repo>/commit/<sha>`, file `https://github.com/<owner>/<repo>/blob/<sha>/<path>`, workflow run `https://github.com/<owner>/<repo>/actions/runs/<run_id>`.
   - Handy `gh` commands: `gh pr view <num> --json url`, `gh pr comment list <num> --json url,author,body`, `gh api repos/:owner/:repo/commits/<sha> --jq .html_url`, `gh browse <path>`, `gh run view <id> --json url`.

Follow the steps below exactly.

---

## 1. Identify CHAT_ID, TIMESTAMP, and TOPIC_SLUG

1. Compute a short `<CHAT_ID>`:

   - Hash the full chat transcript (e.g., md5/sha256).

   - Use the **first 8 characters** of the hash as `<CHAT_ID>`.

2. Compute `<TIMESTAMP>` in this format:

   - `YYYYMMDD-HHMM` (24-hour time).

3. Generate a `<TOPIC_SLUG>` from the chat content:

   - Analyze the chat transcript to identify the main topic, subject, or theme.
   
   - Create a concise, descriptive slug (3-8 words) that captures the essence of the chat.
   
   - Convert to URL-safe format:
     - Lowercase all letters
     - Replace spaces with hyphens
     - Remove special characters (keep only alphanumeric and hyphens)
     - Limit to 60 characters total
   
   - Examples: `langfuse-setup-clickhouse-issues`, `eks-cluster-setup-auto-mode-fargate`, `mastra-workflows-staging-image-validation`
   
   - If the chat topic is unclear or too generic, use a combination of key terms from the first user message and main activities.

You will use `<TOPIC_SLUG>`, `<CHAT_ID>`, and `<TIMESTAMP>` in all filenames.

---

## 2. Filenames and Locations

Use these filenames (using the topic slug for better discoverability):

- Working summary (staging and final):

  - `$TMPDIR/<TOPIC_SLUG>-summary-<TIMESTAMP>.md`

  - `{{outputDir}}/<TOPIC_SLUG>-summary-<TIMESTAMP>.md`

- Logs file (staging and final):

  - `$TMPDIR/<TOPIC_SLUG>-logs-<TIMESTAMP>.log`

  - `{{outputDir}}/<TOPIC_SLUG>-logs-<TIMESTAMP>.log`

- Final narrative (staging and final):

  - `$TMPDIR/<TOPIC_SLUG>-narrative-<TIMESTAMP>.md`

  - `{{outputDir}}/<TOPIC_SLUG>-narrative-<TIMESTAMP>.md`

Assume:

- `$TMPDIR` exists.

- `{{outputDir}}` can be created if it does not exist.

Write each file **first** to `$TMPDIR`, then **copy** it to `{{outputDir}}` with the same filename.

---

## 3. Filter for Meaningful Commands

When scanning the chat for commands / tools / scripts:

**Include a command only if**:

- It affected progress, decisions, or understanding, OR

- Its output changed what you did next, OR

- It produced an error that was important for diagnosis, OR

- It marked a turning point (success/failure/validation).

**Exclude commands that**:

- Are typos or obviously malformed.

- Were accidental or quickly abandoned.

- Produced irrelevant or no output.

- Are duplicates where only the first meaningful run is needed.

- Are trivial environment checks unless they materially affected the solution.

If a failed command was important to the reasoning, include it (with a short explanation).

---

## 4. GitHub Links via `gh` CLI

- When the chat mentions GitHub resources (PR numbers, comment URLs, commit SHAs, file paths, or workflow runs), use `gh` to fetch canonical links and minimal context that helps readers jump directly to the artifact.
- Prefer concise `gh` invocations that surface URLs/identifiers, for example:
  - PR: `gh pr view <num> --json url`
  - PR comments: `gh pr comment list <num> --json url,author,body`
  - Commit: `gh api repos/:owner/:repo/commits/<sha> --jq .html_url`
  - File: `gh browse <path>` (optionally `--branch <branch>` or `--rev <sha>`)
  - Workflow run: `gh run view <id> --json url`
- Record these `gh` commands and essential outputs in the logs file, and incorporate the retrieved links into the working summary, narrative, and appendix when they add clarity.
- If a referenced artifact cannot be resolved, note that briefly in the summary/narrative.

---

## 5. Working Summary (`<TOPIC_SLUG>-summary-<TIMESTAMP>.md`)

Always anchor the summary with the initial user request and proceed chronologically through every turn. Do not omit early context or focus only on recent messages.

Create this file in `$TMPDIR`, then copy it to `{{outputDir}}`.

Use this structure:

```md

# Chat Working Summary

- Chat ID: <CHAT_ID>

- Timestamp: <TIMESTAMP>

- Topic: <short descriptive title>

## Message-by-Message Summary

1. User: <short paraphrase of the user prompt>

   Assistant: <short paraphrase of the response>

   - Meaningful commands (if any): `<command ...>`

   - Output summary: <1–2 lines; refer to logs file>

   - Decisions: <what was decided and why>

   - Issues/Challenges: <if any and how they were addressed>

2. ...

````

This file should be accurate and detailed but does not need polished prose.

It is the internal reference used to build the final narrative.

---

## 6. Logs File (`<TOPIC_SLUG>-logs-<TIMESTAMP>.log`)

Create this file in `$TMPDIR`, then copy it to `{{outputDir}}`.

Include **only outputs from meaningful commands**. For each command:

```txt

=== COMMAND ===

<command as run>

=== OUTPUT (truncated if necessary) ===

<relevant log lines>

=== NOTES ===

<1–3 lines on why this mattered or what it showed>

```

* Do not dump huge logs; keep only the parts needed to understand what happened.

* If logs are large, note that they are truncated.

---

## 7. Final Narrative (`<TOPIC_SLUG>-narrative-<TIMESTAMP>.md`)

Create this file in `$TMPDIR`, then copy it to `{{outputDir}}`.

Audience: yourself (future) and stakeholders.

Goal: accurate story of what happened, what was done, and **why**.

Use this structure:

```md

# Context

[Briefly set the stage. What prompted this work? What was the situation or background?]

# Goal

[What concrete outcome were we trying to achieve in this chat?]

# Purpose

[Why does this matter? Describe the business / technical / stakeholder value behind the goal.]

# Journey

## Overview

[High-level story of what happened from start to finish.

A stakeholder should be able to read this section alone and understand:

- What we tried

- What worked / didn't work

- Where we ended up]

## Deep Dive

[Organize chronologically or by logical phases. Use informative headings.]

### <Phase 1 – short title>

- What we did:

  - <brief description>

  - Commands run (meaningful only): `<command ...>` (see logs file)

- What we observed:

  - <summary of key outputs or findings>

- Decisions:

  - <decisions and rationale>

- Issues & Resolutions:

  - <challenges and how we resolved or worked around them>

### <Phase 2 – short title>

[Repeat the pattern with as many phases as needed.]

# Appendix

[List supporting artifacts as they exist in the final directory `{{outputDir}}`]

- Working summary: `{{outputDir}}/<TOPIC_SLUG>-summary-<TIMESTAMP>.md`

- Logs: `{{outputDir}}/<TOPIC_SLUG>-logs-<TIMESTAMP>.log`

- Narrative: `{{outputDir}}/<TOPIC_SLUG>-narrative-<TIMESTAMP>.md`

- Additional notes, links, or references (if any).

```

Guidelines:

* Keep narrative concise but complete.

* Emphasize **why** choices were made, not just the mechanics.

* Mention important dead ends and what was learned from them.

* Refer to logs by filename instead of pasting them.

* Do not produce partial or recency-only summaries; all sections must reflect the full transcript from first prompt to last.

---

## 8. Final Response in Cursor

Your response to the user when this command runs should be:

1. The full contents of `<TOPIC_SLUG>-narrative-<TIMESTAMP>.md`.

2. A short footer listing the final files in `{{outputDir}}`, for example:

```md

> Files written to {{outputDir}}:

> - <TOPIC_SLUG>-summary-<TIMESTAMP>.md — working summary

> - <TOPIC_SLUG>-logs-<TIMESTAMP>.log — meaningful command logs

> - <TOPIC_SLUG>-narrative-<TIMESTAMP>.md — final narrative document





