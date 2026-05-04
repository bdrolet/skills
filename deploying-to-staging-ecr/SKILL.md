---
name: deploying-to-staging-ecr
description: Build and push a Mastra Docker image to the eng-staging ECR, then deploy to the new staging ECS service. Use when the user wants to manually deploy to the new staging environment (account 962254627709), push an image to the staging ECR, or force a redeployment of the ecs-stage-use2-01/mastra-staging service.
---

# Deploying to Staging ECR

Build a `linux/amd64` Docker image from the Mastra source and push it to the eng-staging ECR in the core management account, then deploy to the new staging ECS cluster.

## Architecture

| Component | Value |
|-----------|-------|
| ECR registry | `950958439470.dkr.ecr.us-east-2.amazonaws.com` |
| ECR repo | `staging/ai-platform/mastra` |
| ECS cluster | `ecs-stage-use2-01` |
| ECS service | `mastra-staging` |
| AWS account | `962254627709` (eng-staging) |
| AWS profile | `eng-staging` |
| Public URL | `https://mastra.stage.aws.homewardhealth.com` |

## Prerequisites

- `eng-staging` AWS profile configured and role assumption working
- Docker running with `buildx` support

Verify access:
```bash
AWS_PROFILE=eng-staging aws sts get-caller-identity
# Must show Account: 962254627709
```

## Steps

### 1. Login to ECR

```bash
AWS_PROFILE=eng-staging aws ecr get-login-password --region us-east-2 \
  | docker login --username AWS --password-stdin 950958439470.dkr.ecr.us-east-2.amazonaws.com
```

### 2. Build and push (linux/amd64)

From `mastra/` directory. The `--platform linux/amd64` flag is **required** — Fargate runs amd64, local Mac builds arm64 by default.

```bash
cd mastra && mkdir -p certs
SHORT_SHA=$(git rev-parse --short HEAD)

docker buildx build \
  --platform linux/amd64 \
  --build-arg NPM_TOKEN="$(gh auth token)" \
  --build-arg GIT_SHA="$SHORT_SHA" \
  --build-arg BUILD_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --build-arg INCLUDE_SSL_CERT=false \
  -t "950958439470.dkr.ecr.us-east-2.amazonaws.com/staging/ai-platform/mastra:${SHORT_SHA}-staging" \
  -t "950958439470.dkr.ecr.us-east-2.amazonaws.com/staging/ai-platform/mastra:latest" \
  --push \
  .
```

Build takes ~5-8 minutes (cross-compilation via QEMU).

### 3. Deploy to ECS

```bash
AWS_PROFILE=eng-staging aws ecs update-service \
  --cluster ecs-stage-use2-01 \
  --service mastra-staging \
  --force-new-deployment \
  --region us-east-2
```

### 4. Verify

Wait ~90 seconds for the task to start and pass health checks.

```bash
curl -s https://mastra.stage.aws.homewardhealth.com/health
# Expected: {"success":true}
```

Or check target health directly:
```bash
AWS_PROFILE=eng-staging aws elbv2 describe-target-health \
  --target-group-arn "arn:aws:elasticloadbalancing:us-east-2:962254627709:targetgroup/mastra-staging-tg/324693f0915228d8" \
  --region us-east-2 --query 'TargetHealthDescriptions[*].TargetHealth.State'
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `platform 'linux/amd64'` error | Built on arm64 without `--platform` | Rebuild with `--platform linux/amd64` |
| `DATABASE_URL is not set` | ASM secrets are placeholders | See `mastra/docs/seed-staging-secrets-prompt.md` |
| `CannotPullContainerError: not found` | Image tag missing in ECR | Verify push succeeded, check tag name |
| 503 from ALB | No healthy targets / no running tasks | Check `aws ecs describe-services` events |
| ECR login fails | `eng-staging` role assumption expired | Re-run `AWS_PROFILE=eng-staging aws sts get-caller-identity` to test |

## CI/CD Note

The GitHub Actions workflow `mastra-3-staging.yml` handles this automatically on merge to `main`. This skill is for **manual** deployments (hotfixes, debugging, or when CI/CD isn't pushing to this ECR yet). The workflow requires `AWS_ENG_STAGING_ACCESS_KEY_ID` / `AWS_ENG_STAGING_SECRET_ACCESS_KEY` secrets to be configured in GitHub.
