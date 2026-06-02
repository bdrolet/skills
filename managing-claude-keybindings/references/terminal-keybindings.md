# Claude Code Terminal Keybindings — Defaults

Source: https://code.claude.com/docs/en/keybindings

## Global (app) context

| Action | Default | Description |
|---|---|---|
| `app:interrupt` | Ctrl+C | Cancel current operation |
| `app:exit` | Ctrl+D | Exit Claude Code |
| `app:redraw` | (unbound) | Force terminal redraw |
| `app:toggleTodos` | Ctrl+T | Toggle task list visibility |
| `app:toggleTranscript` | Ctrl+O | Toggle verbose transcript |

## History context

| Action | Default | Description |
|---|---|---|
| `history:search` | Ctrl+R | Open history search |
| `history:previous` | Up | Previous history item |
| `history:next` | Down | Next history item |

## Chat context

| Action | Default | Description |
|---|---|---|
| `chat:submit` | Enter | Submit message |
| `chat:newline` | Ctrl+J | Insert newline without submitting |
| `chat:cancel` | Escape | Cancel current input |
| `chat:clearInput` | Ctrl+L | Force full screen redraw (preserves input) |
| `chat:clearScreen` | Cmd+K | Clear screen |
| `chat:undo` | Ctrl+\_, Ctrl+Shift+- | Undo last action |
| `chat:externalEditor` | Ctrl+G, Ctrl+X Ctrl+E | Open in external editor |
| `chat:stash` | Ctrl+S | Stash current prompt |
| `chat:imagePaste` | Ctrl+V (Alt+V on Windows) | Paste image |
| `chat:cycleMode` | Shift+Tab | Cycle permission modes |
| `chat:modelPicker` | Meta+P | Open model picker |
| `chat:fastMode` | Meta+O | Toggle fast mode |
| `chat:thinkingToggle` | Meta+T | Toggle extended thinking |
| `chat:killAgents` | Ctrl+X Ctrl+K | Kill all running background subagents |

## Autocomplete context

| Action | Default | Description |
|---|---|---|
| `autocomplete:accept` | Tab | Accept suggestion |
| `autocomplete:dismiss` | Escape | Dismiss menu |
| `autocomplete:previous` | Up | Previous suggestion |
| `autocomplete:next` | Down | Next suggestion |

## Confirmation context

| Action | Default | Description |
|---|---|---|
| `confirm:yes` | Y, Enter | Confirm action |
| `confirm:no` | N, Escape | Decline action |
| `confirm:previous` | Up | Previous option |
| `confirm:next` | Down | Next option |
| `confirm:nextField` | Tab | Next field |
| `confirm:toggle` | Space | Toggle selection |
| `confirm:cycleMode` | Shift+Tab | Cycle permission modes |
| `confirm:toggleExplanation` | Ctrl+E | Toggle permission explanation |

## Transcript context

| Action | Default | Description |
|---|---|---|
| `transcript:toggleShowAll` | Ctrl+E | Toggle show all content |
| `transcript:exit` | q, Ctrl+C, Escape | Exit transcript view |

## History search context

| Action | Default | Description |
|---|---|---|
| `historySearch:next` | Ctrl+R | Next match |
| `historySearch:accept` | Escape, Tab | Accept selection |
| `historySearch:cancel` | Ctrl+C | Cancel search |
| `historySearch:execute` | Enter | Execute selected command |
| `historySearch:cycleScope` | Ctrl+S | Cycle scope: session, project, everywhere |

## Task context

| Action | Default | Description |
|---|---|---|
| `task:background` | Ctrl+B | Background current task |

## Scroll context (fullscreen mode only)

| Action | Default | Description |
|---|---|---|
| `scroll:pageUp` | PageUp | Scroll up half viewport |
| `scroll:pageDown` | PageDown | Scroll down half viewport |
| `scroll:top` | Ctrl+Home | Jump to start of conversation |
| `scroll:bottom` | Ctrl+End | Jump to latest message |
| `selection:copy` | Ctrl+Shift+C / Cmd+C | Copy selected text |
| `selection:extendLeft` | Shift+Left | Extend selection left |
| `selection:extendRight` | Shift+Right | Extend selection right |
| `selection:extendUp` | Shift+Up | Extend selection up |
| `selection:extendDown` | Shift+Down | Extend selection down |

## Select context

| Action | Default | Description |
|---|---|---|
| `select:next` | Down, J, Ctrl+N | Next option |
| `select:previous` | Up, K, Ctrl+P | Previous option |
| `select:accept` | Enter | Accept selection |
| `select:cancel` | Escape | Cancel selection |

## Tabs context

| Action | Default | Description |
|---|---|---|
| `tabs:next` | Tab, Right | Next tab |
| `tabs:previous` | Shift+Tab, Left | Previous tab |

## Voice context (when voice dictation enabled)

| Action | Default | Description |
|---|---|---|
| `voice:pushToTalk` | Space | Dictate a prompt |

## Reserved shortcuts (cannot be rebound)

| Shortcut | Reason |
|---|---|
| Ctrl+C | Hardcoded interrupt/cancel |
| Ctrl+D | Hardcoded exit |
| Ctrl+M | Identical to Enter in terminals |
| Caps Lock | Not delivered to terminal applications |

## Terminal multiplexer conflicts

| Shortcut | Conflict |
|---|---|
| Ctrl+B | tmux prefix (press twice to send) |
| Ctrl+A | GNU screen prefix |
| Ctrl+Z | Unix process suspend (SIGTSTP) |
