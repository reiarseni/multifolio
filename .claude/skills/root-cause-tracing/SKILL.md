---
name: root-cause-tracing
description: Traces an error or bug to its true origin by following the causal chain, not just fixing the symptom. Use when a bug keeps coming back or when the surface error is clearly not the real problem.
license: MIT
compatibility: Claude Code
argument-hint: "[error message or bug description]"
metadata:
  author: obra (concept), adapted for this repo
  source: https://github.com/ComposioHQ/awesome-claude-skills
---

Fixing symptoms is waste. This skill finds the cause that, if removed, makes the symptom impossible.

---

## Step 1 — State the observed symptom

Write the symptom in one sentence:
> "When X happens, Y fails with Z."

If you don't have a concrete reproduction, get one first. A vague bug is not a traceable bug.

---

## Step 2 — Build the causal chain

Starting from the symptom, ask "what caused this?" at each level. Work backwards until you reach a root cause — something that is:
- Under our control (not an external service outage or hardware failure)
- Fixable without side effects on other behavior
- The cause that, if changed, makes the symptom impossible to occur

Document the chain:

```
Symptom: <observed error>
  ← caused by: <intermediate cause 1>
    ← caused by: <intermediate cause 2>
      ← ROOT CAUSE: <fundamental cause>
```

Typical root cause categories:
- **Wrong assumption**: the code assumes X is always true, but it isn't
- **Missing validation**: input or state is never checked before use
- **Race condition**: two operations assume exclusive access to shared state
- **Stale reference**: a value is cached or copied and becomes outdated
- **Missing invariant enforcement**: a constraint that should always hold is never enforced

---

## Step 3 — Verify the root cause

Before fixing, verify the root cause is real:

```bash
# instrument the suspected root cause
# add a temporary log or assertion at that point
# reproduce the symptom and confirm the instrumentation fires
```

If the root cause does not fire during reproduction, go back to Step 2 — you haven't found it yet.

---

## Step 4 — Fix at the root

Fix only at the root cause level. Do not also fix the intermediate causes — they will self-resolve once the root is removed.

Write the fix:
- Minimal change at the root
- Add a guard, invariant, or test that makes the root cause impossible to recur

---

## Step 5 — Confirm the fix

- Reproduce the original symptom → confirm it no longer occurs
- Run the test suite → confirm no regressions
- Remove any temporary instrumentation added in Step 3

---

## Step 6 — Report

```
## Root Cause Trace

Symptom: <original error>
Root cause: <what was actually wrong>
Fix: <what was changed and why>
Prevention: <test or invariant added>
```

---

## Guardrails

- If you cannot trace a causal chain beyond 3 levels, stop and ask the user for more context — guessing root causes is worse than not fixing at all
- Never fix multiple levels of the chain simultaneously — it makes the fix untestable
- If the root cause is in a dependency (library, framework, external API), document it as a known constraint and work around it at the boundary — do not patch the dependency inline
