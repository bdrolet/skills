---
name: mv-tmp
description: Review Files Created in Chat
disable-model-invocation: true
---

# Review Files Created in Chat

## Overview

Review files that have been created or modified during the current chat session. Identify which files should be tracked in git and which should be moved to a temporary directory (e.g., user-only documentation, debug scripts, logs).

## Steps

1. **Review chat history from the beginning:**
   - Start from the first message in the conversation
   - Identify all files that were created or written during this chat session
   - Note the context and purpose of each file creation

2. **Check git status:**
   - Run `git status` to see current working directory state
   - Only consider files that appear in `git status` output (untracked, modified, or deleted)
   - Ignore files that are already committed or ignored by `.gitignore`

3. **Categorize each file:**
   - For each file identified in step 1 that also appears in `git status`:
     - Determine if the file is intended to be tracked in git
     - Determine if the file is intended to be in the current working directory
     - Consider the file's purpose:
       - **Should be tracked**: Terraform files, configuration files, code files, etc.
       - **Should NOT be tracked**: 
         - `*.md` files that are user-only documentation or notes (not project documentation)
         - Debug scripts for investigation (e.g., `debug.sh`, `investigate.py`)
         - Log files (e.g., `*.log`, `debug.log`)
         - Temporary files (e.g., `*.tmp`, `*.bak`)
         - Test files created for investigation purposes
         - Any file explicitly created for temporary use or user reference only

4. **Move non-tracked files to TEMPDIR:**
   - For files that should NOT be checked in:
     - Create TEMPDIR if it doesn't exist: `mkdir -p "$TMPDIR"` or use `/tmp` if `$TMPDIR` is not set
     - Move the file to TEMPDIR: `mv <file> "$TMPDIR"` or `mv <file> /tmp`
     - Inform the user which files were moved and where they were moved to
     - If a file path contains directories, preserve the directory structure or flatten it appropriately

5. **Report findings:**
   - List all files reviewed
   - Indicate which files should remain in the working directory (for git tracking)
   - Indicate which files were moved to TEMPDIR and why
   - If any files are ambiguous, ask the user for clarification

## Requirements

- `git` installed and configured
- Must be in a git repository
- Write access to current working directory and TEMPDIR

## Notes

- Only review files that were created/modified in the current chat session
- Only act on files that appear in `git status` output
- When in doubt about whether a file should be tracked, ask the user
- Preserve file permissions when moving files
- If moving a file would overwrite an existing file in TEMPDIR, append a timestamp or ask the user
