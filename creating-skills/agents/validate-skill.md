# Validate Skill

You are a subagent responsible for validating a skill against the Agent Skills specification.

## Inputs (provided in your task prompt)

- `skill_path`: Absolute path to the skill directory (e.g., `~/.cursor/skills/my-skill`)

## Steps

### 1. Check directory structure

- Verify `SKILL.md` exists in the skill directory
- Verify the directory name is lowercase alphanumeric + hyphens only

### 2. Parse and validate frontmatter

Read `SKILL.md` and extract the YAML frontmatter (between the opening and closing `---` lines).

**`name` field (required):**
- [ ] Present and non-empty
- [ ] 1-64 characters
- [ ] Only lowercase alphanumeric characters and hyphens (`a-z`, `0-9`, `-`)
- [ ] Does not start or end with a hyphen
- [ ] No consecutive hyphens (`--`)
- [ ] Matches the parent directory name exactly

**`description` field (required):**
- [ ] Present and non-empty
- [ ] 1-1024 characters (under 500 recommended)
- [ ] Written in third person (flag if starts with "I ", "You ", "We ")
- [ ] Starts with or contains "Use when" triggering conditions
- [ ] Does NOT summarize the skill's workflow or process (CSO rule: descriptions that summarize workflow cause agents to shortcut and skip the body)

**Optional fields (validate if present):**
- [ ] `license`: string value
- [ ] `compatibility`: 1-500 characters if present
- [ ] `metadata`: map of string keys to string values
- [ ] `allowed-tools`: string (space-delimited tool names)
- [ ] `disable-model-invocation`: boolean value

### 3. Validate body content

- [ ] SKILL.md total line count is under 500
- [ ] Word count under 500 (WARN if over). Count with `wc -w`.
- [ ] Estimate token count (roughly: word count * 1.3). Flag if likely over 5000 tokens.
- [ ] All file references use relative paths (no absolute paths)
- [ ] File references are one level deep (no `../../` or deeply nested chains)
- [ ] No Windows-style paths (`\` as separator)

### 4. Validate referenced files

For any files referenced in the body (links, script paths):
- [ ] Referenced files actually exist at the specified relative path
- [ ] `scripts/` files exist if referenced
- [ ] `references/` files exist if referenced
- [ ] `agents/` files exist if referenced

### 5. Check for skill dependencies

- [ ] If the body references other skills by name (e.g., "invoke the **pr-open** skill"), verify `metadata.depends-on` lists them in the frontmatter
- [ ] If `metadata.depends-on` is present, verify each listed skill is actually referenced in the body
- [ ] Scan for patterns that suggest duplicated logic from common skills (e.g., lengthy git/PR/commit workflows that an existing skill likely handles). Flag as WARN if the body contains substantial workflow steps that overlap with a named dependency.

### 6. Validate subagent files (if `agents/` directory exists)

For each `.md` file in `agents/`:
- [ ] Has a top-level heading (role/task name)
- [ ] Has an "Inputs" or equivalent section documenting expected data
- [ ] Has an "Output" or equivalent section specifying return format
- [ ] Is self-contained (does not reference parent conversation context)

## Output

Return a validation report in this format:

```
## Validation Report: <skill-name>

### Status: PASS | WARN | FAIL

### Results

| Check | Status | Detail |
|-------|--------|--------|
| ... | PASS/WARN/FAIL | ... |

### Issues (if any)

1. [FAIL] Description of failing check
2. [WARN] Description of warning

### Summary

<one sentence: overall assessment>
```

- **FAIL**: Spec violation that must be fixed (missing required fields, name mismatch, etc.)
- **WARN**: Best-practice deviation (over 400 lines, vague description, missing trigger terms)
- **PASS**: Check passed
