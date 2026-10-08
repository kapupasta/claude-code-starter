---
name: principle_workspace_hygiene
description: "Hub — where scratch, links and drift-prone state go, plus shell/tool-shape traps that produce confident wrong output; links every hygiene lesson"
type: feedback
tags: [gotcha]
---

# Workspace hygiene

This file owns the hygiene principle and every incident filed under it.

**When:** you create a scratch file, write a link or a doc, loop over values in the shell, or feed one tool's output into another.

**Principle:** put things where the next session expects them, in a shape that can't silently rot or mislead. The gates *stay inside the workspace* and *archive, don't delete* (in `MEMORY.md`) are the hard form of this hub.

**Sharpest warning signs** (mirrored in `MEMORY.md`):
- drift-prone state (counts, versions, what's deployed) belongs in a script that checks it, not in prose
- scratch goes in one known place (`scratch_dir` in `starter-config.json`), never the workspace root
- links in docs are clickable (`[name.md](file:///abs/path)`), never bare paths

**Also watch for:**
- zsh does not word-split `$VAR` in a for-loop — the loop runs once over the whole string and prints confident wrong findings; use an array
- scratch that must survive a sandboxed → unsandboxed retry can't live in `$TMPDIR` (it differs between the two)
- an MCP/tool input key renamed from the output field it came from — re-feed the key you were handed
- date headers in prose docs ("as of …") — they rot; let a verify script state the current value

## Cases
<!-- One line per incident: **Short rule** - what happened, with a number [fb](./feedback_topic.md) -->
- **Example — a for-loop over `$LIST` reported one confident wrong finding** - zsh treated the whole list as one item. Use `items=(a b c)` or `${=LIST}`
- *Add your own incidents here.*
