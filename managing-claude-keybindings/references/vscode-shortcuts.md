# Claude Code VS Code Extension Shortcuts

Source: https://code.claude.com/docs/en/vs-code

## VS Code commands and keyboard shortcuts

| Command | Shortcut (Mac) | Shortcut (Win/Linux) | Description |
|---|---|---|---|
| Focus Input | `Cmd+Esc` | `Ctrl+Esc` | Toggle focus between editor and Claude panel |
| Open in New Tab | `Cmd+Shift+Esc` | `Ctrl+Shift+Esc` | Open a new conversation as an editor tab |
| New Conversation | `Cmd+N` | `Ctrl+N` | Start a new conversation (requires `enableNewConversationShortcut: true`) |
| Reopen Closed Session | `Cmd+Shift+T` | `Ctrl+Shift+T` | Reopen most recently closed Claude session tab |
| Insert @-Mention Reference | `Option+K` | `Alt+K` | Insert file path + line ref for current selection (editor must be focused) |
| Open Extensions view | `Cmd+Shift+X` | `Ctrl+Shift+X` | Open VS Code Extensions (to install Claude Code) |
| Open Command Palette | `Cmd+Shift+P` | `Ctrl+Shift+P` | Access all Claude Code commands via "Claude Code" search |
| Open Settings | `Cmd+,` | `Ctrl+,` | Open VS Code settings (go to Extensions → Claude Code) |
| Open Keyboard Shortcuts editor | `Cmd+K Cmd+S` | `Ctrl+K Ctrl+S` | Rebind VS Code commands including Claude Code ones |
| Open integrated terminal | `` Cmd+` `` | `` Ctrl+` `` | Open terminal to run Claude CLI |

## Multi-line input in prompt box

- `Shift+Enter` — insert newline without submitting

## Optional settings that unlock shortcuts

These shortcuts are disabled by default and must be enabled in VS Code settings (`Cmd+,` → Extensions → Claude Code or in `settings.json`):

| Setting | Value | Unlocks |
|---|---|---|
| `claudeCode.enableNewConversationShortcut` | `true` | `Cmd/Ctrl+N` for new conversation (Claude must be focused) |
| `claudeCode.enableReopenClosedSessionShortcut` | `false` to disable | `Cmd/Ctrl+Shift+T` (enabled by default) |
| `claudeCode.useCtrlEnterToSend` | `true` | Submit with `Ctrl+Enter` instead of `Enter` |

## macOS Tahoe note

On macOS Tahoe and later, `Cmd+Esc` is intercepted by the system Game Overlay shortcut. Fix:
1. System Settings → Keyboard → Keyboard Shortcuts → Game Controllers → uncheck Game Overlay
2. Or rebind in VS Code: `Cmd+K Cmd+S` → search "Claude Code: Focus input" → assign new key
