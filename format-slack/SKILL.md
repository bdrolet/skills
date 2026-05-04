---
name: format-slack
description: Format Slack
disable-model-invocation: true
---

# Format Slack

## Overview

Convert a Markdown file to Slack-friendly markup and condense long documents so they're easy to paste into Slack.

title: "Format Slack"

command: "format-slack"

description: "Convert a Markdown file to Slack-friendly markup and optionally summarize it, then save the result beside the source file."

arguments:
  - name: sourceFile
    description: "Path to the source Markdown file to convert to Slack-friendly markup."
    default: ""

## Steps

1. **Input**
   - Ask for the path to the source `*.md` file (absolute or relative).
   - Read the file content; if the file is missing or not Markdown, stop and ask for a valid file.

2. **Transform to Slack markup (https://slack.com/help/articles/360039953113-Format-your-messages-in-Slack-with-markup)**
   - Headings: convert `#`, `##`, etc. to a bold line like `*Heading text*` followed by a newline.
   - Bold/italic/strikethrough/code: keep or translate to `*bold*`, `_italic_`, `~strike~`, `` `inline` ``.
   - Links: keep as `[text](https://example.com)`. Do NOT convert to Slack's native `<url|text>` format.
   - Jira tickets: when a ticket key appears (e.g. `GENAI-201`, `DATAENG-1395`), convert it to a link using the pattern `[TICKET-KEY](https://homewardhealth.atlassian.net/browse/TICKET-KEY)`. Apply this to any `PROJECT-NUMBER` pattern that looks like a Jira key.
   - Lists: keep `1. item` for numbered items. Use `•` for unordered bullets.
   - Nested/sub-bullets: indent with *4 spaces* before the bullet character per nesting level (up to 5 levels).
   - Multi-level nesting works: 4 spaces = level 1, 8 spaces = level 2, 12 spaces = level 3, etc.
   - Use nested structure to group related items under a parent. For example, a standup update with multiple topics can use a single numbered item with `•` sub-bullets for each topic, and `•` sub-sub-bullets (8 spaces) for details under each topic.
   - Example:
     ```
     1. *Project Name:*
         • *Feature A:*
             • Detail about feature A.
             • _Another detail (italic for emphasis)._
         • *Feature B:*
             • Detail about feature B.
     2. Next top-level item.
     ```
   - Blockquotes: keep with leading `>`.
   - Code blocks: keep fenced blocks with triple backticks and language if present.
   - Images: drop image markup; keep the alt text + URL in plain text.
   - Tables: flatten to simple bullet lists or short sections (header + rows in bullets).
   - Horizontal rules and HTML: remove unless needed as plain text.

3. **Summarize and structure**
   - Always place a *TL;DR* line near the top of the message (after the title/link, before the body). Keep it to 1–2 sentences capturing the key takeaway so readers scanning Slack get the point immediately.
   - Preserve critical details, decisions, action items, owners, and due dates.

4. **Main post vs. thread**
   - If the content fits comfortably in ~15–20 lines or fewer, keep it as a single message.
   - If the content is longer, split it into a *main post* and one or more *thread replies*. Separate each section with a `---` line so the user knows where to split when pasting.
   - *Main post* — the message posted to the channel. Keep it short and scannable:
       • Title / emoji header
       • TL;DR (1–2 sentences)
       • High-level status or key points (bullet list, ~5–8 lines max)
       • A closing line like "Details in thread." to signal there's more
   - *Thread replies* — posted as replies to the main post. Use these for:
       • Supporting details, connection strings, config values
       • Full breakdowns, per-item analysis, or long lists
       • Context that's useful but not essential for everyone to read
   - Each thread reply should have a bold title line (e.g. `*Thread: connection details*`) so readers can scan the thread quickly.
   - Aim for each thread reply to cover one topic. Prefer 2–3 focused replies over one giant reply.

5. **Output**
   - Save the result in the current directory using the same base name with a `.slack.md` suffix (e.g., `notes.md` → `notes.slack.md`).
   - After saving, copy the file content to the clipboard: `pbcopy < notes.slack.md` (substitute the actual output filename).
   - Return Slack-ready text only (no extra wrappers) as the file content.
   - If content was summarized, note that it's a summary and offer to provide full detail if needed.

6. **Safety**
   - Do not include secrets, tokens, or credentials.
   - Keep a professional, concise tone suitable for posting in Slack.

## Requirements

- Source file must be Markdown.
- Output must be valid Slack markup and concise enough to paste directly into a channel or DM.

