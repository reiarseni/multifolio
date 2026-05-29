---
name: software-architecture
description: Designs correct architecture for new features or systems applying SOLID principles, proven patterns, and explicit tradeoff analysis before writing any code.
license: MIT
compatibility: Claude Code
argument-hint: "[what you need to design]"
metadata:
  author: NeoLabHQ (concept), adapted for this repo
  source: https://github.com/ComposioHQ/awesome-claude-skills
---

Architecture is the set of decisions that are hardest to change later. Make them deliberately.

This skill runs before implementation — not during. It produces a concrete design decision record, not a wall of theory.

---

## Step 1 — Understand the problem

Before designing anything, answer these questions from what the user described and what you find in the codebase:

1. **What behavior is being added?** (user-observable, not internal)
2. **What changes often in this domain?** (the architecture must absorb those changes cheaply)
3. **What must never break?** (the invariants the design must protect)
4. **What already exists?** Scan the codebase for related modules, patterns in use, naming conventions

Do not design yet. Accumulate answers.

---

## Step 2 — Identify the key architectural decisions

From Step 1, extract 2–4 decisions that will have the most impact on the design. Each decision must have at least two real options.

For each decision, present:
- **Decision**: what needs to be chosen
- **Option A**: name + tradeoff
- **Option B**: name + tradeoff
- **Recommendation**: which one and why (cite a specific reason from Step 1, not a generic principle)

Use **AskUserQuestion** for decisions where the user's context matters more than abstract principles (data ownership, team conventions, deployment constraints). Decide yourself for pure engineering choices.

---

## Step 3 — Apply relevant principles

For the chosen options, apply whichever principles are relevant. Do not apply all of them to everything:

- **Single Responsibility**: if a module does two things that change for different reasons, split it
- **Open/Closed**: if callers will need to extend behavior, use an interface or strategy — if they won't, don't add the abstraction
- **Dependency Inversion**: if a high-level module depends on an implementation detail that will change, invert the dependency
- **Composition over inheritance**: prefer passing behavior as functions/objects rather than overriding via subclasses
- **Ports and Adapters**: if an external dependency (DB, API, queue) crosses a domain boundary, put the interface at the boundary

State which principles apply and why. State which ones don't apply, so the design isn't over-engineered.

---

## Step 4 — Produce the architecture record

Write a compact design record:

```
## Architecture: <feature name>

### Context
<one paragraph: what problem, what constraints, what already exists>

### Decisions

**<Decision 1>**: chose <option> because <specific reason>
**<Decision 2>**: chose <option> because <specific reason>

### Structure

<module or file breakdown — names, responsibilities, interfaces>
<data flow: how data moves between components>
<key invariants: what must always be true>

### What this design makes easy
- <change type 1>
- <change type 2>

### What this design makes hard (accepted tradeoff)
- <limitation 1>
```

---

## Step 5 — Hand off to implementation

Once the user confirms the design record, produce:
- A list of files to create or modify (in implementation order)
- For each file: the interface it exposes (not the implementation)
- Any migration or backward-compatibility concern

Do not implement. Implementation is a separate task.

---

## Guardrails

- Never produce an architecture that requires rewriting more than 20% of existing code unless the user explicitly asks for it
- If a simpler design achieves the same goals, choose it — complexity is a cost, not a feature
- The architecture record is the output; never skip it even if the design seems obvious
- Patterns (Repository, Factory, Observer, etc.) are means, not ends — only use them if they solve a specific problem identified in Step 1
