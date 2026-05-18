# `emoji-witty-zh-tw` autoresearch runner

This skill ships with a skill-local autoresearch runner:

- script: `../../scripts/autoresearch.py`
- main instruction file: `../../SKILL.md`

## Layout

The skill now follows the usual skill shape:

```text
emoji-witty-zh-tw/
├── SKILL.md
├── scripts/
│   └── autoresearch.py
└── references/
    └── emoji-witty-zh-tw/
        ├── autoresearch.md
        ├── target-metrics.md
        └── test-cases.md
```

## What the runner mutates

The runner only promotes changes to:

- `SKILL.md`
- `references/emoji-witty-zh-tw/test-cases.md`
- `references/emoji-witty-zh-tw/target-metrics.md`

## Default role matrix

- generator: Codex full, `reasoning_effort=high`
- judge: Codex full, `reasoning_effort=high`
- solvers:
  - Codex full, `reasoning_effort=high`
  - Copilot full, `gpt-5.4`
  - Gemini full
  - Copilot mini, `gpt-5.4-mini`

## Run it

From the repo root:

```bash
python3 .agents/skills/emoji-witty-zh-tw/scripts/autoresearch.py --iterations 10
```

Useful modes:

```bash
python3 .agents/skills/emoji-witty-zh-tw/scripts/autoresearch.py --baseline-only --iterations 0 --cases osaka
python3 .agents/skills/emoji-witty-zh-tw/scripts/autoresearch.py --solver-backend codex:full:codex-full::high
```

## Artifacts

Runs are written under `.autoresearch-runs/emoji-witty-zh-tw/` by default and include:

- baseline benchmark outputs
- per-iteration mutation logs
- per-iteration benchmark results
- keep/discard decisions
- final run summary
