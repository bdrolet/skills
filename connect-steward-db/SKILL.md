---
name: connect-steward-db
description: Connect to Steward Production Postgres (readonly replica) via SSM tunnel for member data queries. Use when the user needs to query homeward_members, care_nav_members, member_facts, or other Steward tables.
---

# Connect to Steward Production Postgres

Query the Steward Production readonly replica via an SSM port-forwarding tunnel through the AWS jumpbox.

## Prerequisites

- AWS CLI configured and authenticated (`aws sts get-caller-identity`)
- SSM plugin installed (`session-manager-plugin`)
- `psql` installed (or use `node` with `pg` module)
- `DATABASE_URL_STEWARD` set in `mastra/.env`
- **AWS profile**: the jumpbox lives in the prod account — use `--profile eng-prod` (defined in `~/.aws/config`)

## Step 1: Start the SSM tunnel

Check if the tunnel is already running on port 15432:

```bash
lsof -i :15432 | grep LISTEN
```

If not running, start it:

```bash
aws ssm start-session \
  --profile eng-prod \
  --region us-east-2 \
  --target i-0c5720bfcb7002667 \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["waywardappstack-postgresprimaryreadreplica3ab5f7f3-vygfk3ev5vop.cmo4fxfp0btp.us-east-2.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["15432"]}'
```

This backgrounds automatically. The tunnel maps `localhost:15432` to the Steward RDS replica.

| Parameter | Value |
|-----------|-------|
| AWS profile | `eng-prod` (account `682983209039`) |
| Jumpbox instance | `i-0c5720bfcb7002667` (`JumpboxStack/hw-ec2-jumpbox`) |
| RDS host | `waywardappstack-postgresprimaryreadreplica3ab5f7f3-vygfk3ev5vop.cmo4fxfp0btp.us-east-2.rds.amazonaws.com` |
| RDS port | 5432 |
| Local port | 15432 |
| Region | us-east-2 |

## Step 2: Connect and query

### Option A: psql

Parse the credentials from `DATABASE_URL_STEWARD` in `mastra/.env`:

```bash
cd /Users/ben.drolet/src/ai-platform-images/mastra
DB_URL=$(grep DATABASE_URL_STEWARD .env | sed 's/DATABASE_URL_STEWARD=//' | tr -d '"')
DB_USER=$(echo "$DB_URL" | sed 's|.*://\([^:]*\):.*|\1|')
DB_PASS=$(echo "$DB_URL" | sed 's|.*://[^:]*:\([^@]*\)@.*|\1|')
DB_NAME=$(echo "$DB_URL" | sed 's|.*/\([^?]*\).*|\1|')

PGPASSWORD="$DB_PASS" psql -h localhost -p 15432 -U "$DB_USER" -d "$DB_NAME" -c "BEGIN TRANSACTION READ ONLY; <query>; COMMIT;"
```

### Option B: Node.js (pg module)

```javascript
const { Pool } = require('pg');
const pool = new Pool({
  host: 'localhost',
  port: 15432,
  database: 'wayward',
  user: 'postgres',
  password: '<from DATABASE_URL_STEWARD>',
  ssl: false,
});
```

## READ-ONLY ENFORCEMENT

This is a **production read replica**. All queries MUST be read-only.

- Wrap every query in `BEGIN TRANSACTION READ ONLY; ... COMMIT;`
- Never run INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, or TRUNCATE
- Always use LIMIT (default 25)

## Key tables

| Table | What it contains |
|-------|-----------------|
| `homeward_members` | Member demographics, contact info, provider attribution |
| `care_nav_members` | Payor/insurance fields |
| `member_facts` | Key-value member facts (filter by `factName`, e.g. `'mns_score'`) |
| `member_clinical_assessment_level` | Clinical assessment level |

## Common queries

### Core member data (same as fetchCoreMemberData)

```sql
SELECT
  hm."firstName", hm."lastName", hm."athenaId",
  cm.payor, cm."ins_plan_id", cm."plan_name",
  mf."factValue" AS mns_score,
  mcal."level" AS clinical_level
FROM homeward_members hm
  LEFT JOIN care_nav_members cm ON cm.id = hm."careNavMemberId"
  LEFT JOIN member_facts mf ON mf."homewardMemberId" = hm.id AND mf."factName" = 'mns_score'
  LEFT JOIN member_clinical_assessment_level mcal ON mcal."homewardMemberId" = hm.id
WHERE hm.id = '<member-uuid>'
```

### Find member by name

```sql
SELECT hm.id, hm."firstName", hm."lastName", hm."engagementStatus"
FROM homeward_members hm
WHERE LOWER(hm."lastName") = LOWER('<last-name>')
LIMIT 10
```

## Closing the tunnel

```bash
# Find the session PID
lsof -i :15432 | grep LISTEN

# Kill it
kill <PID>
```

Or find and kill the SSM session:

```bash
aws ssm describe-sessions --profile eng-prod --region us-east-2 --state Active --query "Sessions[?contains(Target, 'i-0c5720bfcb7002667')].SessionId" --output text | xargs -I{} aws ssm terminate-session --profile eng-prod --region us-east-2 --session-id {}
```
