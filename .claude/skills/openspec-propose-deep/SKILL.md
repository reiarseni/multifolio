---
name: openspec-propose-deep
description: Propose a new change with deep pre-proposal research and exhaustive interactive clarification. Use when the user wants a well-grounded proposal with all key decisions validated before writing a single artifact.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
---

Propose a new change — but only after deeply understanding what should actually be built.

This skill follows the same artifact pipeline as `openspec-propose`, but inserts a **mandatory deep-clarification phase** before any artifact is created. The user drives all key decisions; the AI drives the research and surfaces the right questions.

Artifacts produced (same as openspec-propose):
- proposal.md (what & why)
- design.md (how)
- tasks.md (implementation steps)

When ready to implement, run `/opsx:apply`

---

## Phase 0 — Initial capture

**If no input was provided with the invocation**, ask what the user wants to build using **AskUserQuestion** (open-ended, no preset options):

> "What change do you want to work on? Describe what you want to build or fix."

Keep this question minimal — you need just enough to know the topic. Do NOT ask anything else yet. The deeper questions come later.

From the description, derive a kebab-case change name (e.g., "add offline export" → `add-offline-export`). Hold it for step 4 — don't create the directory yet.

---

## Phase 1 — Codebase reconnaissance

Before talking to the user further, ground yourself in reality. Run in parallel:

```bash
openspec list --json
```

Read whichever existing artifacts are relevant to the proposed change (proposals, designs). Also scan the parts of the codebase most likely to be touched (routers, models, workers, frontend pages). Use `grep` and `find` freely.

Goal: build a mental map of:
- What already exists that overlaps with the request
- Patterns and conventions already in use
- Integration points the user may not be aware of
- Anything the user said that conflicts with the current codebase

Do NOT share findings with the user yet. Accumulate them to inform the interview.

---

## Phase 2 — Web research

Search for industry best practices, common pitfalls, and recommended approaches for the type of feature the user described. Use **WebSearch** and **WebFetch** to gather real, current knowledge.

Good search angles (use whichever apply):
- "{feature type} best practices {year}"
- "{technology} {pattern} tradeoffs"
- "when NOT to use {approach}"
- Security or compliance implications if relevant
- Known UX anti-patterns for this type of feature

**Synthesize findings into a private knowledge base** (just keep it in context — don't write it to a file). You'll use this to:
1. Ask smarter questions in the interview
2. Flag choices the user might not realize are unusual or risky
3. Suggest alternatives the user may not have considered

Do NOT share research with the user as a wall of text. Surface it selectively, embedded in questions.

---

## Phase 3 — Deep interactive interview

**This is the core of the skill.** The interview is non-negotiable — it always happens, even if the request seems crystal clear. Default posture: assume there are decisions the user hasn't thought through yet.

Structure the interview in **up to 3 rounds** of **AskUserQuestion** calls. Each round may have 1–4 questions. Do not ask everything at once.

### Round 1 — Scope and intent

Ask questions that clarify WHAT and WHY. Derive these from what the user said, what you found in the codebase, and what the research surfaced. Examples (adapt to the actual request):

- What problem does this solve for the end user — and who exactly is the end user?
- What does "done" look like? What can a user do that they can't do today?
- Is there a deadline, performance target, or constraint driving this?
- Are there existing features in the codebase that partially do this? (Reference what you found.)

**Challenge incoherence explicitly.** If something the user described doesn't fit the existing architecture, the current user roles, or what makes sense given the stack, say so and ask them to confirm:

> "You mentioned X, but in the current codebase Y already handles that — are you looking to extend Y, replace it, or build something parallel? I want to make sure I don't design around the wrong assumption."

Use **AskUserQuestion** with options when there are a finite set of sensible answers. Use open-ended questions when the answer is truly open.

### Round 2 — Key design decisions (user-driven)

Based on Round 1 answers and your research, surface the 2–4 most consequential design choices for this feature. For each, present:
- The decision to be made
- The realistic options (2–3 max)
- The tradeoff in plain language, enriched by what you found in research
- Your recommendation, if the evidence clearly favors one option

**The user decides — do not pick for them unless the choice is completely obvious and inconsequential.** Frame every question so the user understands the implications of each option.

Examples of good decision questions:
- "Should this be synchronous (simple, immediate) or async with a job queue (complex, but won't block the UI for slow operations)?"
- "Should operators see each other's data within a tenant, or is per-user isolation needed?"
- "This pattern is used everywhere else in the codebase — do you want to stay consistent or diverge? (diverging means more maintenance surface)"

### Round 3 — Edge cases and constraints (conditional)

Only run this round if Round 1 or Round 2 revealed genuinely open questions about:
- Error states and what the user expects to happen
- Access control (which roles should see/do what)
- Data retention, migration, or backward compatibility
- Interaction with existing features that touch the same data

Skip Round 3 if nothing critical is unresolved after Rounds 1 and 2.

---

## Phase 4 — Pre-proposal summary (mandatory)

Before creating any file, present the user with a compact summary of what you're about to build. Use a clear structure:

```
## What I understood

**Feature**: [one sentence]
**Why**: [one sentence]
**Scope**: [what's in, what's explicitly out]

## Key decisions captured

- [decision 1]: [choice the user made]
- [decision 2]: [choice the user made]
- ...

## Assumptions I'm making (not confirmed)

- [assumption] — tell me if this is wrong

## Anything I'm flagging

- [concern or risk surfaced by research or codebase review]
```

Then ask one final **AskUserQuestion**:

> "Does this look right before I write the proposal? Or is there anything you'd change?"

Options: "Looks good, proceed" / "I need to adjust something" (if they pick adjust, let them describe it inline then re-show the summary).

Do NOT proceed to artifact creation until the user confirms.

---

## Phase 5 — Create the change and artifacts

Once confirmed, follow the same pipeline as `openspec-propose`:

1. **Create the change directory**
   ```bash
   openspec new change "<name>"
   ```

2. **Get artifact build order**
   ```bash
   openspec status --change "<name>" --json
   ```

3. **Create artifacts in dependency order** until all `applyRequires` artifacts are done:
   - Get instructions: `openspec instructions <artifact-id> --change "<name>" --json`
   - Read dependency artifacts for context
   - Write the artifact — use `template` as structure, apply `context` and `rules` as constraints (do NOT copy them into the file)
   - Show brief progress: "Created <artifact-id>"
   - Re-check status after each artifact

   All decisions captured in the interview MUST be reflected in the artifacts. The proposal.md should answer WHY with the user's stated intent. The design.md should encode the design choices from Round 2. The tasks.md should include tasks for edge cases surfaced in Round 3.

4. **Show final status**
   ```bash
   openspec status --change "<name>"
   ```

---

## Output

After all artifacts are created, summarize:
- Change name and location
- Brief list of artifacts created
- One sentence on anything notable from the research or interview that shaped the design
- "All artifacts created! Ready for implementation."
- Prompt: "Run `/opsx:apply` or ask me to implement to start working on the tasks."

---

## Guardrails

- **The interview always happens** — never skip it, even if the request seems obvious. Obvious requests hide the most assumptions.
- **The user decides all non-trivial choices** — your job is to surface options and tradeoffs, not to silently pick.
- **Challenge incoherence, then accept confirmation** — if the user confirms something you think is wrong, document it as a known decision and move on. Don't block forever.
- **Research informs questions, not monologues** — don't dump research findings at the user; embed them in questions and options.
- **AskUserQuestion for every key choice** — no silent defaults on decisions that affect architecture, UX, or security.
- **Keep interview rounds focused** — 2–4 questions per round max. Quality over quantity.
- **Never create artifacts before Phase 4 confirmation** — even if you already know what to write.
- If a change with that name already exists, ask if the user wants to continue it or start fresh.
- Verify each artifact file exists after writing before proceeding to the next one.
