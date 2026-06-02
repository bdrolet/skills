---
name: setting-up-zshrc
description: Use when the user wants to set up or repair their zsh configuration, link ~/.zshrc to the scripts repo, run the zsh setup script, or check whether the managed zsh config is active.
compatibility: macOS, requires ~/src/scripts repo
---

# Setting Up ~/.zshrc

The managed zsh config lives in `~/src/scripts/zsh/`. The `~/.zshrc` should only contain a single `source` line pointing to `~/src/scripts/zsh/config/.zshrc`.

## File layout

| File | Purpose |
|---|---|
| `zsh/config/.zshrc` | Main entry point — loads Oh My Zsh, p10k, and sources the files below |
| `zsh/config/.exports` | PATH, env vars, tool inits (nodenv, etc.) |
| `zsh/config/.aliases` | Shell aliases |
| `zsh/config/.functions` | Shell functions |
| `zsh/config/.secrets` | Secrets (gitignored) |

## How to set up

Run the setup script:

```bash
bash ~/src/scripts/zsh/setup.sh
```

It backs up the existing `~/.zshrc` (if not already linked) and replaces it with:

```zsh
source ~/src/scripts/zsh/config/.zshrc
```

Then apply with `source ~/.zshrc` or open a new terminal.

## Verification

Check the link is active:

```bash
grep "scripts/zsh/config/.zshrc" ~/.zshrc
```

Check sourced config files are loading:

```bash
source ~/.zshrc && alias | head -5
```

## Notes

- `setup.sh` and `setup-zsh-config.sh` are identical — prefer `setup.sh`
- `setup-powerlevel10k.sh` installs Oh My Zsh + p10k + MesloLGS NF fonts; run it first on a new machine
- Add PATH entries and env vars to `.exports`, not directly to `.zshrc`
- `.secrets` is gitignored; recreate it manually on new machines
