---
name: starting-local-dev
description: Use when starting local development, running the dev server, launching Mastra locally, or bringing up local services like PostgreSQL, Redis, n8n, and Langfuse
---

# Starting Local Dev

Start all backing services and the Mastra dev server for local development.

## Prerequisites

- Docker running (required for PostgreSQL, Redis, n8n, Langfuse)
- `langfuse/.env` exists (copy from `langfuse/env.example` if missing)

## Steps

### 1. Start backing services

Run from the **repo root** (`ai-platform-images/`):

```bash
./scripts/start-all-services.sh
```

Pass `--no-langfuse` to skip the Langfuse observability stack.

Wait for the status summary confirming services are ready before proceeding.

### 2. Start Mastra dev server

In a **separate terminal**, from the `mastra/` directory:

```bash
cd mastra
npm run dev
```

The server is ready when you see:

```
mastra  x.x.x ready in XXX ms
│ Studio: http://localhost:3001
│ API:    http://localhost:3001/api
```

## Service URLs

| Service | URL |
|---------|-----|
| Mastra API | http://localhost:3001/api |
| Mastra Studio | http://localhost:3001 |
| Mastra Health | http://localhost:3001/health |
| PostgreSQL | `postgresql://mastra:mastra_local_dev@localhost:5433/mastra` |
| Redis | `redis://localhost:6379` |
| n8n | http://localhost:5678 |
| Langfuse | http://localhost:3100 |

## Stopping

```bash
./scripts/stop-all-services.sh
```
