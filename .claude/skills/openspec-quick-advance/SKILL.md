---
name: openspec-quick-advance
description: Fast-track a change to completion — implement all remaining tasks, review the implementation, then archive. Use when the change is well-defined and you want to finish it in one shot.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: custom
  version: "1.0"
---

Fast-track a change to completion: implement remaining tasks, review the implementation, then archive.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change and check readiness**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Run:
   ```bash
   openspec status --change "<name>" --json
   ```

   Parse the JSON to understand:
   - `schemaName`: The workflow being used
   - `applyRequires`: artifact IDs needed before implementation
   - Which artifact contains the tasks and its `outputPath`

   **If any `applyRequires` artifacts are missing (not `done`):**
   - List the missing artifacts
   - Use **AskUserQuestion tool**: "Some required artifacts are missing. Run `/opsx:propose` first, or proceed anyway?"
   - If user wants to proceed: continue with a note in the final summary
   - If not: stop and suggest `/opsx:propose`

   Announce the plan:
   ```
   Quick Advance: <change-name> (schema: <schema-name>)
   Steps: implement → review → archive
   ```

2. **Get apply instructions and read context files**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message and stop, suggest `/opsx:propose`
   - If `state: "all_done"`: skip to step 4 (review)
   - Otherwise: proceed to implementation

   Read every file path listed under `contextFiles`.

3. **Implement all remaining tasks**

   For each pending task:
   - Show which task is being worked on: "Working on task N/M: <description>"
   - Make the code changes required
   - Keep changes minimal and focused
   - Mark task complete in the tasks file: `- [ ]` → `- [x]`
   - Continue to next task

   **Pause if:**
   - Task is unclear → use **AskUserQuestion tool** to clarify, then continue
   - Implementation reveals a design issue → flag it, ask whether to update artifacts or proceed
   - Error or blocker encountered → report and wait for guidance

   After all tasks are complete, show: "All tasks implemented. Moving to review."

4. **Review the implementation**

   Get a full diff of the changes made during this session:
   ```bash
   git diff HEAD
   ```

   Review the diff against the change artifacts (already in context). Check for:
   - **Completeness**: every task reflected in code, nothing skipped
   - **Correctness**: implementation matches what the proposal and design specified
   - **Regressions**: changes that touch existing behavior unexpectedly
   - **Security**: obvious vulnerabilities introduced (injection, broken auth, exposed secrets)
   - **Quality**: naming and structure consistent with the surrounding codebase

   **If blocking issues found:**
   - List them clearly
   - Use **AskUserQuestion tool**: "Found N blocking issue(s). Fix now (recommended), skip and archive anyway, or stop here?"
   - **Fix now**: make the fixes, then proceed to archive
   - **Skip**: proceed to archive, note issues in summary
   - **Stop**: show summary and exit — the change remains active for the user to fix manually

5. **Assess delta spec sync state**

   Check for delta specs at `openspec/changes/<name>/specs/`. If none exist, proceed without sync prompt.

   **If delta specs exist:**
   - Compare each delta spec with its corresponding main spec at `openspec/specs/<capability>/spec.md`
   - Determine what changes would be applied (adds, modifications, removals, renames)
   - Show a combined summary before prompting

   **Prompt options:**
   - If changes needed: "Sync now (recommended)", "Archive without syncing"
   - If already synced: "Archive now", "Sync anyway", "Cancel"

   If user chooses sync, use Task tool (subagent_type: "general-purpose", prompt: "Use Skill tool to invoke openspec-sync-specs for change '<name>'. Delta spec analysis: <include the analyzed delta spec summary>"). Proceed to archive regardless of choice.

6. **Archive the change**

   Create the archive directory if it doesn't exist:
   ```bash
   mkdir -p openspec/changes/archive
   ```

   Generate target name using current date: `YYYY-MM-DD-<change-name>`

   **Check if target already exists:**
   - If yes: Fail with error, suggest renaming existing archive or using different date
   - If no: Move the change directory to archive

   ```bash
   mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>
   ```

**Output On Completion**

```
## Quick Advance Complete

**Change:** <change-name>
**Schema:** <schema-name>

### Summary
- Implemented: N/N tasks ✓
- Review: passed (or "N warnings, M fixes applied") ✓
- Specs: ✓ Synced (or "No delta specs" or "Sync skipped")
- Archived to: openspec/changes/archive/YYYY-MM-DD-<name>/ ✓
```

**Output On Stop (Blocking Issue)**

```
## Quick Advance Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** N/M tasks complete

### Blocking Issue
<description>

The change is still active. Fix the issue and re-run `/openspec-quick-advance` or use `/opsx:apply` to continue.
```

**Guardrails**
- Always read context files from `openspec instructions apply` before implementing — don't assume file names
- Update task checkboxes immediately after completing each task
- Review must happen between implement and archive — never skip it
- If review finds blocking issues and user stops, leave the change active — do not archive a broken state
- If the change has 0 pending tasks at start, skip step 3 and go directly to review
- Never remove or uncheck completed tasks (`- [x]`) during the process
- Preserve `.openspec.yaml` when moving to archive (it moves with the directory)
- Use contextFiles from CLI output, don't assume specific artifact file names
