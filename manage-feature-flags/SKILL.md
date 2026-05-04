---
name: manage-feature-flags
description: Get and set Redis-backed feature flags in local, staging, and production. Use when the user wants to check feature flag status, enable or disable a feature flag, toggle a flag, or manage flags across environments.
---

# Manage Feature Flags

Get or set Redis-backed boolean feature flags in local, staging, or production.

## Flag Registry

> **Source of truth:** `mastra/src/lib/feature-flags.ts` — every flag reader is exported from that file. If it doesn't appear there, it isn't a managed feature flag. Always cross-check the table below against that file (and the key constants in `mastra/src/lib/constants.ts`) before acting; update this skill if they drift.

| Flag | Redis Key | Code Function | Purpose |
|------|-----------|---------------|---------|
| Initial Engagement Mastra | `initial_engagement:mastra_enabled` | `getInitialEngagementMastraEnabled()` | Route initial-engagement to Mastra agent vs n8n |
| AI Dispatcher | `ai_dispatcher:sub_workflows_enabled` | `getAiDispatcherEnabled()` | Route dispatcher types to per-type Mastra sub-workflows |
| Member Data Direct | `member_data:mastra_direct_enabled` | `getMemberDataDirectEnabled()` | IE agent uses granular Steward/Snowflake tools directly instead of the monolithic `getMemberDataTool` that proxies through n8n |

Flag key constants live in `mastra/src/lib/constants.ts` (`INITIAL_ENGAGEMENT_CACHE`, `AI_DISPATCHER_CACHE`, `MEMBER_DATA_DIRECT`) and are registered in `FEATURE_FLAG_REGISTRY` in the same file (used for `localDefault` fallback in development).

Values: `"1"` or `"true"` = enabled; anything else (missing, `"0"`, `"false"`, empty) = disabled.

Fallback behavior (see `getRedisFlag` in `feature-flags.ts`):
- **Local dev** (`NODE_ENV === 'development'`) with missing Redis or missing/empty key → falls back to `localDefault` from `FEATURE_FLAG_REGISTRY`.
- **Staging / production** with missing key or Redis error → defaults to `false`.
- An explicit Redis value always wins, including in local dev.

## How to Run Redis Commands

| Environment | Method |
|-------------|--------|
| **Local** | `redis-cli -u "$REDIS_URL"` or Node one-liner with `REDIS_URL` from `mastra/.env` |
| **Staging / Production** | Follow the [connect-redis](../connect-redis/SKILL.md) skill (ECS Exec into the Mastra container) |

Use the generic GET/SET commands from `connect-redis`, substituting the flag key from the registry above.

## Workflow

When the user asks to check or change a flag:

1. Identify which flag(s) and which environment(s).
2. **GET first** -- always show current value before changing.
3. If changing, **confirm with the user** before SET on staging or production.
4. After SET, GET again to verify the change took effect.

## Requirements

- **Local**: `REDIS_URL` set in `mastra/.env`; Node.js available
- **Remote**: AWS CLI configured, Session Manager plugin installed, IAM permissions for `ecs:ExecuteCommand` and `ssm:StartSession`
