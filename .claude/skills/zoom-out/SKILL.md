---
name: zoom-out
description: Forces stepping back to reconsider the full problem when stuck or going in the wrong direction. Use when the agent is looping, over-engineering, or losing sight of the original goal.
license: MIT
compatibility: Claude Code
argument-hint: "[what you're stuck on]"
metadata:
  author: mattpocock (concept), adapted for this repo
  source: https://github.com/mattpocock/skills
---

Stop. Step back. Reconsider the whole problem before continuing.

This skill is for when the current approach has become the problem — the agent is deep in a solution that isn't working, has drifted from the original goal, or is adding complexity to fix complexity.

---

## Step 1 — Pause and state the original goal

Before anything else, state in one sentence what the user originally asked for. Not what you've been building — what they actually wanted.

If you can't state it clearly in one sentence, that's the problem.

---

## Step 2 — Describe what you've been doing

In 2–3 sentences, describe the current approach:
- What have you built or changed so far?
- What assumption is the current approach built on?
- What is the obstacle that triggered this skill?

---

## Step 3 — Challenge the assumption

Ask: **"Is the current approach the right one, or did we take a wrong turn somewhere?"**

Look for:
- A simpler path that was overlooked at the start
- A library or built-in that already does this
- A misunderstanding of what the user actually needed
- A constraint that no longer applies

If the approach is fundamentally wrong, say so explicitly before proposing an alternative.

---

## Step 4 — Propose a reset or a pivot

Present **one** of these outcomes:

**A) Reset**: The current approach is a dead end. Discard it. Here is the simpler path:
- Describe the alternative in concrete terms (what file changes, what different approach)
- Estimate why it's simpler or more correct
- Ask the user to confirm before proceeding

**B) Pivot**: The approach is right but a specific part is wrong. Here is the correction:
- Name the specific part that needs to change
- Describe the fix
- Continue from there

**C) Continue**: After zooming out, the current approach is actually correct. Here is why:
- Explain the reasoning
- Identify the actual blocker and address it directly

---

## Guardrails

- Do not propose two alternatives and ask the user to choose — pick the better one and recommend it
- Do not zoom out indefinitely; one reset per invocation
- If the user says "just continue", respect it and continue — do not loop back to this skill
