# Agent Skills Specification Reference

Full reference for the [Agent Skills open standard](https://agentskills.io/specification). Read this for detailed field constraints, validation rules, description writing guidance, and subagent patterns.

## Frontmatter Field Details

### `name` (required)

| Constraint         | Detail                                                                 |
| ------------------ | ---------------------------------------------------------------------- |
| Length             | 1-64 characters                                                        |
| Allowed characters | Unicode lowercase alphanumeric (`a-z`, `0-9`) and hyphens (`-`)        |
| Must match         | Parent directory name exactly                                          |
| Forbidden          | Leading hyphen, trailing hyphen, consecutive hyphens (`--`), uppercase |

### `description` (required)

| Constraint | Detail                                                          |
| ---------- | --------------------------------------------------------------- |
| Length     | 1-1024 characters                                               |
| Content    | Must describe what the skill does AND when to use it            |
| Keywords   | Include specific terms that help agents identify relevant tasks |
| Person     | Third person (injected into system prompt)                      |

### Writing Effective Descriptions (CSO)

The description is loaded at startup for **all** skills (~100 tokens each). The agent uses it to decide whether to activate.

**Critical rule**: Description = triggering conditions ONLY. **Never** summarize the skill's workflow. Testing shows that when descriptions summarize workflow, agents shortcut the description and skip reading the full body.

```yaml
# BAD: Summarizes workflow - agent may follow this instead of reading skill
description: Guides users through creating skills with discovery, design, implementation, and verification phases

# BAD: Too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# GOOD: Just triggering conditions, no workflow summary
description: Use when creating, writing, or authoring a new skill, or when asking about SKILL.md structure or best practices

# GOOD: Triggering conditions with symptoms
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
```

**Rules:**
- Start with "Use when..."
- Third person (injected into system prompt)
- Include specific triggers, symptoms, and keywords agents would search for
- Technology-agnostic unless the skill itself is technology-specific
- Under 500 characters recommended, max 1024

### `license` (optional)

Short license name or reference to a bundled license file.

```yaml
license: Apache-2.0
license: Proprietary. LICENSE.txt has complete terms
```

### `compatibility` (optional)

| Constraint  | Detail                                       |
| ----------- | -------------------------------------------- |
| Length      | 1-500 characters                             |
| Purpose     | Environment requirements only                |
| When to use | Only if skill has specific environment needs |

```yaml
compatibility: Designed for Claude Code (or similar products)
compatibility: Requires git, docker, jq, and access to the internet
```

### `metadata` (optional)

Arbitrary key-value map (string keys to string values). Use reasonably unique key names to avoid conflicts.

```yaml
metadata:
  author: example-org
  version: "1.0"
  category: deployment
```

### `allowed-tools` (optional, experimental)

Space-delimited list of pre-approved tools. Support varies between agent implementations.

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

### `disable-model-invocation` (optional, Cursor-specific)

When `true`, skill is only included when user types `/skill-name` in Agent chat. The agent will not automatically activate it based on context.

```yaml
disable-model-invocation: true
```

Use for: destructive operations, rarely-needed workflows, or slash-command-style skills.

## Progressive Disclosure Token Budgets

| Tier                                             | When Loaded         | Budget                   |
| ------------------------------------------------ | ------------------- | ------------------------ |
| Metadata (`name` + `description`)                | Startup, all skills | ~100 tokens              |
| Body (SKILL.md content)                          | On activation       | <5000 tokens recommended |
| Resources (`scripts/`, `references/`, `assets/`) | On demand           | No hard limit            |

## Directory Structure

```
skill-name/
├── SKILL.md              # Required - main instructions
├── scripts/              # Optional - executable code (Python, Bash, JS)
│   ├── deploy.sh
│   └── validate.py
├── references/           # Optional - detailed docs loaded on demand
│   ├── REFERENCE.md
│   └── FORMS.md
└── assets/               # Optional - static resources
    ├── template.json
    └── schema.yaml
```

## All Supported Skill Directories

### Cursor

| Location            | Scope                    |
| ------------------- | ------------------------ |
| `~/.cursor/skills/` | User-level (global)      |
| `.cursor/skills/`   | Project-level            |
| `.agents/skills/`   | Project-level (standard) |

### Cross-Platform Compatibility

Cursor also loads from:

- `.claude/skills/`, `~/.claude/skills/`
- `.codex/skills/`, `~/.codex/skills/`

## File Reference Rules

- Use relative paths from the skill root
- Keep references one level deep from SKILL.md
- Avoid deeply nested reference chains
- Make clear whether scripts should be executed or read as reference

## Validation

### Built-in subagent

This skill includes a validation subagent at `agents/validate-skill.md`. Spawn it with the skill path to get a full spec compliance report (frontmatter fields, name rules, line counts, file references, subagent structure).

### External tool

For CI or standalone validation, use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library:

```bash
skills-ref validate ./my-skill
```

## Authoring Principles

### Token Efficiency

Target word counts:
- Frequently-loaded skills: <200 words
- Standard skills: <500 words
- Move details to `references/` — agents load on demand

Techniques:
- Reference `--help` instead of documenting all flags
- Cross-reference other skills instead of repeating their content
- One excellent example beats many mediocre ones
- Compress examples: show pattern, not conversation

### Reference, Don't Duplicate

Before writing new logic, check existing skills. If one overlaps, reference it:

```markdown
**REQUIRED:** Use pr-open for branch creation and PR submission.
```

Declare in frontmatter so dependencies are discoverable:

```yaml
metadata:
  depends-on: "pr-open, code-review"
```

Use `**REQUIRED:** Use skill-name` or `**REQUIRED BACKGROUND:** Use skill-name` — not file paths (which force-load and burn context).

### Common Body Patterns

- **Template**: Output format templates the agent fills in
- **Workflow**: Checklist steps (`- [ ] Step 1: ...`)
- **Conditional**: Decision points (`Creating new?` → workflow A, `Editing?` → workflow B)
- **Feedback loop**: Edit → validate → fix → only proceed when passing

### Degrees of Freedom

| Level | When to Use | Example |
|-------|-------------|---------|
| **High** (text instructions) | Multiple valid approaches | Code review guidelines |
| **Medium** (pseudocode) | Preferred pattern with variation | Report generation |
| **Low** (specific scripts) | Fragile ops, consistency critical | Database migrations |

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Windows-style paths (`scripts\helper.py`) | Use forward slashes (`scripts/helper.py`) |
| Too many options ("use pypdf, or pdfplumber, or...") | Provide one default with escape hatch |
| Time-sensitive info ("before August 2025...") | Use "Current method" / "Deprecated" sections |
| Inconsistent terminology | Pick one term and use it throughout |
| Vague names (`helper`, `utils`) | Specific names (`processing-pdfs`, `deploy-app`) |
| Name doesn't match directory | `name` field must equal parent directory name |

## Cursor-Specific Features

### Migrating Rules to Skills

`/migrate-to-skills` in Agent chat converts:

- Dynamic rules (`alwaysApply: false`, no `globs`) → standard skills
- Slash commands → skills with `disable-model-invocation: true`

Not migrated: rules with `alwaysApply: true` or specific `globs` patterns; user rules.

## Subagents in Skills

### Skill-Level Subagents (`agents/` directory)

Skills can include an `agents/` directory containing markdown prompt files. These are **not** auto-discovered agent definitions — they are prompt templates that the skill's SKILL.md reads and dispatches via the Task tool at runtime.

```
my-skill/
├── SKILL.md          # Orchestrator - reads agent files and spawns them
└── agents/
    ├── step-one.md   # Prompt template for first subagent
    └── step-two.md   # Prompt template for second subagent
```

### Subagent Prompt File Structure

```markdown
# Task Name

You are a subagent responsible for <specific task>.

## Inputs (provided in your task prompt)

- `input_name`: Description
- `another_input`: Description

## Steps

1. First action
2. Second action

## Rules

- Constraints and guardrails

## Output

Return <exact format/structure>.
```

### Key Principles

- **Self-contained**: Subagents have no access to the parent conversation context
- **Typed inputs**: Document all data the SKILL.md will pass
- **Defined output**: Specify exact return format so the parent can use the result
- **Single responsibility**: One task per subagent
- **Error handling**: SKILL.md should include fallback behavior if subagents fail

### Choosing a Model for Subagents

When the SKILL.md instructs the agent to spawn subagents via the Task tool, it should specify which model to use. The right choice depends on the task complexity:

| Model | When to Use | Examples |
|-------|-------------|---------|
| `fast` | Simple, tightly-scoped tasks: gathering data, formatting output, file lookups, validation checks | Collecting git diff stats, formatting a PR body, running a validation checklist |
| Default (inherit) | Tasks requiring judgment, synthesis, or multi-step reasoning | Writing a PR description from context, analyzing code for review, generating a report from raw data |

**Guidelines for SKILL.md authors:**

- **Default to `fast`** for subagents that follow mechanical steps (gather X, format Y, check Z). It's cheaper and lower latency.
- **Use the default model** when the subagent needs to reason about ambiguous input, make judgment calls, or synthesize information from multiple sources.
- **When writing orchestration instructions**, specify the model choice explicitly so the agent doesn't have to guess:

```markdown
### Step 1 — Gather data (parallel, use fast model)

- **gather-metrics** (`agents/gather-metrics.md`): Pass service name and time window.
- **gather-logs** (`agents/gather-logs.md`): Pass service name and time window.

### Step 2 — Write report (sequential, use default model)

Spawn **write-report** (`agents/write-report.md`). This requires synthesis —
use the default model, not fast.
```

- **Validation subagents** (like `validate-skill.md`) are good candidates for `fast` — they follow a checklist with clear pass/fail criteria.
- **If unsure**, start with `fast`. If the subagent's output quality is poor, upgrade to the default model.

### Orchestration in SKILL.md

The SKILL.md instructs the agent to read each prompt file and spawn via the Task tool:

- **Parallel**: Independent subagents spawned simultaneously
- **Sequential**: One subagent's output feeds into the next
- **Fan-out / fan-in**: Parallel gather, then a combining step

### Claude Code Standalone Subagents (different concept)

In Claude Code, subagents can also be defined as standalone `.md` files in `~/.claude/agents/` or `.claude/agents/` with YAML frontmatter. These are auto-discovered and delegated to by Claude based on the `description` field. This is a different mechanism from skill-level `agents/` prompt templates.

Key frontmatter fields for Claude Code standalone subagents:

| Field             | Description                                                      |
| ----------------- | ---------------------------------------------------------------- |
| `name`            | Unique identifier                                                |
| `description`     | When Claude should delegate to this subagent                     |
| `tools`           | Allowlist of tools (inherits all if omitted)                     |
| `disallowedTools` | Tools to deny                                                    |
| `model`           | `sonnet`, `opus`, `haiku`, or `inherit`                          |
| `permissionMode`  | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns`        | Max agentic turns                                                |
| `skills`          | Skills to preload into context                                   |
| `memory`          | Persistent memory scope: `user`, `project`, or `local`           |
| `background`      | `true` to always run in background                               |
| `isolation`       | `worktree` for git worktree isolation                            |

See [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents) for full details.
