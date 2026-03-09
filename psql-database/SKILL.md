---
name: psql-database
description: Access PostgreSQL databases via psql and ~/.pg_service.conf with read-only guardrails. Only use when manually invoked by the user.
---

# PostgreSQL Database Access

## Connection

Connect using `pg_service.conf` services:

```bash
psql "service=<service-name>"
```

### Discover available services

```bash
grep '^\[' ~/.pg_service.conf | tr -d '[]'
```

## READ-ONLY BY DEFAULT

**All queries MUST be read-only unless the user explicitly asks to modify data.**

### Read-only enforcement

Wrap every SELECT in a read-only transaction:

```bash
psql "service=<service>" -c "BEGIN TRANSACTION READ ONLY; <query>; COMMIT;"
```

Or for multi-statement exploration:

```bash
psql "service=<service>" <<'SQL'
BEGIN TRANSACTION READ ONLY;
-- queries here
COMMIT;
SQL
```

### What counts as explicit write permission

The user must **specifically ask** to insert, update, delete, create, alter, drop, or truncate. Phrases like:

- "update the row where..."
- "delete records that..."
- "insert a new entry for..."
- "create a table called..."
- "run this migration"

If ambiguous, **ask for confirmation before executing any write**.

### Write operations (only when explicitly requested)

When the user explicitly asks for a write:

1. **Show the exact SQL** you plan to run and ask for confirmation
2. **Wrap in a transaction** so it can be rolled back on error:

```bash
psql "service=<service>" <<'SQL'
BEGIN;
-- write statement here
-- Verify the result:
-- SELECT ... to confirm the change
COMMIT;
SQL
```

3. If anything looks wrong, `ROLLBACK` instead of `COMMIT`

### Forbidden without explicit request

Never run these unprompted, even if they seem helpful:
- `INSERT`, `UPDATE`, `DELETE`
- `CREATE`, `ALTER`, `DROP`, `TRUNCATE`
- `GRANT`, `REVOKE`
- Any DDL or DML that modifies state

## Common tasks

### Explore schema

```bash
# List tables
psql "service=<service>" -c "BEGIN TRANSACTION READ ONLY; SELECT tablename FROM pg_tables WHERE schemaname = 'public'; COMMIT;"

# Describe a table
psql "service=<service>" -c "\d <table_name>"

# List columns with types
psql "service=<service>" -c "BEGIN TRANSACTION READ ONLY; SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '<table>' ORDER BY ordinal_position; COMMIT;"
```

### Query data

```bash
# Always limit results to avoid flooding output
psql "service=<service>" -c "BEGIN TRANSACTION READ ONLY; SELECT * FROM <table> LIMIT 25; COMMIT;"
```

### Output formatting

Use these flags for readable output:

| Flag | Purpose |
|------|---------|
| `-x` | Expanded (vertical) display for wide rows |
| `--csv` | CSV output for export |
| `-H` | HTML table output |
| `-t` | Tuples only (no headers/footers) |
| `-A` | Unaligned output |

## Safety rules

1. **Always `LIMIT` queries** — default to `LIMIT 25` unless the user specifies otherwise
2. **Never dump entire tables** without an explicit request and row-count check first
3. **Confirm the target service** before running queries if the user hasn't specified one
4. **Treat production services with extra caution** — any service with `prod` in the name gets a confirmation prompt before writes
5. **No credential exposure** — never print or reference passwords from `pg_service.conf`
