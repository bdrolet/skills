---
name: ship-snapshot
description: Full ship workflow for a snapshot service migration (CI → PR → local E2E test → pr-post). Use when completing a snapshot migration from n8n to direct Snowflake/Postgres fetch. Runs CI checks, opens the PR, verifies the snapshot locally, and posts PHI-masked results.
---

# Ship Snapshot

End-to-end workflow for shipping a completed snapshot service migration. Each phase delegates
to an existing skill — no logic is duplicated here. Designed for Tier 1–3 snapshot migrations
described in `mastra/docs/snapshot-n8n-to-direct-migration.md`.

## Inputs

- **Snapshot type** — infer from the conversation context (e.g. which service file was just
  implemented, what the user said they were working on). Maps to the dispatcher type string:
  `toc-admit`, `toc-discharge`, `chronic-heart-failure`, `general-member-snapshot`,
  `new-stew-member-benefits`, `welcome-call`, `welcome-visit`. Only ask the user if it
  cannot be determined from context.
- **Feature branch** — check with `git branch --show-current`. If still on `main`, the
  `pr-open` skill (Phase 2) will create the feature branch as part of the PR flow. No manual
  branch creation is needed — just ensure all changes are committed or stashed before Phase 2
  runs.

---

## Phase 1 — CI checks

**Invoke:** `.cursor/skills/running-ci-checks/SKILL.md`

Do not proceed to Phase 2 until all 4 checks (typecheck, lint, unit-tests, build) pass.

**Known failure patterns specific to snapshot migrations** (fixes to apply before re-running):

| Error | Fix |
|---|---|
| `TS2556: A spread argument must either have a tuple type` in `*.test.ts` mock factories | Cast the mock: `(...args: unknown[]) => (mockFn as (...a: unknown[]) => unknown)(...args)` |
| `TS18046: 'result.response' is of type 'unknown'` in test assertions | Add type cast: `(result.response as { text: string }).text` — `response: z.unknown()` in `workflow.schema.ts` is intentional |

---

## Phase 1b — Re-verify after merging `main` into the branch

If `origin/main` was merged into the feature branch at any point (resolving conflicts, picking up new flags, etc.), **re-run Phase 1 in full** before relying on prior CI results. Typecheck alone is not sufficient — a clean merge can still break the *branch's own* runtime surface or introduce lint regressions.

**Re-invoke:** `.cursor/skills/running-ci-checks/SKILL.md` (do not duplicate its steps here).

**Merge-specific guardrails on top of Phase 1:**

- When running vitest, confirm the test file(s) for *this branch's primary feature* are in the run, not just files touched by `main`. A narrow scope like `src/lib` plus the merged-in test file leaves the branch's own surface unverified.
- If any check fails post-merge, create a **new follow-up commit** on the branch. Do not `git commit --amend` the merge commit and do not force-push.
- After all four checks pass, run `gh pr view <pr-number> --json mergeable,mergeStateStatus,statusCheckRollup` and confirm `MERGEABLE` / `CLEAN` before continuing to Phase 2 (or Phase 4 if the PR is already open).

---

## Phase 2 — Open PR

**Invoke:** `~/.claude/skills/pr-open/SKILL.md`

**Snapshot migration PR description must include:**
- Which direct-data query functions the new path calls and in what order
- The Redis feature flag key and its local default (`localDefault: true`)
- That the legacy n8n generation workflow is preserved as the flag-off fallback
- A link to `mastra/docs/snapshot-n8n-to-direct-migration.md` as the migration guide

---

## Phase 3 — Local E2E test

### Step 3a — Start services

**Invoke:** `.cursor/skills/starting-local-dev/SKILL.md`

After services are up, verify the Mastra dev server is running on the **feature branch**,
not `main`. If the server hot-reloaded to `main` (e.g. after a `git checkout main` for a
prior commit), kill and restart it on the feature branch:

```bash
lsof -ti :3001 | xargs kill -9
cd mastra && npm run dev
```

### Step 3b — Start Steward SSM tunnel

**Invoke:** `.cursor/skills/connect-steward-db/SKILL.md`

All snapshot migrations require this tunnel because `fetchCoreMemberData` connects to
Steward Postgres on `localhost:15432`. Start the tunnel before running the test.

### Step 3c — Run the dispatcher test

**Invoke:** `.cursor/skills/test-ai-dispatcher/SKILL.md`

Run with `--target mastra-local --force-refresh --no-open` for the snapshot type:

```bash
source mastra/scripts/debug/.venv/bin/activate && \
python3 mastra/scripts/debug/scripts/test_ai_dispatcher.py \
  --target mastra-local -t <snapshot-type> --force-refresh --no-open -v
```

**Expected failure modes (not bugs — document in PR, do not block ship):**

| Symptom | Cause | How to confirm | Action |
|---|---|---|---|
| 500 with `does not exist or not authorized` in Mastra logs | Snowflake role lacks grant on a table locally (e.g. `GEN_AI.PUBLIC.MIHIN_ADT`) | Check server logs: `grep "not authorized"` | Document as local limitation; grants exist in staging/prod |
| 500 with `ECONNREFUSED` | Steward SSM tunnel not running | `lsof -i :15432` | Re-run Step 3b |
| 200 but response text is the LLM-not-configured fallback | `LITELLM_BASE_URL` not set in `mastra/.env` | `grep LITELLM_BASE_URL mastra/.env` | Expected in envs without LiteLLM; verify env var exists |

### Step 3d — Inspect the response

**Invoke:** `subagents/inspect-snapshot-response.md`

Pass it the path to the latest results directory and the snapshot type. It reads the
response JSON, identifies any data gaps (empty sections, "not available" text), and returns
a PHI-masked rendering of the raw response text ready for Phase 4.

---

## Phase 4 — Post results to PR

**Invoke:** `~/.claude/skills/pr-post/SKILL.md`

Post **two** comments to the PR — they serve different reviewer needs:

1. **E2E results comment** — pass/fail, timings, server-log path verification (direct vs.
   n8n), per-dependency latency, generation stats. No response text.
2. **Raw response (PHI masked) comment** — the verbatim response `text` field with every
   PHI token replaced inline. Preserves header, JSON envelopes (`:::component:citationBullet
   { ... } :::`), section ordering, prompt template placeholders (`{{MEMBER_PROFILE_URL}}`,
   `{{ATHENA_MEMBER_URL}}`), and line breaks so reviewers can validate prompt-format
   compliance and section coverage at a glance. Include a small "what was masked" table at
   the bottom listing the placeholders used.

The `pr-post` skill's default policy is to never paste AI-generated member narratives
verbatim. For the raw-response comment we override that policy because (a) every PHI token
is replaced inline before posting and (b) reviewers genuinely need to see the structural
output to spot prompt regressions. The override applies only when every rule below is
satisfied — if any check fails, fall back to a structural-only description.

**Required masking rules for the raw-response comment:**

| Token | Replace with |
|---|---|
| Member name (header, transcripts, anywhere) | `[MEMBER NAME]` |
| Provider / clinician names | `[PROVIDER NAME]` |
| Practice / facility group names | `[PRACTICE GROUP]` |
| Member city / state / address | `[LOCATION]` |
| Specific contact channel ("mobile phone", "email") | `[CONTACT METHOD]` |
| All specific dates and date ranges | `[DATE]` |
| Times of day | `[TIME]` |
| Timezones (reveals geographic region) | `[TZ]` |
| Specific diagnoses (ICD-level or named conditions) | `[DIAGNOSIS]` |
| Lists of chronic conditions | `[CHRONIC CONDITIONS]` |
| Wound / lab / imaging / procedure narratives | `[CLINICAL DETAIL]` |
| Appointment / encounter / EHR UUIDs in `href` | `[APPT ID]` / `[ENCOUNTER ID]` |
| Athena IDs, member plan IDs, MRNs | `[EHR ID]` / `[PLAN ID]` / `[MRN]` |
| Phone / fax numbers, email addresses | `[PHONE]` / `[EMAIL]` |
| Facility OIDs (e.g. `2.16.840.1.113883...`) | `[FACILITY ID]` (not PHI but noise) |

**Things that stay unmasked** (not PHI, useful for review):

- Section titles (`Engagement`, `PCP`, `Upcoming Appointments`, etc.)
- Section `type` and `source` fields (`steward`, `athena`)
- JSON field names (`title`, `text`, `href`, `tooltip`, `newTab`)
- Prompt template tokens (`{{MEMBER_PROFILE_URL}}`, `{{ATHENA_MEMBER_URL}}`)
- Counts and aggregate numbers ("13 prior calls", "231 records")
- Visit/appointment type labels ("Care Management - Initial", "SCHEDULED")
- Generation stats (model, durations, char counts)

**Final gate before posting:** read the masked draft top to bottom and confirm no real
names, dates, locations, diagnoses, or identifiers slipped through. If any did, mask them
or fall back to the structural-only summary.

---

## Phase execution order

```
Phase 1:  running-ci-checks         ← fix failures before continuing
            ↓ all pass
Phase 1b: running-ci-checks (re-run) ← only if main was merged into the branch
            ↓ all pass + gh pr view reports MERGEABLE
Phase 2:  pr-open                   ← creates PR
            ↓
Phase 3a: starting-local-dev        ← backing services + dev server
            ↓
Phase 3b: connect-steward-db        ← SSM tunnel on localhost:15432
            ↓
Phase 3c: test-ai-dispatcher        ← runs dispatcher test locally
            ↓
Phase 3d: inspect-snapshot-response ← reads JSON, masks PHI (unique subagent)
            ↓
Phase 4: pr-post                    ← posts (1) E2E results, (2) raw masked response
```
