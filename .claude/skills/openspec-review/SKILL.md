---
name: openspec-review
description: Adversarial review of an OpenSpec change — artifacts and source code. Auto-detects pre-apply mode (all tasks pending, focuses on design quality) vs pre-archive mode (tasks started, also checks implementation fidelity). Reports findings by severity and offers optional direct edits. Use before starting implementation or before archiving.
license: MIT
compatibility: Requires openspec CLI.
argument-hint: "<change-name>"
metadata:
  author: custom
  version: "1.0"
allowed-tools: Read Bash(openspec *) Bash(grep *) Bash(awk *) Bash(find *) Bash(test *) Edit AskUserQuestion
---

Adversarial review of an OpenSpec change: artifacts and source code. Reports findings categorized by severity and offers optional edits.

**Input**: Optionally specify a change name after the invocation. If omitted, check if it can be inferred from conversation context. If vague or ambiguous, run `openspec list --json` and use **AskUserQuestion** to let the user select.

---

## Step 1 — Select change and validate

If a name is provided, use it. Otherwise infer from context or prompt.

Announce: "Reviewing change: **<name>**"

Validate the change exists and has at least `proposal.md` done:

```bash
openspec status --change "<name>" --json
```

- If the command fails or the change is not found: print error, run `openspec list` to show available changes, and stop.
- If `proposal` artifact is not `done`: inform the user that review requires at least `proposal.md` to be complete, and stop.

---

## Step 2 — Detect review mode

Read the tasks file path from `openspec status --json` output (look for the artifact with id `tasks` and its `outputPath`). The file lives at `openspec/changes/<name>/tasks.md`.

```bash
# count pending and complete tasks
pending=$(grep -c '^\- \[ \]' openspec/changes/<name>/tasks.md 2>/dev/null || echo 0)
complete=$(grep -c '^\- \[x\]' openspec/changes/<name>/tasks.md 2>/dev/null || echo 0)
```

Rules:
- `tasks.md` does not exist → **pre-apply**
- `complete == 0` → **pre-apply** (no implementation started)
- `complete > 0` → **pre-archive** (implementation underway or done)

Announce the detected mode clearly before proceeding:

```
Mode: PRE-APPLY — reviewing design quality (proposal, design, specs, tasks)
```
or
```
Mode: PRE-ARCHIVE — reviewing design quality + implementation fidelity
Tasks: N complete / M total
```

---

## Step 3 — Read context artifacts

Read all artifact files that are `done` according to `openspec status --json`:

- `openspec/changes/<name>/proposal.md`
- `openspec/changes/<name>/design.md` (if done)
- All files under `openspec/changes/<name>/specs/` (if done)
- `openspec/changes/<name>/tasks.md` (if done)

Keep all content in context for the lenses below.

---

## Step 4 — Lens reviews (accumulate findings, do not report yet)

Apply each lens in order. For each finding, record:
- **Sev**: Bloqueante / Recomendado / Opcional
- **Lens**: which artifact
- **Quote**: literal fragment from the artifact (mandatory — no quote = skip the finding)
- **Suggestion**: concrete actionable fix

### Lens A — proposal.md

Check each item; flag only what is actually violated (cite the offending fragment):

- **WHY is concrete**: the Why section names a real problem, not a generic motivation. Flag if it could describe any change without modification.
- **What Changes is specific**: bullet list names concrete capabilities or files, not vague intentions.
- **Capabilities in kebab-case**: every capability under New/Modified uses `kebab-case-name`. Flag any PascalCase, snake_case, or plain English names.
- **Scope creep**: every capability in the Capabilities section traces back to the WHY. Flag capabilities that solve problems not mentioned in Why.
- **Broken capability contract**: every capability listed under New Capabilities will need a corresponding `specs/<name>/spec.md`. Flag any that seem to be implementation details (functions, classes) rather than behavior units.

### Lens B — design.md

- **Decision without alternatives**: each decision under `## Decisions` should state at least one alternative considered. Flag any that say only "we chose X" with no "instead of Y".
- **Risk without mitigation**: each item under `## Risks / Trade-offs` should have a mitigation or acceptance rationale. Flag bare risks with no follow-up.
- **Open questions**: if `## Open Questions` section exists and has unanswered items, flag as Bloqueante (open questions should be resolved before implementation).
- **Circular rationale**: decisions that justify themselves ("we chose X because X is good") without comparing to alternatives.

### Lens C — specs/ (delta specs)

For each spec file under `openspec/changes/<name>/specs/`:

- **Every requirement has ≥1 scenario**: a `### Requirement:` block with no `#### Scenario:` below it is untestable — flag as Bloqueante.
- **Scenario format**: each scenario must have both `**WHEN**` and `**THEN**` lines. Missing either is Bloqueante.
- **Scenario headers use #### (4 hashtags)**: using `###` for scenarios silently breaks parsing. Check the raw markdown.
- **Delta operations are valid**: only `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements` are valid top-level section names. Flag anything else.
- **MODIFIED includes full content**: a `## MODIFIED Requirements` entry that only shows what changed (not the full updated requirement block) loses data at archive time. Flag as Bloqueante.
- **REMOVED has Reason and Migration**: a removed requirement without `**Reason**` and `**Migration**` leaves implementers without context.
- **SHALL/MUST for normative requirements**: requirements using "should" or "may" for normative behavior are ambiguous. Flag as Recomendado.

### Lens D — tasks.md

- **Non-atomic tasks**: a task that contains "and" connecting two distinct deliverables (e.g., "Create X and configure Y") is not atomic. Flag as Recomendado — suggest splitting.
- **Task with no verifiable done criterion**: tasks like "Review the code" or "Check the design" have no objective done state. Flag as Recomendado.
- **Dependency order violation**: if task N.M references an artifact or module that is created in a later task N.P (P > M), the order is inverted. Flag as Bloqueante.
- **Assumption of non-existent code**: tasks that say "add method to `X`" where `X` does not yet exist in the codebase. In pre-apply mode, verify by checking if the file is created by an earlier task. In pre-archive mode, verify with `test -f`.
- **Tasks outside the proposal scope**: tasks that implement features not mentioned in proposal.md. Flag as Recomendado (scope expansion without proposal update).

### Lens E — source code (pre-archive mode only)

**Extract file paths from tasks.md:**

```bash
# extract backtick-quoted paths and bare path patterns from tasks.md
grep -oE '`[^`]+\.[a-zA-Z]{1,5}`' openspec/changes/<name>/tasks.md | tr -d '`' | sort -u
grep -oE '[a-zA-Z0-9_/.-]+\.[a-zA-Z]{1,5}' openspec/changes/<name>/tasks.md | grep '/' | sort -u
```

For each candidate path: run `test -f <path>` from the project root. Read only files that exist. Inform the user which paths could not be located.

For each file read, verify against the specs in context:

- **Missing required behavior**: a scenario in specs says THEN the system does X, but the implementation has no code path for X. Flag as Bloqueante.
- **Behavior outside spec**: the code implements logic that has no corresponding requirement in any spec. Flag as Recomendado (may be incidental complexity or unauthorized scope).
- **Error paths not implemented**: a spec scenario covers failure/error cases but the code has no error handling for it. Flag as Bloqueante.
- **Naming divergence**: spec names a capability or concept consistently but the code uses different terminology with no mapping. Flag as Opcional.

---

## Step 5 — Adversarial transversal pass

After all lenses, do one additional sweep looking for issues that span artifacts — these are the hardest to catch in single-artifact review:

- **Implicit assumptions**: something is treated as true in design.md but not stated in proposal.md, or assumed in tasks.md but not in specs (e.g., "the user is authenticated" assumed everywhere but never specced).
- **Missing edge cases**: scenarios only cover the happy path; failure modes (empty input, missing resource, concurrent writes, network error) have no scenario. Flag the most critical missing ones as Bloqueante or Recomendado based on risk.
- **Security surface not addressed**: if the change touches auth, data access, or external input, verify there is at least one security-focused requirement or scenario. Flag absence as Bloqueante.
- **Consistency gaps**: a concept named differently across proposal/design/specs/tasks/code (e.g., "user group" vs "team" vs "org") that is not an intentional alias.

Only report genuine issues found. Do not invent findings to fill this section.

---

## Step 6 — Present findings report

Print the full findings table:

```
## Review Report: <change-name>

| #  | Sev          | Lens         | Hallazgo                              | Sugerencia                         |
|----|--------------|--------------|---------------------------------------|------------------------------------|
|  1 | Bloqueante   | proposal.md  | "fragment cited literally"            | concrete fix                       |
|  2 | Recomendado  | design.md    | "fragment cited literally"            | concrete fix                       |
...

**Bloqueantes: N · Recomendados: N · Opcionales: N**
```

**If zero Bloqueantes and zero Recomendados:**

```
✓ Change sano — no blocking or recommended issues found.
```

If there are only Opcional findings, list them and ask if the user wants to apply any. If none, terminate here without offering edits.

---

## Step 7 — Offer optional edits (if any Bloqueante or Recomendado findings)

Ask the user which findings to apply using **AskUserQuestion** (multiSelect). Present each finding as an option with a short label (e.g., "1 — proposal: scope creep in capability X").

For each selected finding:
- Make the change with **Edit** directly on the artifact file
- Never use **Write** to rewrite the entire file
- After each edit, confirm: "✓ Applied finding #N"

After all selected edits are done, show a summary of what was changed.

---

## Guardrails

- Every finding MUST cite a literal fragment from the artifact — no citation = no finding.
- Do not report cosmetic issues as Bloqueante.
- If a lens finds nothing, say "Lens X: ✓ OK" — do not skip silently.
- Do not modify any artifact before the user selects which findings to apply.
- In pre-apply mode, never attempt to read source code files.
- If `openspec status` shows a change with no done artifacts besides proposal, skip lenses B/C/D and note it.
- Apply edits only with `Edit` (diff-based), never `Write` (full rewrite).
