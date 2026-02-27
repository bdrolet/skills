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
   - Links: keep as `[text](https://example.com)`.
   - Lists: keep `- item` / `1. item`; indent with two spaces for nesting.
   - Blockquotes: keep with leading `>`.
   - Code blocks: keep fenced blocks with triple backticks and language if present.
   - Images: drop image markup; keep the alt text + URL in plain text.
   - Tables: flatten to simple bullet lists or short sections (header + rows in bullets).
   - Horizontal rules and HTML: remove unless needed as plain text.

3. **Summarize when long**
   - If the document is lengthy or repetitive, create a concise Slack-ready summary first (goal: < ~1200 words, ideally a few short sections).
   - Preserve critical details, decisions, action items, owners, and due dates.
   - Provide a compact structure: a short intro line, bullets for key points, then optional detail blocks.

4. **Output**
   - Save the result in the current directory using the same base name with a `.slack.md` suffix (e.g., `notes.md` → `notes.slack.md`).
   - Return Slack-ready text only (no extra wrappers) as the file content.
   - If content was summarized, note that it's a summary and offer to provide full detail if needed.

5. **Safety**
   - Do not include secrets, tokens, or credentials.
   - Keep a professional, concise tone suitable for posting in Slack.

## Requirements

- Source file must be Markdown.
- Output must be valid Slack markup and concise enough to paste directly into a channel or DM.

