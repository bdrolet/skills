---
name: migrate-skills
description: Use when the user wants to migrate skills from ~/.cursor/skills/ or a project's .cursor/skills/ to ~/.claude/skills/, consolidate skills into the shared directory accessible by both Claude Code and Cursor, or move cursor-local skills to the global shared location.
disable-model-invocation: true
allowed-tools: Bash
---

Move skills from a `.cursor/skills/` directory into `~/.claude/skills/` so they are accessible by both Claude Code and Cursor.

## Source directory

- If the user says "in this project" or "from the project", use `<project-root>/.cursor/skills/` where `<project-root>` is the current working directory root (find it with `git rev-parse --show-toplevel` or use the known project path).
- Otherwise, default to `~/.cursor/skills/`.

If the user says "make sure you are on main" (or a specific branch), check `git branch --show-current` first and confirm before proceeding.

## Steps

1. **Determine source directory** based on arguments above.

2. **Discover skills to migrate**
   ```bash
   ls <source-dir>
   ```
   Skip hidden dirs (`.git`, `.cursor`) and any entries that are already symlinks.

3. **Check for conflicts**
   For each skill found, check if `~/.claude/skills/<skill-name>` already exists. If it does, skip it and report a warning — do not overwrite.

4. **Move each skill**
   ```bash
   mv <source-dir>/<skill-name> ~/.claude/skills/<skill-name>
   ```

5. **Report results**
   Print a summary:
   - Moved: list of skill names successfully migrated
   - Skipped (already exists): list with note to resolve manually
   - Skipped (symlink): list — these are already pointing elsewhere, leave them

## Notes

- `~/.claude/skills/` is read by both Claude Code and Cursor (Cursor loads it for compatibility).
- Do not create back-symlinks in the source directory — they are not needed.
- If `~/.claude/skills/` does not exist, create it first with `mkdir -p ~/.claude/skills`.
