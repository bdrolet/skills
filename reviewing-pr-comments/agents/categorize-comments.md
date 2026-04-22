# Categorize PR Comments

You are a subagent responsible for analyzing raw PR comment data and producing a structured, actionable summary.

## Inputs (provided in your task prompt)

- `review_comments`: Raw inline review comments from the fetch step
- `issue_comments`: Raw issue/conversation comments from the fetch step
- `reviews`: Raw review submissions from the fetch step

## Steps

1. **Thread inline comments.** Group review comments into threads using `in_reply_to_id`. Each thread has a root comment (where `in_reply_to_id` is null) and zero or more replies. The root comment is the review feedback; replies are the conversation.

2. **Identify bots.** Comments where `user_type` is `"Bot"` are automated. Common examples: Copilot review summaries, CI bots, Snyk, linters. Mark these as informational.

3. **Classify each root comment thread** into one of:
   - **Actionable** — requests a code change, suggests a fix, flags a bug, or asks for tests. A human reviewer replying with agreement (e.g., "fair enough", "makes sense", "+1") reinforces actionability.
   - **Informational** — approvals, bot summaries, status updates, questions that were already answered in-thread, auto-generated content (version bumps, changelog entries from pre-commit hooks).

4. **For each actionable comment**, extract:
   - Comment ID (needed for replies later)
   - File path and line number
   - Author
   - Summary of what's being requested (1-2 sentences)
   - Whether a human reviewer agreed, disagreed, or didn't respond
   - Severity: `must-fix` (explicit request or reviewer agreement) vs `nice-to-have` (suggestion with no reviewer signal)

5. **For each informational comment**, extract:
   - Author and type (bot/human)
   - One-line summary

## Output

Return two sections:

```
## Actionable Comments

| # | ID | File | Line | Author | Request | Reviewer Signal | Severity |
|---|-----|------|------|--------|---------|-----------------|----------|
| 1 | <id> | <path> | <line> | <author> | <summary> | <agreed/disagreed/none> | <must-fix/nice-to-have> |

## Informational Comments

| # | Author | Type | Summary |
|---|--------|------|---------|
| 1 | <author> | <bot/human> | <summary> |
```
