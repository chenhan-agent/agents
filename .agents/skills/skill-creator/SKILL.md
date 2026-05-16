---
name: skill-creator
description: Use when creating, revising, or reviewing an agent skill. Helps design portable skills with clear trigger descriptions, compact SKILL.md files, and the right use of scripts, references, and assets.
---

# Skill Creator

Create skills that are easy for agents to discover, safe to reuse, and small enough to maintain.

## When to use this skill

Use this skill when you need to:

- create a new skill from scratch
- turn a repeated workflow into a reusable skill
- improve an existing `SKILL.md`
- split a bloated skill into instructions plus supporting resources
- review whether a skill description is specific enough to trigger reliably

## Goals

A good skill should:

1. activate only for the right tasks
2. give enough guidance to complete the task correctly
3. stay concise, with details moved into files the skill can reference
4. avoid duplicating repository-wide rules that belong in `AGENTS.md`

## Skill design process

### 1. Identify the job

Define the exact task the skill is for.

Ask:

- What repeated problem does this skill solve?
- What signals should cause an agent to use it?
- What mistakes does the agent make without this skill?
- What outputs should the skill help produce?

If the scope is broad, prefer multiple smaller skills over one general skill.

### 2. Write a precise description

The description is the main trigger for discovery. It should say:

- what the skill does
- when to use it
- what kinds of requests should activate it

Good descriptions are concrete and task-focused.

Bad:

- "Helps with development tasks"
- "General coding workflow"

Better:

- "Use when creating a new agent skill or restructuring an existing SKILL.md into instructions, scripts, references, and assets."

### 3. Keep the main file lean

Put the minimum durable guidance in `SKILL.md`:

- what the skill is for
- when to use it
- the workflow to follow
- critical constraints
- expected outputs

Move bulky detail out of `SKILL.md` when possible:

- shell commands or automation -> `scripts/`
- examples, checklists, specs -> `references/`
- templates or starter files -> `assets/`

## Recommended skill structure

```text
.agents/skills/<skill-name>/
  SKILL.md
  scripts/
  references/
  assets/
```

Only add extra folders if the skill truly needs them.

## Authoring guidelines

### Frontmatter

Every skill should start with metadata.

Minimum:

```yaml
---
name: skill-name
description: Clear trigger-focused description of what the skill does and when to use it.
---
```

Rules:

- use lowercase kebab-case for `name`
- make `description` actionable and specific
- avoid vague words like "helpful", "general", or "miscellaneous"

### Body

The body should be practical, not theoretical.

A strong `SKILL.md` usually includes:

1. purpose
2. when to use it
3. step-by-step workflow
4. constraints and failure modes
5. expected output or done criteria

## Workflow for creating a skill

1. Define the task and activation criteria.
2. Draft the frontmatter and short purpose statement.
3. Write the smallest workflow that reliably guides execution.
4. Add supporting resources only where they reduce complexity.
5. Test the skill against realistic prompts.
6. Tighten wording so the skill triggers for the right requests and avoids unrelated ones.

## Review checklist

Before finishing a skill, check:

- Is the description specific enough that an agent can tell when to use it?
- Does the file describe a repeatable workflow instead of generic advice?
- Is anything in `SKILL.md` better moved into `scripts/`, `references/`, or `assets/`?
- Does the skill duplicate guidance that already belongs in `AGENTS.md`?
- Are the expected outputs or success conditions clear?
- Is the skill narrow enough to stay reliable?

## When to split a skill

Split the skill if:

- it covers multiple unrelated workflows
- the trigger description keeps getting broad or fuzzy
- different tasks need different tools, outputs, or constraints
- the file becomes hard to scan quickly

Prefer a small family of focused skills over one overloaded skill.

## Output expectations

When using this skill to create or revise another skill, produce:

1. the target folder path
2. a complete `SKILL.md`
3. any supporting file recommendations
4. a brief explanation of why the structure fits the task

## Important boundary

Use `AGENTS.md` for always-on repository rules.

Use skills for task-specific expertise that should be activated only when relevant.
