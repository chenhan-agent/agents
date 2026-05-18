# agents

## Autoresearch loop for `emoji-witty-zh-tw`

This repo includes a minimal autoresearch-style runner that can iterate on the witty emoji skill for multiple loops, benchmark each candidate, and keep or discard changes based on reasoning-gap metrics.

The implementation now follows the skill-local layout:

- `.agents/skills/emoji-witty-zh-tw/SKILL.md`
- `.agents/skills/emoji-witty-zh-tw/scripts/autoresearch.py`
- `.agents/skills/emoji-witty-zh-tw/references/emoji-witty-zh-tw/*.md`

### What it mutates

The runner intentionally limits edits to:

- `.agents/skills/emoji-witty-zh-tw/SKILL.md`
- `.agents/skills/emoji-witty-zh-tw/references/emoji-witty-zh-tw/test-cases.md`
- `.agents/skills/emoji-witty-zh-tw/references/emoji-witty-zh-tw/target-metrics.md`

### What it benchmarks

Each loop runs a fixed generator / solver / judge flow:

1. Generate emoji designs for the selected targets
2. Ask a full-tier solver and a mini-tier solver to explain them
3. Judge both solver outputs against the generator rationale
4. Aggregate a reasoning-gap objective
5. Keep or discard the candidate

### Default backend matrix

The runner now defaults to:

- **generator**: Codex (`reasoning_effort=high`)
- **judge**: Codex (`reasoning_effort=high`)
- **solvers**:
  - Codex full (`reasoning_effort=high`)
  - Copilot full (`gpt-5.4`)
  - Gemini full (CLI default model unless overridden)
  - Copilot mini (`gpt-5.4-mini`)

This keeps generation and judging anchored to Codex, while using a multi-provider solver matrix.

### Run it

```bash
python3 .agents/skills/emoji-witty-zh-tw/scripts/autoresearch.py --iterations 10
```

Useful flags:

- `--baseline-only` — run only the benchmark baseline, without mutation loops
- `--cases osaka,hongkong` — choose the benchmark case pool
- `--output-dir .autoresearch-runs/emoji-witty-zh-tw` — change where artifacts are written
- `--mutation-backend codex:full:mutation::high` — choose the mutation backend
- `--generator-backend codex:full:generator::high` — choose the generator backend
- `--judge-backend codex:full:judge::high` — choose the judge backend
- `--solver-backend provider:tier:label[:model[:reasoning_effort]]` — add or replace solver backends

### Artifacts

Each run writes a timestamped directory under `.autoresearch-runs/emoji-witty-zh-tw/` with:

- `config.json`
- `baseline/`
- `iteration-*/mutation.json`
- `iteration-*/benchmark/`
- `iteration-*/decision.json`
- `run-summary.json`

This is the repo's equivalent of an overnight autoresearch log: each iteration records the mutation hypothesis, benchmark result, and keep/discard decision.

More runner details live in:

- `.agents/skills/emoji-witty-zh-tw/references/emoji-witty-zh-tw/autoresearch.md`