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
ln -s /path/to/agents/.agents/skills ~/.codex/skills
ln -s /path/to/agents/.agents/skills ~/.copilot/skills
```

If your Claude Code or agy setup also supports a user-level skills path, point it at the same `.agents/skills/` directory.

### Global instructions

Copilot supports a user-level instructions file, so this can also be a symlink:

```bash
ln -s /path/to/agents/AGENTS.md ~/.copilot/copilot-instructions.md
```

For repo-local usage, keep these files at the repo root:

- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `.github/copilot-instructions.md`
