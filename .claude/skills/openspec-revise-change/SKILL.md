---
name: openspec-revise-change
description: Revise the artifacts of an existing OpenSpec change. Use when requirements changed, new information emerged, or the proposal needs to reflect the current state of the codebase.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: custom
  version: "1.0"
---

Revise the artifacts of an existing OpenSpec change.

**Input**: Optionally specify a change name and a description of what changed or needs updating. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the **AskUserQuestion tool** to let the user select

   Always announce: "Revising change: <name>"

2. **Read all current artifacts**

   Run:
   ```bash
   openspec status --change "<name>" --json
   ```

   Parse the JSON to understand:
   - `schemaName`: The workflow being used
   - `artifacts`: list with `id`, `status`, `outputPath`

   Read every artifact file that has `status: "done"` so you have full context of what was previously specified.

3. **Understand what needs revision**

   Use the user's description as the primary input. Supplement with:
   ```bash
   git diff HEAD --stat
   ```

   Compare what the current artifacts specify against what the user described or the code shows. Identify:
   - Artifacts whose content is now outdated or incorrect
   - New requirements not yet captured in any artifact
   - Tasks already implemented in code but still marked `- [ ]`
   - References to things that were removed, renamed, or never existed

   Present a brief analysis:
   ```
   ## Revision Plan

   Artifacts to revise:
   - <artifact-id> — <reason>

   Artifacts that look current:
   - <artifact-id> — no changes needed
   ```

   Use the **AskUserQuestion tool** to confirm the list before proceeding, unless only one artifact needs revision.

4. **Revise selected artifacts in dependency order**

   For each artifact selected for revision:

   a. Get the instructions template:
      ```bash
      openspec instructions <artifact-id> --change "<name>" --json
      ```
      The JSON includes `template`, `instruction`, `context`, `rules`, `outputPath`, and `dependencies`.

   b. Read the current artifact file and all dependency artifact files.

   c. Rewrite the artifact file using `template` as the structure:
      - Keep content that is still valid
      - Incorporate the new requirements or decisions the user described
      - Remove content that no longer applies
      - Apply `context` and `rules` as constraints — do NOT copy them into the file

   d. Write the updated content to `outputPath`.

   e. Show brief progress: "Updated <artifact-id>"

5. **Handle tasks artifact specially**

   When revising the tasks artifact:
   - Preserve all tasks already marked `- [x]` — do NOT remove or uncheck them
   - Check `git diff HEAD` for work already done and mark those tasks `- [x]`
   - Add new tasks for requirements not yet covered
   - Remove only tasks that are irrelevant AND not yet started (`- [ ]`)
   - Reorder incomplete tasks if priority changed

6. **Show final status**

   ```bash
   openspec status --change "<name>"
   ```

**Output On Completion**

```
## Revision Complete

**Change:** <change-name>
**Schema:** <schema-name>

### Revised
- <artifact-id> — <what changed>
- <artifact-id> — <what changed>

### Not Modified
- <artifact-id>

Ready to continue implementation. Run `/opsx:apply` or `/openspec-quick-advance`.
```

**Guardrails**
- Always read ALL current artifacts before revising any of them — context depends on the full picture
- Never remove or uncheck completed tasks (`- [x]`) — they are implementation history
- Check git diff to detect already-implemented work before adding duplicate tasks
- If the user's description conflicts with what the code shows, flag it and ask before writing
- `context` and `rules` from `openspec instructions` are constraints for you — never copy them into the artifact file
- Keep revisions minimal: only change what actually needs to change
- If no change name is provided and context is ambiguous, always prompt — do not guess
- Verify each artifact file exists at `outputPath` after writing before proceeding to the next
