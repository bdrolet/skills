---
name: fetching-meeting-transcripts
description: Use when the user asks to fetch, download, pull, or save meeting transcripts, meeting notes, or Google Meet recordings for a date or date range
---

# Fetching Meeting Transcripts

Fetch Google Meet transcripts from calendar events and save them as Markdown.

## Execution

Spawn a **shell** subagent with the `fast` model to run the script. Do not run it inline -- delegate so the agent can proceed with other work while transcripts download.

```
Task tool parameters:
  subagent_type: "shell"
  model: "fast"
  prompt: "Run: cd ~/src/scripts/python && python3 scripts/fetch_meeting_transcripts.py --date <DATE>
           Return the full output including which files were saved and any errors."
```

Replace `<DATE>` with the requested date (YYYY-MM-DD). Omit `--date` entirely for today.

Output: `~/src/scratchapad/meeting_notes/`.

## What it does

1. Pulls events for the given day via `GoogleCalendarClient`
2. Finds Google Docs attachments on events (e.g. "Notes by Gemini")
3. Exports each doc as Markdown via `GoogleDocsClient`
4. Extracts only the transcript section (from `## ... - Transcript` heading to end)
5. Saves as `YYYY-MM-DD_<meeting-title>.md`

Events without transcripts are silently skipped.

## Date ranges

The script handles one day at a time. For a range, loop:

```bash
for d in 2026-03-{10..14}; do
  python3 scripts/fetch_meeting_transcripts.py --date "$d"
done
```

## Prerequisites

- OAuth token must exist (`google_calendar_token.json` and `google_docs_token.json` in `~/src/scripts/python/`). If missing, the script opens a browser for consent on first run.
- Google Calendar API and Drive API enabled in GCP project `optimal-drummer-486221-b1`.

## Underlying clients

| Client | File | Scope |
|--------|------|-------|
| `GoogleCalendarClient` | `python/clients/google_workspace/calendar.py` | `calendar.readonly` |
| `GoogleDocsClient` | `python/clients/google_workspace/docs.py` | `drive.readonly` |
