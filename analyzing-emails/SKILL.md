---
name: analyzing-emails
description: Use when the user wants to analyze, triage, or process emails from their Outlook inbox, check for action items, or get email recommendations
---

# Analyzing Emails

Runs the email analysis script at `python/scripts/analyze_emails.py` in the `scripts` repo. The script fetches emails via Microsoft Graph, sends each through OpenAI (gpt-3.5-turbo) for triage, and outputs prioritized action recommendations.

## Prerequisites

The file `python/.env` must contain:
- `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` (Azure app registration)
- `OPENAI_API_KEY`

## Running

Always run from the `python/` directory with unbuffered output (stdout is buffered when not a tty):

```bash
cd python && python3 -u scripts/analyze_emails.py 2>&1
```

## Authentication

The script uses Microsoft Graph **device code flow**. On first run (or expired token), it prints a URL and code like:

```
To sign in, use a web browser to open the page:
  https://login.microsoft.com/device
and enter the code: XXXXXXXX
```

Show this to the user and wait for them to confirm sign-in before expecting further output. Subsequent runs use a cached token (`.token_cache.json`).

## Customizing the run

The default `main()` processes 10 latest emails. To change the count, edit line `processor.process_latest_emails(count=10)` in `python/scripts/analyze_emails.py` before running.

Available processing modes in `EmailProcessor`:
- `process_latest_emails(count=N)` — N most recent emails
- `process_all_emails()` — all emails in folder (paginated)
- `process_unread_emails()` — all unread emails
- `process_emails_since(datetime)` — emails after a given time

## Timing expectations

Each email takes ~40 seconds (sequential OpenAI calls). Budget accordingly:
- 10 emails ≈ 7 minutes
- 50 emails ≈ 35 minutes
- Use `block_until_ms: 0` and poll the terminal file for large runs
