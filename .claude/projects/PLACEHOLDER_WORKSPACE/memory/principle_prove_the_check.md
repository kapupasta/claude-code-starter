---
name: principle_prove_the_check
description: "Hub — before reporting done/fixed/clean/passing/none, the check must be able to fail and must test the real thing; links every verification lesson"
type: feedback
tags: [gotcha]
---

# Prove the check, verify the real thing

This file owns the verification principle and every incident filed under it.

**When:** you are about to say something is done, fixed, deployed, clean, passing, identical or absent — or about to trust a script, test, grep or sweep that says so.

**Principle:** a result is evidence only if the instrument could have reported the opposite, and only about the thing it actually touched. Local ≠ deployed, count ≠ content, sample ≠ population, a green test ≠ a correct test.

**Sharpest warning signs** (mirrored in `MEMORY.md`):
- a pass counts only if you've seen that check fail; a sample proves presence, never absence
- verify by content, not count
- deployed ≠ local: fetch the live artifact, look at the live page, drive the embed

**Also watch for:**
- an edit tool that exits 0 when it changed nothing (`sed -i` with an anchor that never matched) — read the effect back, never the exit code
- a verification chain ending in `|| echo "ok"` — `grep -c` exits 1 on zero, short-circuits the `&&`, and the fallback prints the all-clear
- `command not found` inside a loop falling through to the "clean" branch for every item
- a normalizer hiding exactly the defect class it normalizes away
- a checker with several filters probed only once — each filter is its own blind spot
- a grep-to-verify that can't match text that wraps a line or contains markup
- a stand-in test that doesn't exercise the identical mechanism (same auth path, same code path)
- a spec tested by its own author, who already knows the answers
- a client-side "saved" flag treated as a stored value — reload and read it back
- config called "done" because the file parses; runtime changes need a runtime probe
- layout checked at one viewport only

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — `sed -i` reported success on a no-op** - an indented config line never matched `^port`, the command exited 0, and only a trailing `cat` showed nothing changed. Read edits back or `diff` against a backup
- **Example — a consistency assertion passed because the mechanism never ran** - the checked component was disabled at that viewport. Add a liveness assert and a third verdict, INVALID
- *Add your own incidents here.*
