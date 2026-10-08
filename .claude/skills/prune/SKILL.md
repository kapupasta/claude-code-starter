---
name: prune
description: "Reduce size and remove duplication from CLAUDE.md or MEMORY.md without restructuring. Use when files are getting too large, content is duplicated, or sections are outdated. Do NOT use for restructuring, renaming headings, rewriting content, or deleting memories (archive, don't delete) — and not as a session-wrap flow (that is pre-clear)."
---

# Prune

This file owns the reduce-only edit flow for `CLAUDE.md` and `MEMORY.md`. It removes outdated, duplicated or redundant content. It does NOT restructure, rename sections or rewrite content.

## The Core Rule

**Prune = reduce size and remove duplication. Never restructure. Never rewrite.**

If a section needs to be restructured rather than trimmed, that is a separate task. Surface it to the user and stop.

## When to use

- CLAUDE.md is approaching or exceeding ~40k characters
- MEMORY.md is near its load cap (Claude Code auto-loads only the first 200 lines OR 25KB, whichever comes first) — `scripts/meta-health.sh` check [1] warns before you hit it
- Content is duplicated between CLAUDE.md and MEMORY.md
- Sections reference old projects, old decisions or old tools that no longer apply

## Inputs required

- **Target file(s)**: CLAUDE.md, MEMORY.md, or both
- **Size target** (optional): e.g. "get it under 400 lines" — if not provided, aim for ~20% reduction

## Procedure

### For CLAUDE.md

**Step 1: Get a quality report (optional).** If you have a CLAUDE.md quality/review skill or plugin installed, run it first and use its conciseness findings as the basis for what to cut. Otherwise go straight to Step 2.

**Step 2: Identify candidates for removal**
- Sections flagged as verbose or low-value
- Content that duplicates what's already in MEMORY.md or a memory topic file
- Outdated references (old projects, resolved issues, stale decisions)
- Generic best-practice advice that isn't specific to this workspace
- Anything `grep` can answer in two seconds (file lists, what exists) — docs capture *why*, not *what*

**Step 3: Present the removal plan**

List exactly what will be removed, with a one-line reason per item:

```
PROPOSED REMOVALS from CLAUDE.md:
- Lines 45-52 (verbose explanation of X) — covered more concisely in MEMORY.md
- Lines 201-210 (deleted projects list) — stale, not useful for agents
- [etc.]
Estimated reduction: ~80 lines (~15%)
```

Do NOT edit yet. Wait for user approval.

**Step 4: Execute approved removals.** Make only the approved edits. Preserve all section headings, structure, and content not on the approved list.

**Step 5: Report** before/after line count:
```
CLAUDE.md: 420 lines → 338 lines (-82 lines, -20%)
```

---

### For MEMORY.md

**Step 1: Audit current state**
- Line count and byte size
- Index entries that point to non-existent files (`scripts/meta-health.sh` check [2] lists them)
- Entries over the one-line ≤200-char stub rule (check [6]) — the usual cause of bloat. The fix is a **compaction pass**: move the why/war-story into the linked topic file and keep rule + pointer
- Lessons that belong in a principle hub's `## Cases` or a gotcha bucket rather than the index (see `CONVENTIONS.md` routing)
- Content that duplicates CLAUDE.md

**Step 2: Present the removal plan.** Same format as above — what will be removed or moved, one-line reason each. Wait for approval.

**Step 3: Execute approved removals.** Edit only what was approved. A topic file that is no longer useful moves to `memory/archive/`; it is never deleted.

**Step 4: Report** before/after line count and byte size.

---

## Guardrails

- Never delete a section heading without removing all content under it too (orphan headings are worse than verbose content)
- Never reword or remove a **Gate** line without the user's explicit yes — gates are the user's own lines
- Never remove a project from the roster unless the user confirms it is dead
- Never raise a size threshold to make a warning go away — compact instead
- If in doubt about whether something is still relevant, ask rather than removing it
- After pruning, do a final read of the affected sections to confirm they still make sense in context
