---
name: connect-redis
description: Connect to Mastra ElastiCache Redis in staging or production via ECS Exec. Use when the user needs to query Redis, check feature flags, inspect cache, run redis-cli, or debug Redis on staging or production.
---

# Connect to Mastra Redis

Run Redis commands on private ElastiCache instances via ECS Exec into the Mastra container.

## Environments

| Environment | ECS Cluster | ECS Service | Container | Region |
|-------------|-------------|-------------|-----------|--------|
| **Staging** | `n8n-staging-cluster` | `mastra-staging-service` | `mastra` | `us-east-2` |
| **Production** | `n8n-cluster` | `mastra-service` | `mastra` | `us-east-2` |

The Mastra container has `REDIS_URL` set in its environment. Always connect using `process.env.REDIS_URL` to ensure you hit the same Redis instance the application uses.

**Important:** Production has two separate Redis instances. The Mastra app uses `mastra-production-redis`, NOT `n8n-production-redis`. Never hard-code an ElastiCache endpoint — always use `process.env.REDIS_URL`.

## Running Commands

To execute a Redis command, read the subagent prompt at `agents/run-redis-command.md` in this skill directory, then spawn it via the Task tool with `model: "fast"`. Pass it:

- `environment`: `staging` or `production`
- `redis_command`: An ioredis one-liner from the table below

The subagent handles endpoint discovery, ECS task lookup, and ECS Exec automatically.

### Common ioredis one-liners

| Operation | `redis_command` |
|-----------|-----------------|
| PING | `r.ping().then(v=>{console.log(v);r.disconnect()})` |
| GET | `r.get('KEY').then(v=>{console.log(v);r.disconnect()})` |
| SET | `r.set('KEY','VALUE').then(v=>{console.log(v);r.disconnect()})` |
| KEYS | `r.keys('PATTERN*').then(v=>{console.log(JSON.stringify(v,null,2));r.disconnect()})` |
| DEL | `r.del('KEY').then(v=>{console.log(v);r.disconnect()})` |
| TTL | `r.ttl('KEY').then(v=>{console.log(v);r.disconnect()})` |

## Common Mastra Redis Keys

| Key | Purpose | Values |
|-----|---------|--------|
| `initial_engagement:mastra_enabled` | Feature flag: route initial-engagement to Mastra vs n8n | `"1"` = enabled, `"0"` = disabled |
| `ai_dispatcher:sub_workflows_enabled` | Feature flag: route dispatcher types to per-type Mastra sub-workflows | `"1"` = enabled, `"0"` = disabled |
| `initial_engagement:INITIAL_ENGAGEMENT_RESPONSE:<memberId>` | Cached engagement summary | JSON blob |

## Requirements

- AWS CLI configured with default profile
- Session Manager plugin installed (`brew install --cask session-manager-plugin`)
- IAM permissions for `ecs:ExecuteCommand` and `ssm:StartSession`

## Notes

- Redis instances are in private subnets (`vpc-078f1ac889cdabd95`); not reachable via VPN or jumpbox
- Production Mastra uses `mastra-production-redis` (ElastiCache), **not** `n8n-production-redis`
- Terraform: staging at `~/src/Infra/environments/staging/mastra/redis.tf`, production at `~/src/Infra/environments/production/mastra/redis.tf`
