---
name: inspect-snapshot-response
description: Read the dispatcher test result JSON for a snapshot type, identify data gaps, and return a PHI-masked structural summary ready to post to a PR.
---

# Inspect Snapshot Response

Reads the response JSON produced by `test_ai_dispatcher.py`, inspects its structure, flags
any data gaps, and returns a PHI-masked summary safe to include in a PR comment.

## Inputs

- `results_dir`: absolute path to the timestamped results folder (e.g.
  `mastra/scripts/debug/results/test-dispatcher-20260424-213120/`)
- `snapshot_type`: dispatcher type string (e.g. `toc-admit`)

## Steps

### Step 1 — Read the result JSON

```bash
cat <results_dir>/<snapshot_type>.json
```

Extract:
- `status` — PASS or FAIL
- `http_status` — HTTP response code
- `elapsed_seconds` — response time
- `text_length` — character count of the response text
- `response.data.response.text` — the full LLM-generated text (handle with care — PHI)
- `error` — error message if status is FAIL

### Step 2 — Parse the response text structure

Read the response `text` and identify which output sections are present. For each section
defined in the snapshot's `mastra/src/prompts/<snapshot-type>.md`, note:
- **Populated** — section has real data
- **Gap** — section says "not available", "not explicitly listed", or equivalent
- **Missing** — section is absent from the output entirely

Do NOT include the raw text content. Work only with structure and metadata.

### Step 3 — Apply PHI masking rules

When preparing the summary, apply these rules to any content derived from the response text:

| Content type | Rule |
|---|---|
| Provider / clinician names | Replace with `[PROVIDER NAME]` |
| Clinical diagnoses | Replace with `[DIAGNOSIS]` |
| Specific dates (admit, discharge, visit) | Replace with `[DATE]` |
| Facility OIDs (numeric dot-separated, e.g. `2.16.840.1.113883...`) | Replace with `[FACILITY ID]` |
| Facility human-readable names | Replace with `[FACILITY NAME]` |
| Member names, DOB, address | Replace with appropriate `[MEMBER *]` placeholder |
| Raw response text | Never include verbatim — describe structurally only |

### Step 4 — Check server logs for errors (if FAIL or partial data)

If the test failed or sections have gaps, check the Mastra dev server log for the most
recent request to identify the root cause:

```bash
grep -A 5 "<snapshot_type>\|FetchCoreMemberData\|SnowflakeClient.*failed\|not authorized" \
  /path/to/mastra-server.log | tail -30
```

Classify the failure:
- **Snowflake grant missing** — `does not exist or not authorized` → local limitation, staging/prod have grants
- **Steward connection refused** — `ECONNREFUSED` on port 15432 → SSM tunnel down
- **LLM not configured** — response text is the fallback message → `LITELLM_BASE_URL` unset

## Output

Return a structured result with all PHI masked:

```
## Snapshot test result — <snapshot_type>

**Status:** PASS / FAIL (HTTP <code>, <elapsed>s, <char_count> chars)

**Response structure:**
- <Section name>: populated / gap ("not available") / missing
- <Section name>: populated / gap ("not available") / missing
- ...

**Data gaps noted:**
- <section>: <reason — e.g. "no medications query in fetchClinicalData">
- ...  (or "None" if all sections populated)

**Failure cause (if FAIL):**
- <classified cause from server logs, or "N/A">

**Local limitations (expected, not regressions):**
- <e.g. "Snowflake grant missing for GEN_AI.PUBLIC.MIHIN_ADT — works in staging/prod">
- ...  (or "None")
```
