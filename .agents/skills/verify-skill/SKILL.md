---
name: verify-skill
description: Use when validating whether a repository skill is correctly discovered and followed by Copilot, Gemini, and Codex. Runs headless cross-agent checks with fixed model tiers and compares discovery, recall, and behavior against expected outputs.
---

# Verify Skill

Verify that a skill is loaded, recalled, and actually followed across Copilot, Gemini, and Codex.

## When to use this skill

Use this skill when you need to:

- validate a newly created or revised skill
- compare behavior across Copilot, Gemini, and Codex
- check whether a skill is only visible or truly being applied
- evaluate success at both full and mini model tiers
- produce evidence before merging a skill change

## Goals

A good verification run should:

1. test all three agents from the same repository working directory
2. use headless mode instead of interactive sessions
3. keep prompts identical across agents whenever possible
4. check discovery, recall, and behavior rather than only asking what was loaded
5. separate model-tier differences from skill-design problems

## Fixed model tiers

Use these model targets unless the user explicitly requests a different matrix.

### Full tier

- Copilot -> `gpt-5.4`
- Codex -> `gpt-5.4`
- Gemini -> `gemini-3.1-pro`

### Mini tier

- Copilot -> `gpt-5.4-mini`
- Codex -> `gpt-5.4-mini`
- Gemini -> `gemini-3.1-flash`

If a CLI rejects a model name, report the exact mismatch instead of silently switching.

## Execution mode

Prefer headless commands:

- Copilot -> `copilot --allow-all-tools --model <model> -p "<prompt>"`
- Gemini -> `gemini --skip-trust --model <model> -p "<prompt>"`
- Codex -> `codex exec -m <model> "<prompt>"`

Run from the repository root or the intended working directory for the skill under test.

## Verification process

### 1. Identify the target

Collect:

- target skill name
- target skill path
- current repository path
- current commit SHA if available

Read the target `SKILL.md` before testing.

### 2. Extract unique markers

Find details that are specific enough to prove the skill was actually read:

- unique checklists
- special output requirements
- exact boundaries or constraints
- distinctive phrases or rules

Do not rely only on generic statements that a built-in skill could also produce.

### 3. Build the test set

Use at least these three test types.

#### Discovery test

Ask which instruction files and skills are active for the repository.

Purpose:

- confirm whether the agent can name the target skill
- gather path evidence when available

#### Recall test

Ask for facts that only the target skill should know.

Purpose:

- verify that the agent loaded the target skill contents

#### Behavior test

Ask the agent to perform a small task using the target skill.

Purpose:

- confirm the skill changes behavior, not just recall

### 4. Keep prompts aligned

Use the same wording across agents unless a CLI requires a small syntax change.

If you must diverge, keep the semantic request identical and note the difference.

### 5. Run the matrix

Run all three agents for:

1. full tier
2. mini tier

If time or cost matters, start with full tier and expand only when needed.

## Evaluation rules

Classify each result as one of:

- **loaded** -> direct evidence that the target skill was read and used
- **likely loaded** -> strong behavioral match without explicit path evidence
- **not proven** -> some overlap, but generic or ambiguous
- **failed** -> output conflicts with the target skill or ignores it

Treat these as stronger evidence, in order:

1. explicit path to the target `SKILL.md`
2. correct recall of unique markers
3. behavior that follows the target output contract
4. generic claims that a skill is active

## Failure analysis

When verification is weak or fails, check:

- description too vague for discovery
- skill overlaps with a built-in skill
- target rules are too generic
- output contract is missing or weak
- prompts are too broad
- model tier is too weak for the skill complexity
- CLI did not accept the intended model

## Output expectations

When using this skill, produce:

1. the target skill path and model matrix used
2. the exact prompts used for discovery, recall, and behavior
3. per-agent results for Copilot, Gemini, and Codex at the tested tier or tiers
4. quoted evidence that supports each verdict
5. a final verdict for each agent: loaded, likely loaded, not proven, or failed
6. recommended changes if the verification is weak

## Important boundary

This skill verifies whether another skill is discoverable and behaviorally effective.

It does not replace the target skill, rewrite repository policy, or assume that an agent naming a skill is enough proof by itself.
