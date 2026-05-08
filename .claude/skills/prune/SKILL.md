---
name: prune
description: "Reduce size and remove duplication from CLAUDE.md or MEMORY.md without restructuring. Use when files are getting too large, content is duplicated, or sections are outdated."
---

# Prune

Reduce the size of `CLAUDE.md` or `MEMORY.md` (or both) by removing outdated, duplicated, or redundant content. This skill does NOT restructure, rename sections, or rewrite content — it only removes.

## The Core Rule

**Prune = reduce size and remove duplication. Never restructure. Never rewrite.**

If a section needs to be restructured rather than trimmed, that is a separate task. Surface it to the user and stop.

## When to use

- CLAUDE.md is approaching or exceeding ~40k characters
- MEMORY.md is getting unwieldy or hard to scan (over ~200 lines)
- Content is duplicated between CLAUDE.md and MEMORY.md
- Sections reference old projects, old decisions, or old tools that no longer apply

## Inputs required

- **Target file(s)**: CLAUDE.md, MEMORY.md, or both
- **Size target** (optional): e.g. "get it under 400 lines" — if not provided, aim for ~20% reduction

## Procedure

### Step 1: Audit current state

- Line count
- Identify content that duplicates between CLAUDE.md and MEMORY.md
- Identify outdated references (resolved issues, completed projects, deprecated tools)
- Identify generic best-practice advice that isn't specific to this workspace
- Identify MEMORY.md index entries that point to non-existent files

### Step 2: Present the removal plan

List exactly what will be removed, with a one-line reason per item:

```
PROPOSED REMOVALS from CLAUDE.md:
- Lines 45-52 (verbose explanation of X) — covered more concisely in MEMORY.md
- Lines 201-210 (deleted projects list) — stale, not useful for agents
- [etc.]
Estimated reduction: ~80 lines (~15%)
```

Do NOT edit yet. Wait for user approval.

### Step 3: Execute approved removals

Make only the approved edits. Preserve all section headings, structure, and content not on the approved list.

### Step 4: Report

Show before/after line count:
```
CLAUDE.md: 420 lines → 338 lines (-82 lines, -20%)
```

## Guardrails

- Never delete a section heading without removing all content under it too (orphan headings are worse than verbose content)
- Never remove active project entries from MEMORY.md unless user confirms the project is dead
- If in doubt about whether something is still relevant, ask rather than removing it
- After pruning, do a final read of the affected sections to confirm they still make sense in context
