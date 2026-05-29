---
name: test-fixing
description: Systematically detects broken tests, traces the root cause, and fixes them without breaking others. Use when CI is red or a test regression appears.
license: MIT
compatibility: Claude Code
argument-hint: "[test file or error message]"
metadata:
  author: mhattingpete (concept), adapted for this repo
  source: https://github.com/ComposioHQ/awesome-claude-skills
---

Broken tests are a signal, not just noise. Fix them systematically — no random attempts, no skipping, no `// TODO: fix later`.

---

## Step 1 — Collect the failing tests

Run the test suite and capture all failures:

```bash
# adapt to the project's test runner
npm test 2>&1 | tail -100
# or: pytest -x, cargo test, go test ./..., etc.
```

List every failing test by name. Do not fix anything yet.

---

## Step 2 — Classify the failures

Group failures into categories:

- **Regression**: test was passing before; a recent code change broke it
- **Flaky**: test fails intermittently (timing, random data, external dependency)
- **Stale**: test was written for behavior that was intentionally changed
- **Environment**: test fails due to missing setup, wrong config, or missing dependency

Announce the classification before proceeding. If classification is unclear, default to Regression.

---

## Step 3 — Identify the root cause

For **Regression** failures:
```bash
git log --oneline -10   # find the commit that introduced the break
git diff HEAD~1 -- <relevant file>
```
Read the failing test. Read the code it tests. Find the exact mismatch between expected and actual behavior.

For **Stale** failures:
- Confirm with the user that the behavior change was intentional before modifying the test
- Never silently update a test expectation without confirmation

For **Flaky** failures:
- Add retry or isolation (avoid `sleep`-based fixes)
- If the test depends on external state, mock or seed it

For **Environment** failures:
- Fix the setup, not the test
- Document what was missing in a comment or README addition

---

## Step 4 — Fix one test at a time

Fix in order of classification: Regression first, then Stale (with confirmation), then Environment, then Flaky.

For each fix:
1. Make the minimal change needed — do not refactor surrounding code
2. Run only that test to confirm it passes
3. Run the full suite to confirm no new failures were introduced
4. If a new failure appears, undo the fix and re-classify

---

## Step 5 — Report

After all tests pass:

```
## Test Fixing Complete

Fixed: N tests
- <test name> — <one-line cause and fix>
- ...

Skipped (needs user decision):
- <test name> — <reason>
```

---

## Guardrails

- Never skip or comment out a test to make CI green — that is not a fix
- Never change a test's expected value without understanding why it changed
- If a Stale test update requires confirming intentional behavior change, always ask the user first
- Stop and report if fixing one test consistently breaks another — that signals a deeper design issue
