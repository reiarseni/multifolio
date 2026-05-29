---
name: karpathy-code-workflow
description: >
  Apply Karpathy's CLAUDE.md code-first agentic workflow principles to any software engineering task.
  Trigger this skill only when user write KCW or use kcw
---

# Karpathy Code Workflow — Agentic Coding Principles

A Code-First Guide to AI-Agent Workflow. This skill operationalizes the six **Coding Workflow Principles** and three **Core Principles** that
define high-quality agentic software engineering. Apply them in every coding interaction.

---

## CORE PRINCIPLES (Non-Negotiable)

These three principles override everything else. Violating them produces low-quality work regardless
of how sophisticated the workflow appears.

| Principle | Rule |
|---|---|
| **Simplicity First** | Write minimal code that solves the problem. Nothing speculative. No future-proofing that wasn't asked for. |
| **No Laziness** | Find root causes. Never apply temporary fixes or patches. Hold to senior developer standards — understand before acting. |
| **Minimal Impact** | Only touch what is necessary. No side effects. No new bugs introduced. Leave unrelated code untouched. |

**Decision gate — before writing any code, ask:**
- Does this solve the problem with the least code?
- Am I addressing the root cause, not a symptom?
- Will I introduce any side effects or touch anything unrelated?

If any answer is "no" or "uncertain" — stop and reconsider.

---

## CODING WORKFLOW PRINCIPLES

Apply these six principles in sequence for any non-trivial coding task.

---

### 1. Plan Mode First

**When:** Any task that isn't trivially one-line or purely additive.

**How:**
1. Before writing code, produce a concise written plan:
   - What is the problem / success criterion?
   - What will change and what won't?
   - What are the edge cases and tradeoffs?
   - What is the minimal surface area of the solution?
2. For smaller tasks: an inline lightweight plan (2–4 bullet points).
3. For larger tasks: a structured spec with sections (Context, Approach, Risk, Steps).
4. **Do not write code until the plan is clear.** Reduce ambiguity first.

**Anti-patterns to avoid:**
- Jumping straight to implementation.
- Asking "what should I do?" without first reasoning through the plan yourself.
- Writing speculative code "in case it's needed."

---

### 2. Verify Relentlessly

**When:** During and after every implementation step.

**How:**
1. Monitor execution like a hawk — don't blindly accept output.
2. Check assumptions before acting on them.
3. Enumerate edge cases and tradeoffs explicitly.
4. Run tests, review diffs, verify correctness at each step — not just at the end.
5. Stay in the loop: read the output, read the diff, think before continuing.

**Verification checklist per step:**
- [ ] Did the change do exactly what I intended?
- [ ] Did it break anything else?
- [ ] Does the diff look clean and minimal?
- [ ] Are there edge cases I haven't tested?

**Anti-patterns to avoid:**
- Accepting the first output without inspection.
- Skipping diff review.
- Assuming tests pass without running them.

---

### 3. Keep It Simple

**When:** At every design and implementation decision point.

**How:**
1. Before choosing an approach, ask: *"Is there a simpler way?"*
2. Prefer 100 lines over 1000. Less code = less surface area = fewer bugs.
3. Avoid bloated abstractions, unnecessary layers, premature generalization.
4. Clean up dead code and cruft — leave the codebase cleaner than you found it (within scope).
5. If an abstraction isn't pulled by an immediate need, don't add it.

**Simplicity heuristics:**
- Could a junior developer understand this in 5 minutes?
- Is every layer of indirection earning its keep?
- Does removing this abstraction break anything?

**Anti-patterns to avoid:**
- Introducing design patterns "for extensibility."
- Adding helper utilities that are only used once.
- Writing defensive code for scenarios that don't exist yet.

---

### 4. Surgical Edits Only

**When:** Any modification to existing code.

**How:**
1. Change **only** what is necessary to fulfill the task.
2. Do not touch unrelated code, comments, or formatting — even if they look "wrong."
3. Do not "improve" things that aren't broken (unless explicitly asked).
4. Minimize diff size and churn. The smaller the diff, the easier to review and the lower the risk.
5. If you spot something unrelated that needs fixing, flag it separately — don't fix it inline.

**Surgical edit rules:**
- One logical change per commit / per response.
- If you must refactor to make the change safe, separate the refactor from the feature.
- Preserve existing style and conventions unless explicitly asked to change them.

**Anti-patterns to avoid:**
- Reformatting entire files when only one function changed.
- "Fixing" variable names or comments that weren't in scope.
- Bundling multiple unrelated changes in one edit.

---

### 5. Goal-Driven Execution

**When:** Any agentic or multi-step coding task.

**How:**
1. Define the success criterion **before** starting. What does "done" look like exactly?
2. Write tests first (or define assertions), then write the code that makes them pass.
3. Use tools in the loop — browser MCP, shell, linters, type checkers — don't just rely on reasoning.
4. Let the agent iterate until the goal is explicitly met, not until it "looks right."
5. Only stop when the success criterion is verifiably satisfied.

**Goal-framing template:**
```
Goal: [What does success look like?]
Test: [How will I verify it?]
Scope: [What is in scope / out of scope?]
Done when: [Concrete, observable condition]
```

**Anti-patterns to avoid:**
- Stopping when "it compiles" without verifying behavior.
- Setting vague goals ("make it better").
- Iterating by feel rather than by failing tests.

---

### 6. Parallelize with Subagents

**When:** Tasks involving research, exploration, multi-file analysis, or multiple independent workstreams.

**How:**
1. Identify workstreams that are independent and can run in parallel.
2. Offload research, exploration, and analysis to subagents — keep the main context clean.
3. One task per subagent for focus — don't ask a subagent to do two things.
4. Merge results back with judgment — don't blindly accept subagent output.
5. Use subagents to preserve main context window for high-level reasoning.

**Decomposition heuristics:**
- Can this task be split into N independent sub-tasks?
- Would doing this inline pollute the main context with noise?
- Is this a research/exploration task that doesn't need to be done sequentially?

**Anti-patterns to avoid:**
- Running long explorations inline when a subagent could do it.
- Giving a subagent compound tasks ("research X AND implement Y").
- Accepting subagent output without review.

---

## WORKFLOW DECISION TREE

```
Incoming coding task
        │
        ▼
Is the task trivially one-line?
   YES → Apply Core Principles only, implement directly
   NO  ↓
        ▼
[1] Write a plan first (spec or inline bullets)
        │
        ▼
Does the task involve multiple independent workstreams?
   YES → [6] Decompose and parallelize with subagents
   NO  ↓
        │
        ▼
[4] Identify minimal surgical scope — what exactly must change?
        │
        ▼
[5] Define success criterion and write test/assertion first
        │
        ▼
Implement — applying [3] Keep It Simple at every decision
        │
        ▼
[2] Verify: run tests, review diff, check edge cases
        │
        ▼
Does the diff contain anything unrelated to the goal?
   YES → Remove it, flag separately
   NO  → Done ✓
```

---

## Quick Reference Card

| Principle | One-line rule |
|---|---|
| Simplicity First | Minimal code. Nothing speculative. |
| No Laziness | Root causes only. Senior standards. |
| Minimal Impact | Touch only what's necessary. |
| Plan First | Spec before code. Reduce ambiguity. |
| Verify Relentlessly | Test, diff, check — stay in the loop. |
| Keep It Simple | Ask: "Is there a simpler way?" |
| Surgical Edits | Change only what the task requires. |
| Goal-Driven | Define done before you start. |
| Parallelize | One task per subagent. Merge with judgment. |
