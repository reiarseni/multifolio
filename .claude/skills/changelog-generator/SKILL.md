---
name: changelog-generator
description: Transforms git commits into structured, user-readable release notes. Produces a changelog entry ready to publish — not a raw commit dump.
license: MIT
compatibility: Claude Code
argument-hint: "[version] [from-ref]"
metadata:
  author: ComposioHQ (concept), adapted for this repo
  source: https://github.com/ComposioHQ/awesome-claude-skills
---

Release notes are for humans, not for git. Transform commits into a changelog entry that tells users what changed and why it matters to them.

**Input**: Optionally provide a version number (e.g. `v1.2.0`) and a base ref to compare from (e.g. `v1.1.0` or a commit SHA). If omitted, uses the latest tag as base and asks for the version.

---

## Step 1 — Collect the commits

```bash
# if a base ref was provided:
git log <base-ref>..HEAD --oneline --no-merges

# if no base ref:
git describe --tags --abbrev=0   # get latest tag
git log <latest-tag>..HEAD --oneline --no-merges
```

If there are no commits since the last tag, report that and stop.

---

## Step 2 — Ask for version (if not provided)

Use **AskUserQuestion**:
> "What version is this release?"

Options: suggest the next semver increment based on what the commits contain (patch if only fixes, minor if new features, major if breaking changes).

---

## Step 3 — Classify commits

For each commit, classify into one of these categories:

| Category | Commit prefix or signal |
|---|---|
| **Breaking Changes** | `!` suffix, `BREAKING CHANGE` in body, or major behavior removal |
| **New Features** | `feat:` |
| **Bug Fixes** | `fix:` |
| **Performance** | `perf:` |
| **Developer Experience** | `chore:`, `refactor:`, `build:`, `ci:` |
| **Documentation** | `docs:` |

Skip commits that are purely internal or mechanical (e.g. "fix typo in comment", "update lockfile") — they add noise without value to readers.

---

## Step 4 — Write user-facing descriptions

For each included commit, rewrite the message as a user-facing bullet:
- Start with a verb (Added, Fixed, Improved, Removed)
- Describe the effect on the user, not the implementation detail
- Keep it to one line

Examples:
- `feat: add offline export` → `Added offline export for reports — works without internet connection`
- `fix: handle null user in checkout` → `Fixed a crash that occurred when checking out without a logged-in user`
- `perf: cache product queries` → `Improved product listing load time by caching frequent queries`

---

## Step 5 — Produce the changelog entry

```markdown
## [<version>] — <YYYY-MM-DD>

### Breaking Changes
- <description> — **action required**: <what users must do to adapt>

### New Features
- <description>

### Bug Fixes
- <description>

### Performance
- <description>

### Developer Experience
- <description> _(internal)_
```

Omit sections that are empty. Always include Breaking Changes if any exist, even if it's the only section.

---

## Step 6 — Ask where to write it

Use **AskUserQuestion**:
> "Where should I write this entry?"

Options:
- `CHANGELOG.md` (prepend at top, after any header)
- `RELEASES.md`
- Print only (don't write to file)

If writing to a file and the file doesn't exist, create it with a standard header.

---

## Guardrails

- Never include commit SHAs or branch names in user-facing release notes
- Breaking Changes must always include an "action required" note — if you can't determine what users must do, flag it and ask
- Do not invent features or changes not present in the commits
- If a commit message is too cryptic to translate to user-facing language, skip it rather than guess
