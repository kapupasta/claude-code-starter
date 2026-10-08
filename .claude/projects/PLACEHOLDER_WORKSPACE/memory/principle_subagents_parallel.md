---
name: principle_subagents_parallel
description: "Hub — when dispatching subagents or sharing a working tree with other sessions, bound what each agent may touch and verify what it did; links every dispatch/collision lesson"
type: feedback
tags: [claude-code, git-gh]
---

# Subagents & parallel work

This file owns the dispatch-and-collision principle and every incident filed under it.

**When:** you dispatch a subagent, run agents side by side, or work in a tree that other sessions (or humans) also write.

**Principle:** an agent does what its prompt allows, not what you meant; two writers in one tree collide silently. Bound each agent's files and waits, and verify its output yourself. The gate *`git fetch` every repo* (in `MEMORY.md`) covers the human-writer half.

**Sharpest warning signs** (mirrored in `MEMORY.md`):
- bound each agent's files and waits; verify its output yourself, not its report
- parallel writers in one tree collide silently — stage exact paths and check the commit's file count

**Also watch for:**
- subagents slipping conditionals into a "clean" refactor — check the result visually or by diff
- a backgrounded or long-waiting subagent: deploy/CI waits are the controller's job, and an agent's report dies with its context unless it writes as it goes
- fanning out over a selection set you haven't measured — a bad set costs ×N before any agent reports
- renumbering a findings list into a dispatch silently drops items — count them in
- when a review finds a defect, grep the remaining briefs for the same shape before the next dispatch
- verify an agent's isolation (which files and tools it touched) from the transcript, not from its own report
- `git checkout` in a shared tree to "peek" at a branch — use `git show <ref>:<path>` or a worktree

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — a verified staging set committed larger** - 12 paths checked clean in one turn, committed as 18 the next, carrying a parallel session's edits. Stage, assert and commit in one call
- *Add your own incidents here.*
