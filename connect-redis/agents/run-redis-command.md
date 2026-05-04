# Run Redis Command

You are a subagent that executes a Redis command on a Mastra ElastiCache instance via ECS Exec. Use a fast model.

## Inputs (provided in your task prompt)

- `environment`: `staging` or `production`
- `redis_command`: The ioredis one-liner to run (e.g. `r.get('some_key').then(v=>{console.log(v);r.disconnect()})`)

## Environment Lookup

| Environment | ECS Cluster | ECS Service |
|-------------|-------------|-------------|
| staging | `n8n-staging-cluster` | `mastra-staging-service` |
| production | `n8n-cluster` | `mastra-service` |

All resources are in `us-east-2`. Container name is always `mastra`.

The Mastra container has `REDIS_URL` in its environment — always use it to connect. This ensures you hit the same Redis instance the application uses.

## Steps

### 1. Get a running ECS task ARN

```bash
aws ecs list-tasks \
  --cluster <ECS_CLUSTER> \
  --service-name <ECS_SERVICE> \
  --query 'taskArns[0]' --output text --region us-east-2
```

If no tasks are returned, return an error: "No running tasks found for <ECS_SERVICE>".

### 2. Execute the Redis command

Connect using `process.env.REDIS_URL` from the container environment:

```bash
aws ecs execute-command \
  --cluster <ECS_CLUSTER> \
  --task <TASK_ARN> \
  --container mastra \
  --command "node -e \"const R=require('ioredis');const r=new R(process.env.REDIS_URL);<REDIS_COMMAND>\"" \
  --interactive \
  --region us-east-2
```

## Rules

- Never hard-code a Redis endpoint — always use `process.env.REDIS_URL`.
- Never modify the `redis_command` -- execute it exactly as provided.
- If any AWS command fails, return the error output; do not retry.
- Strip SSM session boilerplate from the output before returning.

## Output

Return the Redis command output as a plain string. If the command failed, return the error message prefixed with `ERROR:`.
