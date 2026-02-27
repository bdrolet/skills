---
name: create-command
description: Create Cursor Command
disable-model-invocation: true
---

# Create Cursor Command

## Overview

Create a new Cursor command from a short description and a target scope (repo or global), then write the command file to the correct `commands` directory.

## Steps

1. **Collect inputs:**
   - Ask for a short command name (kebab-case preferred).
   - Ask for a brief command description (1-3 sentences).
   - Ask for scope: `repo` or `global`.
   - If scope is `repo`, ask for the repo root path (`$repo_dir`) when not already known.

2. **Choose the output path:**
   - `repo`: `$repo_dir/.cursor/commands/<command-name>.md`
   - `global`: `~/.cursor/commands/<command-name>.md`

3. **Create the command file (Markdown):**
   - Use this structure:
     ```
     # <Command Title>

     ## Overview

     <1-2 sentences>

     ## Steps

     1. **Step name**
        - Clear, actionable bullets
        - Avoid ambiguity; include decision points

     ## Requirements (optional)

     - List tools or prerequisites if needed
     ```

4. **Add helpful guidance and tips:**
   - Encourage short, concrete steps.
   - Use checklists for repeatable actions.
   - Include safety notes when running commands or changing files.

5. **Write the file to disk:**
   - Ensure the parent directory exists.
   - Save the file with `.md` extension.

## Tips

- Keep the title and file name aligned (e.g., `# Run Tests` → `run-tests.md`).
- Prefer concise, explicit verbs ("Create", "Validate", "Summarize").
- If the command is complex, add a small checklist near the end.

## Notes

- Commands are plain Markdown files stored in `commands` directories and surface in Cursor when typing `/`.
- Use `repo` scope for project-specific workflows and `global` for reusable commands.
