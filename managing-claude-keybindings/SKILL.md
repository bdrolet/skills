---
name: managing-claude-keybindings
description: Use when the user asks what keyboard shortcut does a specific thing in Claude Code, wants to look up a default keybinding, asks how to trigger a Claude action by keyboard, wants to configure keybindings in ~/.claude/keybindings.json, or asks about VS Code extension shortcuts for Claude.
---

Claude Code has two layers of keyboard shortcuts:

1. **Terminal/CLI keybindings** — configured in `~/.claude/keybindings.json`, apply in the terminal CLI. See [terminal-keybindings.md](references/terminal-keybindings.md) for all defaults organized by context.
2. **VS Code extension commands** — native VS Code shortcuts for controlling the extension panel. See [vscode-shortcuts.md](references/vscode-shortcuts.md).

## Answering shortcut questions

- If the user is in **VS Code**: check [vscode-shortcuts.md](references/vscode-shortcuts.md) first, then terminal defaults
- If the user is in the **terminal CLI**: check [terminal-keybindings.md](references/terminal-keybindings.md)
- Actions follow `namespace:action` format (e.g. `chat:submit`, `app:toggleTodos`)

## Configuring terminal keybindings

Run `/keybindings` in Claude Code to create/open `~/.claude/keybindings.json`. Changes apply live without restart.

```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    { "context": "Chat", "bindings": { "ctrl+e": "chat:externalEditor" } }
  ]
}
```

Set a binding to `null` to unbind it. Reserved keys that cannot be rebound: `Ctrl+C`, `Ctrl+D`, `Ctrl+M`, `Caps Lock`.

## VS Code-specific settings

| Setting | Default | Description |
|---|---|---|
| `useCtrlEnterToSend` | false | Use Ctrl+Enter instead of Enter to submit |
| `enableNewConversationShortcut` | false | Enable Cmd/Ctrl+N for new conversation |
| `enableReopenClosedSessionShortcut` | true | Cmd/Ctrl+Shift+T reopens last closed session |

Enable in VS Code settings (`Cmd+,` → Extensions → Claude Code) or add to `settings.json` as `"claudeCode.<settingName>": true`.

## Official docs

- Terminal keybindings: https://code.claude.com/docs/en/keybindings
- VS Code extension: https://code.claude.com/docs/en/vs-code
