---
name: creating-skills
description: Use when creating, writing, or authoring a new skill, or when asking about SKILL.md structure, frontmatter format, or skill best practices
metadata:
  depends-on: "writing-skills"
---

# Creating Skills

Skills are markdown packages that teach agents domain-specific tasks, following the [Agent Skills open standard](https://agentskills.io/specification).

## Quick Reference

| Element | Rule |
|---------|------|
| Name | Lowercase + hyphens, max 64 chars, gerund preferred (`creating-skills` not `skill-creation`), must match directory name |
| Description | "Use when..." only — triggering conditions, **never** summarize workflow. Third person. Max 1024 chars |
| Body | <500 words target. Only include what the agent doesn't already know |
| Structure | `SKILL.md` (required), optional `agents/`, `scripts/`, `references/`, `assets/` |
| Storage | `~/.cursor/skills/` (global), `.cursor/skills/` or `.agents/skills/` (project). Never `~/.cursor/skills-cursor/` |
| Dependencies | Reference existing skills by name, don't duplicate. Declare in `metadata.depends-on` |
| Subagents | Default to subagents for any bounded step whose intermediate context the parent doesn't need — bash output, log reads, reviews, data fetches. Inline only when the parent needs the full output to proceed. Put prompts in `agents/`. `fast` for gather/format; default for reasoning |

See [specification reference](references/specification.md) for all frontmatter fields and validation rules.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Description summarizes workflow | Claude shortcuts the description and skips the body. Use only "Use when..." triggers |
| Duplicating another skill's logic | Reference it: `**REQUIRED:** Use skill-name`. Declare in `metadata.depends-on` |
| Body too verbose | Target <500 words. Move details to `references/`. Agent is smart — only add what it doesn't know |
| Name doesn't match directory | `name` field must exactly equal parent directory name |
| Vague name (`helper`, `utils`) | Use specific gerunds: `processing-pdfs`, `deploying-apps` |
| Subagent assumes parent context | Subagents are isolated. Document all inputs explicitly |
| Inline steps that say "run in parallel" | That's a subagent. Move the steps to `agents/` — describing parallelism in prose means you need an agents/ file |

## Workflow

### Phase 1: Discovery

Gather from user (or infer from conversation context):
- Purpose, trigger scenarios, storage location
- Invocation mode: automatic (default) or manual-only (`disable-model-invocation: true`)
- Check for **existing skills** that overlap — reference, don't duplicate

### Phase 2: Design

1. Name: lowercase gerund + hyphens, matches directory
2. Description: "Use when..." with specific triggers/symptoms — no workflow summary
3. Plan body sections. Target <500 words
4. Identify dependencies on other skills
5. **Default to subagents** for any bounded step whose intermediate context the parent won't need — bash commands, log reads, text review, data fetches. The subagent absorbs the noise and returns only what matters. Common patterns: parallel fan-out, verbose output isolation, model switching. See [subagent patterns](references/specification.md#named-subagent-patterns). Inline only when the parent needs the full output to proceed.

### Phase 3: Implementation

1. Create `skill-name/SKILL.md` with frontmatter
2. Add `metadata.depends-on` if referencing other skills
3. Write body — invoke dependencies by name, don't copy logic
4. Create `references/`, `scripts/`, `assets/` as needed
5. If using subagents: create `agents/` with prompt files. Each must have Inputs, Steps, Output sections. Add orchestration instructions to SKILL.md with fallback behavior.

### Phase 4: Verification

Spawn the **validate-skill** subagent (`agents/validate-skill.md`). Read the agent file first, then pass it the absolute path to the new skill directory. Fix any **FAIL** items. Address **WARN** items if practical.

## Resources

- [Specification reference](references/specification.md) — frontmatter fields, validation rules, anti-patterns, subagent details
- [Complete examples](references/examples.md) — simple skill and skill-with-subagents
- For eval loops, benchmarking, and description optimization, see skill-creator
