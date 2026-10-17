# agents

Shared agent skills / instructions repo for **Claude Code**, **Codex**, **agy**, and **GitHub Copilot**.

## What this repo is for

- keep one shared skill source in `.agents/skills/`
- keep one canonical instruction source in `AGENTS.md`
- expose tool-specific instruction entry points without duplicating the rules

This repo intentionally keeps the README high level. Browse `.agents/skills/` directly for the actual skills.

## Instruction files in this repo

- **Codex:** `AGENTS.md`
- **Claude Code:** `CLAUDE.md`
- **agy:** `GEMINI.md`
- **Copilot:** `.github/copilot-instructions.md`

`CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` should stay thin wrappers around the canonical rules in `AGENTS.md`.

## Global setup

Use **symlinks**, not copies, so this repo stays the source of truth.

### Global skills

If a tool supports a global skills directory, a symlink is enough:

```bash
ln -s ~/agents/.agents/skills ~/.codex/skills
ln -s ~/agents/.agents/skills ~/.copilot/skills
ln -s ~/agents/.agents/skills ~/.gemini/antigravity-cli/skills
```

In this setup, agy / Antigravity CLI uses `~/.gemini/antigravity-cli/skills` for user-level global skills, so it can point at the same shared `.agents/skills/` directory.

### Global instructions

For instructions, each tool has its own global entry point. Keep `~/agents`
as the canonical source, then expose tool-specific shims with symlinks.

| Tool | Global entry point | Recommended link target | Notes |
|------|--------------------|-------------------------|-------|
| **agy / agy-acp** | `~/AGENTS.md` | `~/agents/AGENTS.md` | Works when `/home/agent` is added as a workspace, which is the normal OpenAB `working_dir=/home/agent` setup. |
| **Codex** | `~/.codex/AGENTS.md` | `~/agents/AGENTS.md` | Codex also merges repo-local and subdirectory `AGENTS.md` files hierarchically. |
| **Claude Code** | `~/.claude/CLAUDE.md` | `~/agents/CLAUDE.md` | Keep `CLAUDE.md` as a thin wrapper around the canonical rules in `AGENTS.md`. |
| **Gemini CLI** | `~/.gemini/GEMINI.md` | `~/agents/GEMINI.md` | Use this when running Gemini directly rather than through `agy-acp`. |
| **GitHub Copilot CLI** | `~/.copilot/copilot-instructions.md` | `~/agents/.github/copilot-instructions.md` | This is Copilot's user-level personal instructions file. |
| **GitHub Copilot CLI** | `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | `~/agents` | Add this so Copilot can also discover the canonical `~/agents/AGENTS.md` and any shared `*.instructions.md` files from this repo. |

Example setup:

```bash
mkdir -p ~/.codex ~/.claude ~/.copilot ~/.gemini

ln -sfn ~/agents/AGENTS.md ~/AGENTS.md
ln -sfn ~/agents/AGENTS.md ~/.codex/AGENTS.md
ln -sfn ~/agents/CLAUDE.md ~/.claude/CLAUDE.md
ln -sfn ~/agents/GEMINI.md ~/.gemini/GEMINI.md
ln -sfn ~/agents/.github/copilot-instructions.md ~/.copilot/copilot-instructions.md
```

For Copilot, also export the extra instructions directory from your shell init:

```bash
export COPILOT_CUSTOM_INSTRUCTIONS_DIRS="$HOME/agents"
```

That keeps one canonical `AGENTS.md` in this repo while still letting each
tool read instructions from the path it expects.

For repo-local usage, keep these files at the repo root:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.github/copilot-instructions.md`
