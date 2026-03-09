# Skill Examples

## Simple Skill

```
code-review/
├── SKILL.md
└── references/
    └── STANDARDS.md
```

```markdown
---
name: code-review
description: Review code for quality, security, and maintainability. Use when reviewing pull requests or code changes.
---

# Code Review

1. Check for correctness and potential bugs
2. Verify security best practices
3. Assess readability and maintainability
4. Ensure tests are adequate

## Feedback Format

- **Critical**: Must fix before merge
- **Suggestion**: Consider improving
- **Nice to have**: Optional enhancement

## Resources

- [Coding standards](references/STANDARDS.md)
```

## Skill with Subagents

```
incident-report/
├── SKILL.md
└── agents/
    ├── gather-metrics.md
    ├── gather-logs.md
    └── write-report.md
```

**SKILL.md** orchestrates by reading each agent file and spawning via Task tool:

```markdown
---
name: incident-report
description: Generate post-incident reports by gathering metrics and logs. Use when the user needs an incident report, postmortem, or RCA.
disable-model-invocation: true
---

# Incident Report

Read each agent's instruction file from `agents/` before spawning.

## Step 1 — Gather data (parallel)

- **gather-metrics** (`agents/gather-metrics.md`): Pass service name and time window.
- **gather-logs** (`agents/gather-logs.md`): Pass service name and time window.

## Step 2 — Write report (sequential)

Spawn **write-report** (`agents/write-report.md`). Pass metrics and logs from step 1.

If step 1 fails, write a basic report from available context.
```

**agents/gather-metrics.md** (subagent prompt):

```markdown
# Gather Metrics

You are a subagent responsible for collecting service metrics.

## Inputs (provided in your task prompt)

- `service_name`: The service to investigate
- `time_window`: Start and end timestamps

## Steps

1. Query monitoring tools for the service
2. Capture error rates, latency, and throughput during the window
3. Identify anomalies or threshold breaches

## Output

Return: metric name, normal baseline, observed value, whether anomalous.
```
